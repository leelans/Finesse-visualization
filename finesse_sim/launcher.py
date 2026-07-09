"""
Optics Simulator — standalone launcher (no debug/crash features).

Run: python launcher.py
Build: pyinstaller optics_sim.spec
"""
import os
import sys
import json
import subprocess
import threading
import webbrowser
import traceback
import time

# NOTE: This launcher is always started by run.bat using the dedicated 'finesse_sim'
# conda env (finesse 3.x + flask), so no env auto-detection / re-exec is needed here.

# ====== Safe DLL search path fix for conda envs (matplotlib/ft2font) ======
# Only add the ACTIVE interpreter's Library/bin to the DLL search path.
# Do NOT call SetDllDirectoryW (it breaks the process-wide DLL search order)
# and do NOT import ctypes here (it can fail to load in restricted environments).
if sys.platform == 'win32':
    _libbin = os.path.join(sys.prefix, 'Library', 'bin')
    if os.path.isdir(_libbin):
        try:
            os.add_dll_directory(_libbin)
        except Exception:
            pass
    os.environ.setdefault('CONDA_DLL_SEARCH_MODIFICATION_ENABLE', '1')

# ====== Load external Python libraries (user's system Python) ======
def _load_external_site_packages():
    """Append compatible conda/system site-packages to sys.path as a fallback.

    Only Python-version-matching envs are added, and the base (root) conda
    env is skipped to avoid mixing incompatible compiled extensions (e.g. _ctypes).
    """
    py_tag = f'python{sys.version_info.major}.{sys.version_info.minor}'
    py_tag_short = f'python{sys.version_info.major}{sys.version_info.minor}'
    candidates = []

    # 1. Conda envs (skip base/root env, skip incompatible Python versions)
    try:
        r = subprocess.run(['conda', 'env', 'list'], capture_output=True, text=True, timeout=5)
        cur_py = f'{sys.version_info.major}.{sys.version_info.minor}'
        for line in r.stdout.split('\n'):
            s = line.strip()
            if not s or s.startswith('#') or s.startswith('*'):
                continue
            parts = s.split()
            env_path = parts[-1]
            if os.path.normcase(os.path.normpath(env_path)) == os.path.normcase(os.path.normpath(sys.base_prefix)):
                continue  # skip base env
            # Verify the env's Python version matches the active interpreter
            # BEFORE trusting its compiled extensions (e.g. _ctypes). Conda
            # paths (.../Lib/site-packages) carry no 'python' substring, so a
            # path-based guard cannot detect cross-version mismatches here.
            py_exe = os.path.join(env_path, 'python.exe')
            if os.path.exists(py_exe):
                try:
                    vr = subprocess.run(
                        [py_exe, '-c', 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")'],
                        capture_output=True, text=True, timeout=5)
                    env_py = vr.stdout.strip()
                    if vr.returncode != 0 or cur_py != env_py:
                        print(f"[LOADER] Skip conda env {env_path} (Python {env_py} != {cur_py})")
                        continue
                except Exception as _verr:
                    print(f"[LOADER] Skip conda env {env_path} (version check failed: {_verr})")
                    continue
            sp = os.path.join(env_path, 'Lib', 'site-packages')
            if os.path.isdir(sp):
                candidates.append(sp)
    except Exception:
        pass

    # 2. System PATH python (skip if version mismatched)
    for path_dir in os.environ.get('PATH', '').split(os.pathsep):
        for py_exe in ['python.exe', 'python3.exe']:
            full = os.path.join(path_dir, py_exe)
            if os.path.exists(full):
                try:
                    r = subprocess.run([full, '-c', 'import sys; print(sys.version)'],
                                       capture_output=True, text=True, timeout=5)
                    ver = r.stdout.strip()
                    if f'{sys.version_info.major}.{sys.version_info.minor}' not in ver:
                        continue
                    r2 = subprocess.run([full, '-c', 'import site; print(site.getsitepackages()[0])'],
                                        capture_output=True, text=True, timeout=5)
                    sp = r2.stdout.strip()
                    if sp and os.path.isdir(sp):
                        candidates.append(sp)
                except Exception:
                    pass

    # 3. user_packages/ directory next to the exe
    exe_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
    user_pkg = os.path.join(exe_dir, 'user_packages')
    if os.path.isdir(user_pkg):
        candidates.append(user_pkg)

    # Append compatible, deduplicated paths only
    seen = set(map(os.path.normcase, sys.path))
    for sp in candidates:
        spn = os.path.normcase(os.path.normpath(sp))
        # Only accept site-packages whose Python version matches the active interpreter
        if 'site-packages' in spn and 'python' in spn:
            if py_tag not in spn and py_tag_short not in spn:
                continue
        if spn not in seen:
            sys.path.append(sp)
            seen.add(spn)
            print(f"[LOADER] External site-packages: {sp}")

_load_external_site_packages()

from flask import Flask, render_template, jsonify, request, send_file, make_response

# ====== Sweep progress tracking ======
_sweep_progress = {"total": 0, "current": 0, "status": "idle"}
_sweep_progress_lock = threading.Lock()

# ====== 日志 ======
import logging
logger = logging.getLogger('optics-sim')
logger.setLevel(logging.INFO)
logger.propagate = False  # Prevent propagation to root logger
import logging.handlers as _lh
_base = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
LOG_FILE = os.path.join(_base, 'optics-sim.log')
_handler = _lh.RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s - %(message)s', '%H:%M:%S'))
logger.addHandler(_handler)

# ====== 路径设置 ======
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    # Write crash/log files in executable directory
    EXE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXE_DIR = BASE_DIR

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
STATIC_DIR = os.path.join(BASE_DIR, 'static')
NODE_MODULES_DIR = os.path.join(BASE_DIR, 'node_modules')

# ====== 启动诊断 ======
try:
    from finesse_engine import get_engine
    engine = get_engine()
    logger.info("finesse 3 loaded successfully")
except Exception as e:
    logger.error("finesse not available: %s", e)

# ====== Flask App ======
app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR, static_url_path='/static')

@app.route('/node_modules/<path:filename>')
def serve_node_modules(filename):
    from flask import Response
    filepath = os.path.join(NODE_MODULES_DIR, filename)
    if not os.path.exists(filepath):
        return 'File not found', 404
    mimetype = 'application/wasm' if filename.endswith('.wasm') else None
    return send_file(filepath, mimetype=mimetype)

# Delayed import — let import errors surface cleanly
try:
    from component_registry import registry
    from finesse_engine import get_engine, FinesseError, ModelBuildError, SimulationError
    engine = get_engine()
    logger.info("Core modules loaded successfully")
except Exception as e:
    logger.critical("Failed to load core modules: %s", e)
    raise


# ====== API 路由 ======

@app.route('/')
def index():
    path = os.path.join(TEMPLATE_DIR, 'index.html')
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    resp = make_response(html)
    resp.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    return resp

@app.route('/jupyter')
def jupyter_page():
    return render_template('jupyter.html')


@app.route('/api/components')
def list_components():
    return jsonify([c.to_frontend() for c in registry.list_all()])


@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/api/svg-icons')
def svg_icons():
    """返回可用的图标列表（SVG + PNG + JPG + GIF）"""
    import glob
    icons_dir = os.path.join(STATIC_DIR, 'components')
    if not os.path.isdir(icons_dir):
        return jsonify({"icons": [], "exts": {}})
    exts = {}
    for ext in ['svg', 'png', 'jpg', 'jpeg', 'gif']:
        for f in glob.glob(os.path.join(icons_dir, '*.' + ext)):
            name = os.path.splitext(os.path.basename(f))[0]
            exts[name] = ext
    return jsonify({"icons": list(exts.keys()), "exts": exts, "dir": icons_dir})


@app.route('/api/svg/<name>')
def svg_icon(name):
    """返回图标（自动检测 SVG/PNG/JPG 等）"""
    safe_name = os.path.basename(name)
    mime_map = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.gif': 'image/gif'}
    for ext, mime in mime_map.items():
        path = os.path.join(STATIC_DIR, 'components', safe_name + ext)
        if os.path.exists(path):
            return send_file(path, mimetype=mime)
    return 'Not found', 404


@app.route('/api/sweep-progress')
def sweep_progress():
    with _sweep_progress_lock:
        return jsonify(dict(_sweep_progress))

@app.route('/api/eval-vars', methods=['POST'])
def eval_vars():
    """Evaluate Python variable definitions and return name→value mapping."""
    try:
        import builtins
        code = request.get_json(silent=True) or {}
        lines = (code.get('code', '') or '').split('\n')
        eval_globals = {"__builtins__": builtins}
        for line in lines:
            line = line.strip()
            if line.startswith('import ') or line.startswith('from '):
                try:
                    exec(line, eval_globals)
                except Exception as e:
                    logger.warning("eval_vars: failed to exec: %s — %s", line, e)
        ns = {}
        logger.info("eval_vars: %d lines to evaluate, globals=%s", len(lines), [k for k in eval_globals.keys() if not k.startswith('__')])
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('import') or line.startswith('from'):
                continue
            if '=' in line:
                eq = line.index('=')
                name = line[:eq].strip()
                val_expr = line[eq+1:].strip()
                if not name or not val_expr:
                    continue
                ci = val_expr.find('#')
                if ci >= 0:
                    val_expr = val_expr[:ci].strip()
                try:
                    val = eval(val_expr, eval_globals, ns)
                    ns[name] = val
                    logger.info("eval_vars: %s = %s (%s)", name, val, type(val).__name__)
                except Exception as e:
                    logger.warning("eval_vars: %s FAILED: %s", name, e)
        result = {}
        for k, v in ns.items():
            if isinstance(v, (int, float)):
                result[k] = v
            elif isinstance(v, (list, tuple)) and len(v) == 1:
                result[k] = float(v[0])
        logger.info("eval_vars returning %d vars: %s", len(result), list(result.keys()))
        return jsonify(result)
    except Exception as e:
        logger.exception("eval_vars crashed: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route('/api/simulate', methods=['POST'])
def simulate():
    logger.info("Simulation request received")
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    components = data.get('components', [])
    connections = data.get('connections', [])
    vars_list = data.get('vars', [])
    boxes = data.get('boxes', [])
    analysis = data.get('analysis', {})
    preamble = data.get('preamble', [])

    logger.debug("Components: %d, Connections: %d, Vars: %d, Analysis: %s",
                 len(components), len(connections), len(vars_list), analysis.get('type'))

    if not components:
        return jsonify({"error": "No components provided"}), 400

    try:
        # Step 1: 构建模型
        logger.debug("Building model...")
        model, katscript, demod_map, space_rename = engine.build_model(components, connections, vars_list, boxes, preamble=preamble)
        homs_str = str(list(model.homs)) if hasattr(model, 'homs') else 'NO HOMS'
        logger.debug("=== MODEL HOMS: %s", homs_str)
        result = {"katscript": katscript, "rename_map": space_rename}  # always include katscript in response

        # Step 2: 运行分析
        atype = analysis.get('type', 'noxaxis')
        logger.info("Running analysis: %s", atype)

        if atype == 'noxaxis':
            sim_result = engine.run_noxaxis(model)
            result.update({"type": "noxaxis", "outputs": sim_result.get("outputs", {}), "ccd": sim_result.get("ccd", {})})
        elif atype == 'xaxis':
            params = analysis.get('params', [])
            mode = analysis.get('mode', 'together')
            if not params:
                return jsonify({"error": "No parameters specified"}), 400
            logger.info("Sweeping %d params, mode=%s", len(params), mode)
            total = (params[0]['steps'] if mode == 'together'
                     else params[0]['steps'] * (params[1]['steps'] if len(params) > 1 else 1))
            with _sweep_progress_lock:
                _sweep_progress.update({"total": total, "current": 0, "status": "running"})
            try:
                scan = engine.run_xaxis(model, params=params, mode=mode, demod_map=demod_map)
            finally:
                with _sweep_progress_lock:
                    _sweep_progress.update({"current": total, "status": "idle"})
            scan["katscript"] = katscript
            result.update(scan)
        else:
            return jsonify({"error": f"Unknown analysis: {atype}"}), 400

        logger.info("Simulation completed successfully")
        return jsonify(result)

    except ModelBuildError as e:
        logger.error("Model build failed: %s", e)
        return jsonify({"error": str(e), "type": "build_error"}), 400
    except SimulationError as e:
        logger.error("Simulation failed: %s", e)
        import traceback as _tb
        logger.error("Simulation traceback:\n%s", ''.join(_tb.format_exc()))
        return jsonify({"error": str(e), "type": "sim_error", "katscript": result.get("katscript", "")}), 500
    except Exception as e:
        # 未预期的错误 —— 记录完整 traceback
        tb = traceback.format_exc()
        logger.exception("Unexpected simulation error")
        logger.error("Katscript:\n%s", result.get("katscript", "(no katscript)"))
        return jsonify({
            "error": str(e) + " (unexpected)",
            "type": "unexpected",
            "traceback": tb.split('\n'),
            "katscript": result.get("katscript", ""),
        }), 500


@app.route('/api/beam-trace', methods=['POST'])
def beam_trace_api():
    """光束追踪——使用 Finesse 原生 beam_trace()"""
    data = request.get_json(silent=True) or {}
    components = data.get('components', [])
    connections = data.get('connections', [])
    vars_list = data.get('vars', [])
    boxes = data.get('boxes', [])
    preamble = data.get('preamble', [])
    try:
        model, katscript, demod_map, _ = engine.build_model(components, connections, vars_list, boxes, preamble=preamble)
        sol = model.run("noxaxis()")
        # Finesse native beam trace
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            model.beam_trace()
        finally:
            sys.stdout = old_stdout
        trace_text = buf.getvalue()
        if not trace_text.strip():
            trace_text = "(no beam trace data available)"
        return jsonify({"trace_text": trace_text, "katscript": katscript})
    except Exception as e:
        import traceback
        return jsonify({"error": str(e)}), 500


@app.route('/api/trace-path', methods=['POST'])
def trace_path_api():
    """手动 beam trace：trace node1 node2"""
    data = request.get_json(silent=True) or {}
    path = data.get('path', '').strip()
    components = data.get('components', [])
    connections = data.get('connections', [])
    vars_list = data.get('vars', [])
    boxes = data.get('boxes', [])
    if not path:
        return jsonify({"error": "No path specified"}), 400
    preamble = data.get('preamble', [])
    try:
        model, katscript, demod_map, _ = engine.build_model(components, connections, vars_list, boxes, preamble=preamble)
        model.run("noxaxis()")
        import io, sys
        old_stdout = sys.stdout
        sys.stdout = buf = io.StringIO()
        try:
            if path.startswith('propagate '):
                parts = path.split()
                result = model.propagate_beam(from_node=parts[1], to_node=parts[2])
                print(result)
            else:
                model.parse("trace " + path)
        finally:
            sys.stdout = old_stdout
        trace_text = buf.getvalue()
        if not trace_text.strip():
            trace_text = "(no trace data)"
        return jsonify({"trace_text": trace_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/jupyter', methods=['POST'])
def jupyter_api():
    try:
        data = request.get_json(silent=True) or {}
        logger.info("JUPYTER: got data keys=%s", list(data.keys()))
        code = data.get('code', '')
        ns = {}
        # np
        try:
            import numpy as np; ns['np'] = np
        except: pass
        # Stored data
        for name, d in (data.get('data', {}) or {}).items():
            if isinstance(d, list):
                try: ns[name] = np.array(d, dtype=float)
                except: pass
        # Build model
        components = data.get('components', [])
        if components:
            try:
                model, _, _discard, _ = engine.build_model(
                    components, data.get('connections', []),
                    data.get('vars', []), data.get('boxes', []),
                    preamble=data.get('preamble', []))
                try: model.run("noxaxis()")
                except Exception as run_err: ns['model_warning'] = str(run_err)
                ns['model'] = model
                import finesse; ns['finesse'] = finesse
                # Add each component to namespace so user can access them directly
                for comp in components:
                    cid = comp.get('id', '')
                    try: ns[cid] = getattr(model, cid, None)
                    except: pass
                logger.info("JUPYTER: model built, %d components in namespace", len(components))
            except Exception as e:
                ns['model_error'] = str(e)
                logger.warning("JUPYTER model build failed: %s", e)
        # Exec
        import io, sys
        buf = io.StringIO()
        old = sys.stdout; sys.stdout = buf
        try:
            exec(code, ns)
        except Exception as e:
            sys.stdout = old
            return jsonify({'error': str(e), 'output': buf.getvalue()})
        finally:
            sys.stdout = old
        return jsonify({'output': buf.getvalue() or '(no output)'})
    except Exception as top_err:
        import traceback
        logger.error("JUPYTER CRASH: %s\n%s", top_err, traceback.format_exc())
        return jsonify({'error': 'Crash: ' + str(top_err)}), 200

# ====== Examples API ======
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')
os.makedirs(EXAMPLES_DIR, exist_ok=True)

@app.route('/api/examples', methods=['GET', 'POST'])
def examples_api():
    """Save/load examples to the examples/ directory."""
    examp_dir = os.path.join(BASE_DIR, 'examples')
    os.makedirs(examp_dir, exist_ok=True)

    if request.method == 'GET':
        files = sorted([f for f in os.listdir(examp_dir) if f.endswith('.json')],
                       key=lambda f: os.path.getmtime(os.path.join(examp_dir, f)), reverse=True)
        result = []
        for f in files:
            try:
                with open(os.path.join(examp_dir, f), 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                result.append({
                    "name": data.get("name", os.path.splitext(f)[0]),
                    "filename": f,
                    "timestamp": os.path.getmtime(os.path.join(examp_dir, f)),
                    "data": data.get("data", {}),
                })
            except Exception:
                pass
        return jsonify(result)

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or 'unnamed').strip()
    safe_name = "".join(c for c in name if c.isalnum() or c in ' _-').rstrip()
    if not safe_name:
        safe_name = 'unnamed'
    filepath = os.path.join(examp_dir, f'{safe_name}.json')
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info("Example saved: %s", filepath)
        return jsonify({"ok": True, "file": os.path.basename(filepath)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/examples/delete', methods=['POST'])
def delete_example():
    """Delete a saved example."""
    data = request.get_json(silent=True) or {}
    filename = (data.get('filename') or '').strip()
    if not filename:
        return jsonify({"error": "No filename provided"}), 400
    examp_dir = os.path.join(BASE_DIR, 'examples')
    filepath = os.path.join(examp_dir, os.path.basename(filename))
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info("Example deleted: %s", filepath)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def internal_error(e):
    """Flask 层面 500 错误"""
    logger.error("Internal server error: %s", e)
    return jsonify({"error": "Internal server error"}), 500


# ====== 启动 ======

def _find_free_port(start=5000, max_attempts=50):
    """Find first available port starting from `start`."""
    import socket
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start  # fallback

def _open_browser(url):
    """Open the default browser to the app URL; never let a failure crash the server."""
    try:
        webbrowser.open(url)
    except Exception as e:
        logger.warning("Could not auto-open browser (%s). Open %s manually.", e, url)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', '-p', type=int, default=None, help='Server port')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not auto-open a browser (run.bat handles it instead)')
    args, _ = parser.parse_known_args()
    port = args.port or _find_free_port()
    url = f'http://localhost:{port}'
    # Log startup info so it survives even if the console window is closed.
    logger.info("Starting Finesse3 Optics Simulator — Standalone at %s", url)
    print("=" * 60)
    print("Finesse3 Optics Simulator — Standalone")
    print(f"Server running at: {url}")
    print("Open this URL in your browser.")
    print("Press Ctrl+C in this window to stop the server.")
    print("=" * 60)
    if not args.no_browser:
        threading.Timer(1.5, lambda: _open_browser(url)).start()

    try:
        app.run(host='0.0.0.0', port=port, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
        logger.info("Server stopped by user (Ctrl+C).")
    except Exception as e:
        logger.critical("Failed to start server: %s", e, exc_info=True)
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Print to console
        print(f"\n[FATAL] {type(e).__name__}: {e}", file=sys.stderr)
        traceback.print_exc()
    finally:
        # Keep CMD window open in frozen mode for error inspection
        if getattr(sys, 'frozen', False):
            print("\n" + "=" * 55)
            print("  Press Enter to close this window...")
            print("=" * 55)
            try:
                input()
            except (EOFError, KeyboardInterrupt):
                pass
