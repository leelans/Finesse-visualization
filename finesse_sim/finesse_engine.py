"""
Finesse execution engine — responsible for model construction, simulation execution, and result extraction.

Design principles:
1. Fully decoupled from Flask, independently testable
2. Explicit input/output data structures
3. Every exception carries context information
"""
import logging
from typing import Dict, List, Any, Optional, Tuple
import re
from io import StringIO
import numpy as np

from component_registry import registry, _format_param

logger = logging.getLogger('optics-sim')

# B3: Set non-interactive matplotlib backend once at import time (not per-run)
import matplotlib
matplotlib.use('Agg')


def _resolve_braces(text: str, vars_list: list) -> str:
    """Replace {expr} placeholders with numerically evaluated values.

    Finesse's KatScript parser does not understand Python f-string syntax {var}.
    This function evaluates each {expr} using the variable definitions from vars_list
    and substitutes the numeric result.

    Example: "alpha={-mc2_angle}" with vars [{"name":"mc2_angle","value":"1.4"}]
             → "alpha=-1.4"
    """
    if not vars_list or '{' not in text:
        return text

    # Build a numeric namespace from vars_list
    ns = {}
    for v in vars_list:
        try:
            ns[v['name']] = float(v['value'])
        except (ValueError, TypeError):
            ns[v['name']] = v['value']

    def _replacer(match):
        expr = match.group(1)
        try:
            result = eval(expr, {"__builtins__": {}}, ns)
            # Format: avoid scientific notation for values in [1e-4, 1e6]
            if isinstance(result, (int, float)):
                if result == 0:
                    return '0'
                if 1e-4 <= abs(result) < 1e6:
                    s = f"{result:.10f}".rstrip('0').rstrip('.')
                    return s
                return f"{result:.6e}"
            return str(result)
        except Exception:
            logger.warning("Cannot evaluate {%%s} — passing through", expr)
            return match.group(0)

    return re.sub(r'\{([^}]+)\}', _replacer, text)


class FinesseError(Exception):
    """Finesse engine error"""
    pass


class ModelBuildError(FinesseError):
    """Model build failure"""
    pass


class SimulationError(FinesseError):
    """Simulation execution failure"""
    pass


class FinesseEngine:
    """Encapsulates finesse3 model construction and simulation"""

    def __init__(self):
        self._finesse = None
        self._actions = None
        self._ensure_finesse()

    def _ensure_finesse(self):
        """Lazy-load finesse; detects installation status at startup"""
        try:
            import finesse
            from finesse.analysis import actions
            self._finesse = finesse
            self._actions = actions
            logger.info("finesse %s loaded successfully", finesse.__version__)
        except ImportError as e:
            raise FinesseError(
                "finesse3 is not installed. "
                "Run: conda activate finesse && pip install finesse"
            ) from e

    # ---------- Model Construction ----------

    def build_model(
        self,
        components: List[dict],
        connections: List[dict],
        vars_list: List[dict] = None,
        boxes: List[dict] = None,
        preamble: List[str] = None,
    ) -> Tuple[Any, str, dict, dict]:
        """
        Build a finesse Model from components and connections.

        Args:
            components: [{"type": "laser", "id": "c0", "params": {"P": 1.0}}, ...]
            connections: [{"from": "c0", "fromPort": "p1", "to": "c1", "toPort": "p1"}, ...]
            vars_list: [{"name": "len", "value": 1.5}, ...] — global variables for KatScript
            boxes: [{"id", "name", "x", "y", "w", "h"}, ...] — annotation boxes

        Returns:
            (model, katscript, demod_map, space_rename) tuple
            space_rename: dict mapping original space_id -> renamed space_id (conflicts with vars)

        Raises:
            ModelBuildError: if any component or connection cannot be resolved
        """
        model = self._finesse.Model()
        _demod_map = {}  # B1: per-build demod map (no cross-build pollution, no frozen-obj issues)
        lines = []
        tem_lines = []
        sgen_lines = []
        xaxis_lines = []
        deferred_preamble = []  # astigd/attr/lock/modes etc. parsed after components
        if preamble:
            logger.info("Preamble lines: %s", preamble)
            for pl in preamble:
                stripped = pl.strip()
                if stripped.startswith('tem'):
                    tem_lines.append(pl)
                elif stripped.startswith('sgen') or stripped.startswith('fsig'):
                    sgen_lines.append(pl)  # defer after components
                elif stripped.startswith('xaxis') or stripped.startswith('x2axis') or stripped.startswith('noxaxis'):
                    xaxis_lines.append(pl)  # defer to end (analysis)
                elif stripped.startswith('astigd') or stripped.startswith('attr') or stripped.startswith('lock') or stripped.startswith('modes') or stripped.startswith('sweep') or stripped.startswith('signal') or stripped.startswith('splitters'):
                    deferred_preamble.append(pl)  # parsed after components are built
                else:
                    lines.append(pl)
                    try:
                        model.parse(pl)
                    except Exception as e:
                        raise ModelBuildError(f"Failed to parse preamble line '{pl}': {e}") from e

        # Phase 0: Declare global variables
        # Collect variable names for conflict detection (spaces, not vars, will be renamed)
        var_names = set()
        if vars_list:
            for v in vars_list:
                vname = v['name']
                var_names.add(vname)
                var_line = f"var {vname} {v['value']}"
                lines.append(var_line)
                try:
                    model.parse(var_line)
                    logger.info("Declared var: %s", vname)
                except Exception as e:
                    raise ModelBuildError(f"Failed to declare variable '{v['name']}': {e}") from e

        # Phase 1: Separate normal components, detectors, Gauss, and cavities
        detector_types = {"photodetector", "ccd", "pd", "ad"}
        gauss_types = {"gauss"}
        cavity_types = {"cavity"}

        normal_comps = [c for c in components if c.get("type") not in detector_types and c.get("type") not in gauss_types and c.get("type") not in cavity_types]
        detector_comps = [c for c in components if c.get("type") in detector_types]
        gauss_comps = [c for c in components if c.get("type") in gauss_types]
        cavity_comps = [c for c in components if c.get("type") in cavity_types]

        # Create normal components
        def _box_for(comp):
            """Return (box_name, box_id) if comp center is inside any box, else (None, None)."""
            if not boxes:
                return None, None
            cx = comp.get('x', 0) + comp.get('w', 40) / 2
            cy = comp.get('y', 0) + comp.get('h', 40) / 2
            for b in boxes:
                if b['x'] <= cx <= b['x'] + b['w'] and b['y'] <= cy <= b['y'] + b['h']:
                    return b['name'], b.get('id', '')
            return None, None

        # Pre-scan: assign each component to a box
        comp_boxes = []
        for comp in normal_comps:
            name, bid = _box_for(comp)
            comp_boxes.append((comp, name, bid))

        # Track per-box: need to close with ### after last component
        box_open = {}  # box_id -> True when we've opened it
        for i, (comp, box_name, box_id) in enumerate(comp_boxes):
            type_id = comp.get("type", "")
            comp_id = comp.get("id", "")
            params = comp.get("params", {})

            if not type_id or not comp_id:
                raise ModelBuildError(f"Invalid component: type={type_id}, id={comp_id}")

            kat_def = registry.get(type_id)
            if kat_def is None:
                raise ModelBuildError(f"Unknown component type: {type_id}")

            # Check if this is the first component in its box group
            prev_name = comp_boxes[i-1][1] if i > 0 else None
            is_first = box_name and box_name != prev_name

            # Check if next component is in a different box (or no box)
            next_name = comp_boxes[i+1][1] if i+1 < len(comp_boxes) else None
            is_last = box_name and box_name != next_name

            try:
                if is_first:
                    lines.append(f"# {box_name}")
                line = registry.build_kat_line(comp_id, type_id, params,
                    used_params=set(comp.get('usedParams', [])))
                lines.append(line)
                resolved_line = _resolve_braces(line, vars_list or [])
                logger.debug("Parsing: %s", resolved_line)
                model.parse(resolved_line)
                if is_last:
                    lines.append("###")
                if type_id in ('mirror', 'beamsplitter'):
                    elem = getattr(model, comp_id, None)
                    if elem is not None:
                        val = comp.get('imaginary_transmission', None)
                        if val is not None:
                            if isinstance(val, str):
                                val = val.lower() in ('true', '1', 'yes')
                            try:
                                elem.imaginary_transmission = val
                            except AttributeError:
                                pass
            except Exception as e:
                raise ModelBuildError(
                    f"Failed to build component {type_id}({comp_id}): {e}"
                ) from e

        # Phase 2: Create space connections (only between non-detector components)
        space_rename = {}  # maps original space_id -> renamed space_id (when conflict with var)
        logger.info("Connections: %s", connections)
        for conn in connections:
            from_id = conn.get("from", "")
            to_id = conn.get("to", "")
            from_port = conn.get("fromPort", "p1")
            to_port = conn.get("toPort", "p1")

            # Skip connections involving detectors, Gauss, and cavities
            skip_ids = {d["id"] for d in detector_comps} | {g["id"] for g in gauss_comps} | {c["id"] for c in cavity_comps}
            if from_id in skip_ids or to_id in skip_ids:
                continue

            if not from_id or not to_id:
                raise ModelBuildError(f"Invalid connection: {conn}")

            space_id = conn.get('name') or f"s_{from_id}_{to_id}"
            # If space_id conflicts with a variable name, rename the space (not the var)
            if space_id in var_names:
                new_space_id = space_id + '_space'
                space_rename[space_id] = new_space_id
                lines.append(f"# Space renamed: {space_id} -> {new_space_id}  (conflicts with variable)")
                logger.info("Space %s renamed to %s (conflicts with variable)", space_id, new_space_id)
                space_id = new_space_id
            length = conn.get('lengthExpr') or conn.get('length', 1) or 1
            extra = ''
            params = conn.get('params') or {}
            for pk, pv in params.items():
                extra += f' {pk}={pv}'
            space_line = (
                f"s {space_id} {from_id}.{from_port} {to_id}.{to_port} L={length}{extra}"
            )
            lines.append(space_line)
            try:
                resolved_space_line = _resolve_braces(space_line, vars_list or [])
                model.parse(resolved_space_line)
            except Exception as e:
                raise ModelBuildError(
                    f"Failed to connect {from_id}.{from_port} -> {to_id}.{to_port}: {e}"
                ) from e

        # Emit deferred tem lines now that laser exists
        logger.info("TEM lines deferred: %d lines -> %s", len(tem_lines), tem_lines)
        for tl in tem_lines:
            tl_clean = tl.split('#')[0].strip()  # strip inline comments
            if tl_clean:
                lines.append(tl_clean)
                try:
                    model.parse(tl_clean)
                except Exception as e:
                    raise ModelBuildError(f"Failed to parse tem line '{tl_clean}': {e}") from e

        # Emit deferred sgen/fsig lines (need components to exist)
        for sl in sgen_lines:
            sl_clean = sl.strip()
            if sl_clean:
                lines.append(sl_clean)
                try:
                    model.parse(sl_clean)
                except Exception as e:
                    raise ModelBuildError(f"Failed to parse signal line '{sl_clean}': {e}") from e

        # Phase 3: Create detectors — attach to the upstream port connected to this detector
        det_ids = {d["id"] for d in detector_comps}
        for det in detector_comps:
            det_id = det.get("id", "")
            source_node = None

            # Find the connection that links to this detector
            for conn in connections:
                # Case 1: source → PD (normal)
                if conn.get("to") == det_id:
                    raw_port = conn.get('fromPort', 'p1')
                    # Strip .o/.i suffix from port (backend always adds .o)
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['from']}.{clean_port}"
                    break
                # Case 2: PD → source (reverse connection, auto-corrected)
                if conn.get("from") == det_id:
                    raw_port = conn.get('toPort', 'p1')
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['to']}.{clean_port}"
                    logger.info("Auto-corrected detector: %s reads from %s", det_id, source_node)
                    break

            if source_node is None:
                raise ModelBuildError(
                    f"Detector {det_id} is not connected to any component. "
                    f"Connect it to an optical output port."
                )

            det_type = det.get("type", "photodetector")
            logger.info("Building detector: id=%s type=%s full_data=%s", det_id, det_type, {k:det[k] for k in det.keys()})
            if det_type == "ad":
                params = det.get("params", {})
                extra = ' '.join(f'{k}={_format_param(v)}' for k,v in params.items() if v is not None)
                det_line = f"ad {det_id} {source_node}.o {extra}".strip()
            elif det_type == "ccd":
                params = det.get("params", {})
                extra = ' '.join(f'{k}={_format_param(v)}' for k,v in params.items() if v is not None)
                det_line = f"ccd {det_id} {source_node}.o {extra}".strip()
                logger.info("CCD %s built at %s.o (from connection port=%s)", det_id, source_node, conn.get('fromPort', '?'))
            else:
                params = det.get("params", {})
                # Detect pd1/pd2: if photodetector has 'f' param, it's a demod
                has_f = params.get('f')
                if has_f:
                    kat_cmd = 'pd1'
                else:
                    kat_cmd = det.get('kat') or 'pd'  # handle null/empty kat
                logger.info("kat_cmd=%s det=%s has_f=%s", kat_cmd, det_id, has_f)
                extra = ''
                if has_f:
                    extra = ' ' + str(has_f)
                det_line = f"{kat_cmd} {det_id} {source_node}.o{extra}"
            lines.append(det_line)
            try:
                model.parse(det_line)
                # B1: Store demod flag in per-build local dict (Finesse objects are frozen)
                # Only photodetector type can be demod (pd1/pd2); ad/ccd are never demod
                if det_type not in ('ad', 'ccd'):
                    _demod_map[det_id] = (kat_cmd in ('pd1', 'pd2'))
            except Exception as e:
                raise ModelBuildError(
                    f"Failed to build detector {det_id}: {e}"
                ) from e

        # Phase 3b: Add default detector (if none present)
        if not self._has_detector(model):
            # Auto-add detector at the last component's output port
            pass

        # Phase 4: Create Gauss (beam parameters)
        for gauss in gauss_comps:
            gauss_id = gauss.get("id", "")
            source_node = None
            for conn in connections:
                if conn.get("to") == gauss_id:
                    raw_port = conn.get('fromPort', 'p1')
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['from']}.{clean_port}.o"
                    break
                if conn.get("from") == gauss_id:
                    raw_port = conn.get('toPort', 'p1')
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['to']}.{clean_port}.o"
                    break
            if source_node is None:
                raise ModelBuildError(f"Gauss {gauss_id} is not connected to any component.")
            params = gauss.get("params", {})
            extra = ' '.join(f'{k}={_format_param(v)}' for k, v in params.items() if v is not None)
            gauss_line = f"gauss {gauss_id} {source_node} {extra}".strip()
            lines.append(gauss_line)
            try:
                model.parse(gauss_line)
            except Exception as e:
                raise ModelBuildError(f"Failed to build gauss: {e}") from e

        # Phase 5: Create Cavity
        for cav in cavity_comps:
            cav_id = cav.get("id", "")
            source_node = None
            for conn in connections:
                if conn.get("to") == cav_id:
                    raw_port = conn.get('fromPort', 'p1')
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['from']}.{clean_port}.o"
                    break
                if conn.get("from") == cav_id:
                    raw_port = conn.get('toPort', 'p1')
                    clean_port = raw_port.replace('.o', '').replace('.i', '')
                    source_node = f"{conn['to']}.{clean_port}.o"
                    logger.info("Auto-corrected cavity: %s reads from %s", cav_id, source_node)
                    break
            if source_node is None:
                raise ModelBuildError(f"Cavity {cav_id} is not connected to any component.")
            cav_line = f"cav {cav_id} {source_node}"
            lines.append(cav_line)
            try:
                model.parse(cav_line)
            except Exception as e:
                raise ModelBuildError(f"Failed to build cavity: {e}") from e

        # CCD requires gauss or cavity — user must add them explicitly
        # (no auto-injection)

        # Parse deferred preamble lines (astigd/attr/lock/modes/sweep/signal)
        # These reference components, so must run after components are built
        for pl in deferred_preamble:
            pl_clean = pl.strip()
            if pl_clean:
                lines.append(pl_clean)
                try:
                    model.parse(pl_clean)
                except Exception as e:
                    raise ModelBuildError(f"Failed to parse preamble line '{pl_clean}': {e}") from e

        # Emit deferred xaxis analysis lines (must be very last)
        for xl in xaxis_lines:
            xl_clean = xl.strip()
            if xl_clean:
                lines.append(xl_clean)
                try:
                    model.parse(xl_clean)
                except Exception as e:
                    raise ModelBuildError(f"Failed to parse analysis line '{xl_clean}': {e}") from e

        katscript = "\n".join(lines)
        logger.info("Model built (%d components, %d connections):", len(components), len(connections))
        for line in lines:
            logger.info("  %s", line)
        return model, katscript, _demod_map, space_rename

    # ---------- Simulation Execution ----------

    def run_noxaxis(self, model) -> dict:
        """Run noxaxis, extract PD + CCD via sol.plot()"""
        try:
            sol = model.run("noxaxis()")
            outputs = {}
            ccd_data = {}
            import numpy as np, io, base64

            # Extract PD outputs
            if hasattr(model, 'detectors') and model.detectors:
                dets = model.detectors
                items = dets.items() if isinstance(dets, dict) else [
                    (getattr(d, 'name', str(d)), d) for d in dets
                ]
                for name, dname in items:
                    sname = str(name)
                    try:
                        val = sol[sname]
                        if hasattr(val, 'ndim') and val.ndim >= 2:
                            pass  # CCD handled below
                        else:
                            outputs[sname] = float(val)
                    except Exception:
                        pass

            # B2: Use sol.plot() for CCD images — figs is dict name→Figure
            import matplotlib.pyplot as plt
            try:
                figs, anims = sol.plot(cmap='hot')
                try:
                    fig_items = list(figs.items()) if hasattr(figs, 'items') else []
                except Exception:
                    fig_items = []
                logger.info('sol.plot() returned: figs=%s, anims=%s',
                            [f[0] for f in fig_items] if fig_items else 'None/empty',
                            list(anims.keys()) if hasattr(anims, 'keys') else 'None/empty')
                if fig_items:
                    for cname, fig in fig_items:
                        try:
                            val = sol[cname]
                            if hasattr(val, 'ndim') and val.ndim >= 2:
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                                buf.seek(0)
                                ccd_data[cname] = {'image': base64.b64encode(buf.read()).decode('utf-8')}
                                logger.info('CCD %s: image generated via sol.plot()', cname)
                            else:
                                plt.close(fig)
                        except Exception:
                            plt.close(fig)

                # Fallback: directly extract 2D data from all detectors
                if not ccd_data and hasattr(model, 'detectors') and model.detectors:
                    dets = model.detectors
                    items = dets.items() if isinstance(dets, dict) else [
                        (getattr(d, 'name', str(d)), d) for d in dets
                    ]
                    for name, _ in items:
                        sname = str(name)
                        try:
                            val_arr = np.array(sol[sname], dtype=complex)
                            if val_arr.ndim >= 2:
                                intensity = np.abs(val_arr)
                                if intensity.size > 0:
                                    fig = plt.figure(figsize=(5, 5))
                                    ax = fig.add_subplot(111)
                                    ax.pcolormesh(intensity, cmap='hot', shading='auto')
                                    ax.set_aspect('equal')
                                    ax.set_title(sname)
                                    buf = io.BytesIO()
                                    fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                                    buf.seek(0)
                                    ccd_data[sname] = {'image': base64.b64encode(buf.read()).decode('utf-8')}
                                    plt.close(fig)
                                    logger.info('CCD %s: image generated via direct 2D extraction', sname)
                        except Exception:
                            pass
            except Exception as e:
                logger.warning('CCD image generation failed: %s', e, exc_info=True)


            logger.info('pd: %s, ccd: %s', outputs, list(ccd_data.keys()))
            return {'outputs': outputs, 'ccd': ccd_data}
        except Exception as e:
            raise SimulationError(f'simulation failed: {e}') from e

    def run_xaxis(
        self, model, params: list, mode: str = "together",
        demod_map: dict = None,
    ) -> dict:
        """
        Run parameter sweep.
        params: [{"param": "m1.phi", "start": 0, "stop": 360, "steps": 100}, ...]
        mode: "together" (vary all params in parallel) or "separate" (nested sweep, max 2 params)
        """
        import numpy as np
        try:
            if mode == 'together':
                # xaxis(param1, lin, s1, e1, N, param2, lin, s2, e2, ...)
                cmd_parts = []
                N = params[0]['steps']
                for p in params:
                    pname = p['param']
                    if pname.startswith('var:'): pname = pname[4:]
                    cmd_parts.append(pname)
                    cmd_parts.append('lin')
                    cmd_parts.append(str(p['start']))
                    cmd_parts.append(str(p['stop']))
                    cmd_parts.append(str(N))
                cmd = "xaxis(" + ", ".join(cmd_parts) + ")"
                logger.info("Running: %s", cmd)
                sol = model.run(cmd)
                x_data = np.array(sol.x, dtype=float).flatten()
            elif mode == 'separate' and len(params) >= 2:
                P = params[0]; Q = params[1]
                p1 = P['param']
                if p1.startswith('var:'): p1 = p1[4:]
                p2 = Q['param']
                if p2.startswith('var:'): p2 = p2[4:]
                cmd = f"x2axis({p1}, lin, {P['start']}, {P['stop']}, {P['steps']}, {p2}, lin, {Q['start']}, {Q['stop']}, {Q['steps']})"
                logger.info("Running: %s", cmd)
                sol = model.run(cmd)
                x_data = np.array(sol.x, dtype=float)  # 2D grid
            else:
                raise SimulationError(f"Invalid sweep: mode={mode}, params={len(params)}")
        except Exception as e:
            err_str = str(e)
            if 'depends on a symbolic' in err_str or 'cannot be directly changed' in err_str:
                import re
                match = re.search(r"Symbolic='(\w+)'", err_str)
                if match:
                    sym_name = match.group(1)
                    logger.info("Resolving symbolic dependency, retrying with '%s'", sym_name)
                    if mode == 'together':
                        cmd_parts = []; N = params[0]['steps']
                        for p in params:
                            cmd_parts.append(sym_name)
                            cmd_parts.append('lin')
                            cmd_parts.append(str(p['start']))
                            cmd_parts.append(str(p['stop']))
                            cmd_parts.append(str(N))
                        cmd = "xaxis(" + ", ".join(cmd_parts) + ")"
                        logger.info("Retrying: %s", cmd)
                        sol = model.run(cmd)
                        x_data = np.array(sol.x, dtype=float).flatten()
                    elif mode == 'separate' and len(params) >= 2:
                        P = params[0]; Q = params[1]
                        cmd = f"x2axis({sym_name}, lin, {P['start']}, {P['stop']}, {P['steps']}, {sym_name}, lin, {Q['start']}, {Q['stop']}, {Q['steps']})"
                        logger.info("Retrying: %s", cmd)
                        sol = model.run(cmd)
                        x_data = np.array(sol.x, dtype=float)
                    else:
                        raise SimulationError(f"Sweep failed: {e}") from e
                else:
                    raise SimulationError(f"Sweep failed: {e}") from e
            else:
                raise SimulationError(f"Sweep failed: {e}") from e

        yseries = []
        ccd_anim = {}
        if hasattr(model, 'detectors') and model.detectors:
            dets = model.detectors
            items = dets.items() if isinstance(dets, dict) else [
                (getattr(d, 'name', str(d)), d) for d in dets
            ]
            for name, _ in items:
                sname = str(name)
                try:
                    val_arr = np.array(sol[sname], dtype=complex)
                    if val_arr.ndim >= 2:
                        intensity = np.abs(val_arr)
                        if intensity.ndim >= 3:
                            # 3D: per-step CCD frames from sol[name] (if Finesse provides them)
                            frames = [intensity[fi].tolist() for fi in range(intensity.shape[0])]
                            ccd_anim[sname] = {"frames": frames}
                            logger.info("CCD %s anim 3D: %d frames", sname, len(frames))
                        else:
                            ccd_anim[sname] = {"frames": [intensity.tolist()]}
                            logger.info("CCD %s single frame", sname)
                    else:
                        vals = np.abs(val_arr).flatten()
                        yseries.append({"label": sname, "data": vals.tolist()})
                        # Only return phase for demodulated detectors (pd1/pd2), not regular pd
                        _is_demod = demod_map.get(sname, False) if demod_map else False
                        if _is_demod:
                            phase_vals = np.angle(val_arr, deg=True).flatten()
                            yseries.append({"label": sname + "_phase", "data": phase_vals.tolist()})
                        if vals.size > 1:
                            pd_elem = getattr(model, sname, None)
                            pd_node = getattr(pd_elem, 'node', '?') if pd_elem else '?'
                            logger.info("PD %s@%s: %d pts, min=%.4g max=%.4g", sname, pd_node, vals.size, vals.min(), vals.max())
                except Exception:
                    try:
                        yseries.append({"label": sname, "data": np.array(sol[sname], dtype=float).flatten().tolist()})
                    except Exception:
                        pass

            # B2: Use sol.plot() for true per-step CCD animation
            has_ccd = any(v.get('frames') for v in ccd_anim.values())
            if has_ccd:
                try:
                    import matplotlib.pyplot as plt, io, base64
                    figs, anims = sol.plot(cmap='hot')
                    if anims:
                        # anims is dict name→Animation or list of Animation objects
                        anim_items = anims.items() if isinstance(anims, dict) else list(enumerate(anims))
                        for cname_key, anim in anim_items:
                            cname = str(cname_key)
                            new_frames = []
                            anim_fig = getattr(anim, '_fig', None)
                            for fi in range(len(x_data)):
                                fig = anim_fig if anim_fig is not None else plt.figure(figsize=(5, 5))
                                try:
                                    anim._draw_frame(fi)
                                except Exception:
                                    pass
                                buf = io.BytesIO()
                                fig.savefig(buf, format='png', bbox_inches='tight', dpi=80)
                                buf.seek(0)
                                new_frames.append(base64.b64encode(buf.read()).decode('utf-8'))
                                if anim_fig is None:
                                    plt.close(fig)
                            if new_frames:
                                if cname in ccd_anim:
                                    ccd_anim[cname]['frames_png'] = new_frames
                                    ccd_anim[cname]['frames'] = new_frames
                                    logger.info('CCD %s: %d frames from sol.plot() animation', cname, len(new_frames))
                                else:
                                    ccd_anim[cname] = {"frames": new_frames, "frames_png": new_frames}
                                    logger.info('CCD %s (sol.plot): %d frames', cname, len(new_frames))
                except Exception as e:
                    logger.warning('sol.plot() animation extraction failed: %s', e)
                    import traceback
                    logger.warning(traceback.format_exc())


        return {
            "type": "xaxis",
            "x": x_data.flatten().tolist() if x_data.ndim > 1 else x_data.tolist(),
            "y": yseries,
            "param": params[0]['param'] if len(params) == 1 else f"{len(params)} params ({mode})",
            "ccd_anim": ccd_anim,
        }

    # ---------- Utility Methods ----------

    def _extract_detector_outputs(self, model, sol) -> dict:
        """Extract detector output values from the model"""
        outputs = {}

        # Method 1: Get from model.detectors
        if hasattr(model, 'detectors'):
            detectors = model.detectors
            # detectors may be dict {name: object} or similar object-only structure
            if isinstance(detectors, dict):
                items = detectors.items()
            else:
                items = [(getattr(d, 'name', str(d)), d) for d in detectors]

            for det_name, det_obj in items:
                name = str(det_name)  # ensure string type
                try:
                    value = sol[name]
                    if isinstance(value, (int, float, np.floating)):
                        outputs[name] = float(value)
                    elif isinstance(value, np.ndarray):
                        outputs[name] = value.real.tolist()
                except (KeyError, TypeError, IndexError):
                    pass

        # Method 2: Walk through model attributes looking for Readout types
        if not outputs:
            for attr_name in dir(model):
                if attr_name.startswith('_'):
                    continue
                try:
                    obj = getattr(model, attr_name)
                except Exception:
                    continue
                if obj is not None:
                    cls_name = obj.__class__.__name__
                    if any(kw in cls_name for kw in ('Detector', 'Readout')):
                        try:
                            outputs[attr_name] = float(sol.get(attr_name, 0))
                        except (ValueError, TypeError):
                            pass

        return outputs

    def _resolve_param(self, model, param_path: str):
        """Resolve "c0.phi" -> model.c0.phi parameter object."""
        parts = param_path.split('.')
        if len(parts) != 2:
            return None
        element_name, param_name = parts
        element = getattr(model, element_name, None)
        if element is not None:
            return getattr(element, param_name, None)
        return None

    @staticmethod
    def _has_detector(model) -> bool:
        """Check whether the model already has a detector."""
        if hasattr(model, 'detectors'):
            return len(model.detectors) > 0
        return False

    def get_katscript(self, model) -> str:
        """Export the model's KatScript representation."""
        try:
            buf = StringIO()
            model._dump_kat(buf)
            return buf.getvalue()
        except Exception:
            return str(model)


def _safe_array(solution, attr_name: str) -> Optional[np.ndarray]:
    """Safely retrieve a numpy array from a solution object."""
    try:
        val = getattr(solution, attr_name)
        if val is not None:
            arr = np.asarray(val)
            if arr.ndim > 0:
                return arr
    except Exception:
        pass
    return None


def _print_model_info(model):
    """Print model debug information to the log."""
    logger.info("======== Model Info ========")
    if hasattr(model, 'elements'):
        logger.info("Elements: %s", list(model.elements.keys()))
    if hasattr(model, 'detectors'):
        detectors = model.detectors
        if isinstance(detectors, dict):
            logger.info("Detectors: %s", list(detectors.keys()))
        else:
            names = [getattr(d, 'name', str(d)) for d in detectors]
            logger.info("Detectors: %s", names)
    try:
        from io import StringIO
        buf = StringIO()
        model._dump_kat(buf)
        logger.info("KatScript:\n%s", buf.getvalue().strip())
    except Exception:
        pass
    logger.info("==============================")


# Global engine singleton (lazy initialization)
_engine_instance = None


def get_engine() -> FinesseEngine:
    """Get the FinesseEngine singleton — initialized on first call."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = FinesseEngine()
    return _engine_instance
