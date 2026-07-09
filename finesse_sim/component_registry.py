"""
Component registry — centralized management of all finesse component definitions,
parameter validation, and KatScript generation.

Design principles:
1. Single source of truth: all component information is defined only once here
2. Parameter validation: prevent invalid values from entering the finesse engine
3. Type safety: use dataclass to define clear data structures
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class PortDef:
    """Port definition"""
    name: str          # p1, p2, in, out
    direction: str     # "both", "in", "out"


@dataclass
class ComponentDef:
    """Component definition"""
    type_id: str                # laser, mirror, beamsplitter, ...
    display_name: str           # display name
    kat_command: str            # KatScript command: l, m, bs, lens, ...
    default_params: Dict[str, Any] = field(default_factory=dict)
    advanced_params: List[str] = field(default_factory=list)  # parameter names folded into Advanced
    ports: List[PortDef] = field(default_factory=list)
    visual_width: int = 40
    visual_height: int = 40
    visual_color: str = "#888888"

    def to_frontend(self) -> dict:
        """Export data for frontend"""
        return {
            "type": self.type_id,
            "name": self.display_name,
            "kat": self.kat_command,
            "params": self.default_params,
            "advanced": self.advanced_params,
            "ports": [{"name": p.name, "dir": p.direction} for p in self.ports],
            "width": self.visual_width,
            "height": self.visual_height,
            "color": self.visual_color,
        }


class ComponentRegistry:
    """Component registry"""

    def __init__(self):
        self._components: Dict[str, ComponentDef] = {}
        self._register_defaults()

    def _register_defaults(self):
        """Register standard component library (with full parameters)"""
        self.register(ComponentDef(
            type_id="laser", display_name="Laser", kat_command="l",
            default_params={"P": 1.0, "f": 0, "phase": 0},
            advanced_params=["f", "phase"],
            ports=[PortDef("p1", "out")],
            visual_width=40, visual_height=30, visual_color="#e74c3c",
        ))
        self.register(ComponentDef(
            type_id="mirror", display_name="Mirror", kat_command="m",
            default_params={"R": 0.99, "T": 0.01, "L": 0, "phi": 0.0,
                            "Rcx": None, "Rcy": None, "Rc": None, "xbeta": 0, "ybeta": 0,
                            "imaginary_transmission": None},
            advanced_params=["L", "Rcx", "Rcy", "xbeta", "ybeta"],
            ports=[PortDef("p1", "both"), PortDef("p2", "both")],
            visual_width=30, visual_height=60, visual_color="#3498db",
        ))
        self.register(ComponentDef(
            type_id="beamsplitter", display_name="Beamsplitter", kat_command="bs",
            default_params={"R": 0.5, "T": 0.5, "L": 0, "phi": 0, "alpha": 0,
                            "Rcx": None, "Rcy": None, "Rc": None, "xbeta": 0, "ybeta": 0,
                            "imaginary_transmission": None},
            advanced_params=["L", "alpha", "Rcx", "Rcy", "xbeta", "ybeta"],
            ports=[PortDef("p1", "both"), PortDef("p2", "both"),
                   PortDef("p3", "both"), PortDef("p4", "both")],
            visual_width=40, visual_height=40, visual_color="#9b59b6",
        ))
        self.register(ComponentDef(
            type_id="lens", display_name="Lens", kat_command="lens",
            default_params={"f": 1.0},
            advanced_params=[],
            ports=[PortDef("p1", "both"), PortDef("p2", "both")],
            visual_width=20, visual_height=60, visual_color="#2ecc71",
        ))
        self.register(ComponentDef(
            type_id="modulator", display_name="EOM", kat_command="mod",
            default_params={"f": 10e6, "midx": 0.1, "phase": 0, "order": 1},
            advanced_params=["phase", "order", "mod_type"],
            ports=[PortDef("p1", "both"), PortDef("p2", "both")],
            visual_width=30, visual_height=50, visual_color="#e67e22",
        ))
        self.register(ComponentDef(
            type_id="isolator", display_name="Isolator", kat_command="isol",
            default_params={"S": 0},
            advanced_params=[],
            ports=[PortDef("p1", "both"), PortDef("p2", "both")],
            visual_width=30, visual_height=40, visual_color="#1abc9c",
        ))
        self.register(ComponentDef(
            type_id="photodetector", display_name="Photodetector", kat_command="pd",
            default_params={},
            advanced_params=["pdtype"],
            ports=[PortDef("p1", "in")],
            visual_width=30, visual_height=35, visual_color="#34495e",
        ))
        self.register(ComponentDef(
            type_id="ccd", display_name="CCD", kat_command="ccd",
            default_params={"xlim": 1, "ylim": 1, "npts": 256},
            advanced_params=["w0_scaled"],
            ports=[PortDef("p1", "in")],
            visual_width=40, visual_height=30, visual_color="#f39c12",
        ))
        self.register(ComponentDef(
            type_id="gauss", display_name="Gauss", kat_command="gauss",
            default_params={"w0": 1e-3, "z": 0},
            advanced_params=["w0x", "w0y", "zx", "zy"],
            ports=[PortDef("p1", "both")],
            visual_width=30, visual_height=30, visual_color="#8e44ad",
        ))
        self.register(ComponentDef(
            type_id="cavity", display_name="Cavity", kat_command="cav",
            default_params={},
            advanced_params=[],
            ports=[PortDef("p1", "both")],
            visual_width=30, visual_height=20, visual_color="#c0392b",
        ))
        self.register(ComponentDef(
            type_id="ad", display_name="Amplitude Detector", kat_command="ad",
            default_params={"f": 0, "n": 0, "m": 0},
            advanced_params=[],
            ports=[PortDef("p1", "in")],
            visual_width=30, visual_height=35, visual_color="#34495e",
        ))
        self.register(ComponentDef(
            type_id="custom", display_name="Custom", kat_command="",
            default_params={},
            advanced_params=[],
            ports=[PortDef("p1", "both"), PortDef("p2", "both"),
                   PortDef("p3", "both"), PortDef("p4", "both")],
            visual_width=40, visual_height=40, visual_color="#7f8c8d",
        ))

    def register(self, comp: ComponentDef):
        self._components[comp.type_id] = comp

    def get(self, type_id: str) -> Optional[ComponentDef]:
        return self._components.get(type_id)

    def list_all(self) -> List[ComponentDef]:
        return list(self._components.values())

    def build_kat_line(self, comp_id: str, type_id: str, params: dict, used_params: set = None) -> str:
        """
        Build a single KatScript line.

        Rules:
        - Basic parameters are always output (skipped when value is None)
        - Advanced parameters are only output when they have been used
          (present at import or edited in GUI)
        - Values are automatically formatted
        """
        # Custom component: use _kat_type for the kat command
        if type_id == "custom":
            kat = params.get('_kat_type', '?')
            if not kat:
                raise ValueError("Custom component has no kat type set")
            used = used_params or set()
            param_str = ' '.join(
                f'{k}={_format_param(params.get(k))}'
                for k in used if params.get(k) is not None and not k.startswith('_')
            )
            return f'{kat} {comp_id} {param_str}'.strip()

        comp = self.get(type_id)
        if comp is None:
            raise ValueError(f"Unknown component type: {type_id}")

        kat = comp.kat_command
        merged_params = {}
        used = used_params or set()
        advanced_set = set(comp.advanced_params)

        for key in comp.default_params:
            if key in params and params[key] is not None:
                merged_params[key] = params[key]
            else:
                merged_params[key] = comp.default_params[key]

        # Output rules:
        # - used non-empty (import/manual edit): only output params in used
        #   (+ some required structural params)
        # - used empty (newly dragged component): output all non-None defaults
        if used:
            param_str = ' '.join(
                f'{k}={_format_param(params.get(k, comp.default_params.get(k)))}'
                for k in used if params.get(k, comp.default_params.get(k)) is not None
            )
        else:
            param_str = ' '.join(
                f'{k}={_format_param(v)}' for k, v in merged_params.items()
                if v is not None
                and v != float('inf')
                and not (isinstance(v, float) and v != v)
            )
        return f'{kat} {comp_id} {param_str}'.strip()


def _format_param(value) -> str:
    """Format parameter value to KatScript-compatible format"""
    if isinstance(value, str) and value:
        return value  # expression output as-is, e.g. "-m1.phi"
    if isinstance(value, float):
        if value == 0.0:
            return "0"
        if abs(value) >= 1e6 or (abs(value) < 1e-4 and value != 0):
            return f"{value:.6e}"
        return f"{value:.6f}".rstrip('0').rstrip('.')
    if isinstance(value, int):
        return str(value)
    return str(value)


# global singleton
registry = ComponentRegistry()
