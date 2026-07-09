# Optics Simulator — Changelog

## [1.1.0] — 2026-07-03

### Added
- **Custom component**: Drag & drop "Custom" from the library to create arbitrary Finesse components (e.g. dbs, grating). Prompts for port count on drop. Properties panel exposes Kat Type and Extra param fields.
- **Dynamic port binding**: `run.bat` auto-detects a free port starting from 5000 using .NET TcpClient; `launcher.py` accepts `--port` argument.

### Fixed
- **Variable/space name collision**: When a space ID conflicts with a variable name, the SPACE is renamed (suffix `_space`) instead of the variable. Rename comments appear in KatScript output.
- **`{var}` expressions in KatScript**: `_resolve_braces()` evaluates Python f-string expressions like `{-mc2_angle}` before passing to Finesse's `model.parse()`, supporting arbitrary expressions via variable values.
- **Expression preservation**: Component parameters with `{var}` references (e.g. `T=1-{ITM_refl}`) are preserved as strings in `_paramExprs` and displayed in blue in the properties panel.
- **Export rename comments**: Both `.kat` and `.ipynb` exports include a header block listing all auto-renamed spaces.

### Changed
- **build_model() return type**: Now returns 4-tuple `(model, katscript, demod_map, space_rename)`.
- **API response**: `/api/simulate` response includes `rename_map` field.
- **`/api/eval-vars`**: Returns `{"value": <number>, "expr": <original_expression>}` per variable.
- **All comments translated to English** across 5 core source files: `finesse_engine.py`, `launcher.py`, `component_registry.py`, `debug.py`, `templates/index.html`.

### Files modified
| File | Changes |
|------|---------|
| `finesse_engine.py` | Phase 0 remove var_rename; Phase 2 add space_rename; `_resolve_braces()`; 4-tuple return; English comments |
| `launcher.py` | `--port` argument; 4-tuple unpacking; `rename_map` in response; English comments |
| `component_registry.py` | Custom component type; `_kat_type` handling in `build_kat_line`; English comments |
| `debug.py` | English comments and crash popup messages |
| `templates/index.html` | `_paramExprs` storage & display; `updateCustomKat()`; custom import/export; rename comments in export; English JS comments |
| `run.bat` | Auto-detect free port via PowerShell |

---

## [1.2.0] — 2026-07-08

### Fixed
- **`_ctypes` / `ft2font` DLL load failure on startup**: Removed the broken top-level ctypes patch (`import ctypes` + `SetDllDirectoryW`) that crashed under restricted DLL search. Now only adds the active interpreter's `Library\bin` via `os.add_dll_directory(sys.prefix/...)` on Windows (with `CONDA_DLL_SEARCH_MODIFICATION_ENABLE=1`).
- **Cross-version conda env conflict in `_load_external_site_packages()`**: Now skips the base/root conda env and verifies each candidate env's actual Python version (by running its `python.exe`) before appending to `sys.path`. The old path-string heuristic (`'python' in spn`) was a no-op for conda envs and has been removed.
- **`run.bat` silent crash (window closes instantly)**: Rewrote `run.bat` as pure ASCII (no Chinese / no UTF-8 BOM) so it no longer fails to parse under the GBK codepage on double-click. It now resolves the dedicated `finesse_sim` env directly via known install paths (`C:\Users\89589\.conda\envs\finesse_sim`, then `C:\ProgramData\anaconda3\envs\finesse_sim`) with a `conda run -n finesse_sim` fallback, instead of relying on `conda` being on PATH. The window now stays open on any error (`pause`).

### Changed
- **Startup env handling**: `launcher.py` no longer auto-detects/scans conda envs or re-execs under another interpreter. `run.bat` is solely responsible for launching under `finesse_sim` (finesse 3.x + flask). The plain `finesse` env must NOT be used (it lacks flask).
- **Logging**: `launcher.py` `main()` now writes the server URL and any fatal error (with traceback) to `optics-sim.log`, so startup failures are diagnosable without the console.

### Removed
- `detect_env.py` and `_qa_test_reexec.py` (superseded by `run.bat` path resolution).

### Files modified
| File | Changes |
|------|---------|
| `launcher.py` | Safe DLL fix; removed re-exec / auto-detect; `main()` logs URL + fatal errors to `optics-sim.log`; `--port` still accepted |
| `run.bat` | Pure ASCII; resolves `finesse_sim` path directly; prepends `Library\bin` to PATH; `pause` on exit/error |
| `detect_env.py` | Removed |
| `_qa_test_reexec.py` | Removed |

---

## [1.0.0] — 2026-06-29

### Initial release
- 11 built-in optical component types
- SVG canvas with drag & drop, rotation, flip, BFS layout
- KatScript import with Python variable resolution
- `noxaxis` and `xaxis` simulation
- CCD imaging via `sol.plot()`
- Jupyter notebook export
- Light/dark theme
