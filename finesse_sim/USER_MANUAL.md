# Finesse3 Optics Simulator — User Manual

> Version 1.1.0 — Frequency-domain optical interferometer design & simulation

---

## 1. Getting Started

**Requirements:** Windows 10/11, [Miniconda](https://docs.conda.io/en/latest/miniconda.html), Finesse 3 (>= 3.0a33) in a conda env named `finesse`.

```bash
conda create -n finesse python=3.10 -y
conda activate finesse
pip install finesse numpy scipy networkx flask
```

**Launch:** double-click `run.bat`. The launcher finds a free port and opens your browser at `http://localhost:5000`.

---

## 2. Interface Overview

| Panel | Purpose |
|-------|---------|
| Library (left) | Drag components onto the canvas |
| Canvas (center) | Visual layout of the optical setup |
| Properties (right) | Edit parameters of the selected item |
| Output (bottom) | KatScript preview, charts, CCD images |

Shortcuts: **Shift+drag** locks movement direction. **Delete** removes the selected item.

---

## 3. Building a Model

1. Drag a component from the left library onto the canvas.
2. Connect ports by dragging from one component's red port dot to another.
3. Repeat to build your optical layout.

### Available Components

| Icon | Type | Description |
|------|------|-------------|
| L | Laser | Laser source |
| M | Mirror | Reflective mirror |
| BS | Beamsplitter | 4-port splitter |
| Ln | Lens | Thin lens |
| EOM | Modulator | Electro-optic modulator |
| Iso | Isolator | Optical isolator |
| PD | Photodetector | Power detector |
| CCD | CCD | Beam profile camera |
| G | Gauss | Beam parameter definition |
| Cav | Cavity | Optical cavity |
| AD | Amp. Detector | Amplitude detector |
| ? | Custom | Other KatScript component |

### Manipulating Components

- **Drag** to move.
- **Flip** (Flip H / Flip V buttons in Properties).
- **Rotate** (+-90, +-45, or custom angle in Properties).
- **Right-click** for context menu, or **Delete** key to remove.

---

## 4. Editing Components

Click a component. The Properties panel shows:

Name — unique ID, e.g. `m1`.
Parameters — `R`, `T`, `f`, `phi` (numbers or `{var}` expressions).
Advanced — click to show `alpha`, `Rc`, etc.
Extra param — add any KatScript parameter.

Blue text = active variable reference. Example: `R={bs_r}`, `T=1-{bs_r}`.

---

## 5. Editing Connections

Click a connection line. Properties shows:

Port selectors — switch which ports are linked.
Name — space ID.
Length (L) — optical path length in metres.
Extra param — e.g. `nr` for refractive index.

---

## 6. Variables and Expressions

Click **Vars** in the toolbar to open the Variables panel. Define:

```
Name: arm_len    Value: 3.0
Name: R_bs       Value: 0.5
```

Use `{name}` in any parameter field: `R={R_bs}`, `L={arm_len}`.

When importing Python scripts, expressions using `numpy`, `math`, etc. are evaluated server-side and the results become variables.

---

## 7. Running Simulations

**Run** — static (noxaxis). Shows KatScript, PD readouts, CCD images (if Gauss/Cavity is upstream of the CCD).

**Sweep** — parameter scan (xaxis). Select a parameter, set range and steps. Chart.js plots detector outputs vs. the swept parameter. Demodulated detectors (pd1/pd2) show amplitude and phase.

---

## 8. Importing Models

Paste KatScript or an entire Python/Jupyter cell into the import text area and click **Import**.

### Directly from Jupyter

**Copy your whole Jupyter cell** and paste it. The importer handles everything automatically:

- Strips `import`, `print()`, `model.run()`, and non-model code.
- Evaluates Python variables (including `numpy` expressions).
- Parses every `model.parse("""...""")` block into components and connections.
- Preserves `{var}` references in parameters.

You can paste code with multiple `model.parse()` calls, debug prints, or any extra lines — it all works.

### Example 1 — Basic Michelson (mod1)

Paste these KatScript lines:

```
l L0 P=1
s s0 L0.p1 bs1.p1 L=0.5
bs bs1 R=0.5 T=0.5
s s1 bs1.p2 m1.p1 L=3
m m1 R=0.99 T=0.01
s s2 bs1.p3 m2.p1 L=3.001
m m2 R=0.99 T=0.01
s s3 bs1.p4 pd1.p1 L=0.5
pd pd1
```

Light splits at `bs1`, travels to `m1` (3 m) and `m2` (3.001 m), recombines, interference measured at `pd1`.

### Example 2 — With Variables (mod2)

Paste the whole cell:

```python
arm_len = 3.0
delta_len = 0.001
bs_r = 0.5
m_r = 0.99

model.parse("""
l L0 P=1
s s0 L0.p1 bs1.p1 L=0.5
bs bs1 R={bs_r} T=1-{bs_r}
s s1 bs1.p2 m1.p1 L={arm_len}
m m1 R={m_r} T=1-{m_r}
s s2 bs1.p3 m2.p1 L={arm_len+delta_len}
m m2 R={m_r} T=1-{m_r}
s s3 bs1.p4 pd1.p1 L=0.5
pd pd1
""")
```

Vars panel shows `arm_len`, `delta_len`, `bs_r`, `m_r`. Edit any to tune the whole model.

### Example 3 — Computed Variables (mod3)

Arm length computed from wavelength with `numpy`:

```python
import numpy as np

wavelength = 1064e-9
arm_len = int(3.0 / wavelength) * wavelength
bs_angle = np.rad2deg(np.arcsin(0.1))
m_refl = 0.99

model.parse("""
l L0 P=1
s s0 L0.p1 bs1.p1 L=0.5
bs bs1 R={m_refl} T=1-{m_refl} alpha={bs_angle}
s s1 bs1.p2 m1.p1 L={arm_len}
m m1 R={m_refl} T=1-{m_refl}
s s2 bs1.p3 m2.p1 L={arm_len}
m m2 R={m_refl} T=1-{m_refl} phi=90
s s3 bs1.p4 pd1.p1 L=0.5
pd pd1
""")
```

After import: `wavelength = 1.064e-07`, `arm_len` (integer wavelengths near 3 m), `bs_angle` (from `np.rad2deg`), `m_refl = 0.99`. Try sweeping `m2.phi` 0–360 degrees.

---

## 9. Exporting Models

**Export .kat** — plain-text KatScript file. Header lists any auto-renamed spaces.
**Export .ipynb** — ready-to-run Jupyter notebook.

---

## 10. Custom Components

Finesse has many component types beyond the built-in list (`dbs`, `grating`, `squeezer`). Use the **Custom** component:

1. Drag **Custom** (grey "?" icon) onto the canvas and enter the number of ports.
2. In Properties, set **Kat Type** (e.g. `dbs`) and **Name**.
3. Use **Extra param** to add any KatScript parameters.

---

## 11. Saving and Loading

Click **Save**, enter a name. The model (all component positions, angles, connections, variables, and parameters) is saved to the `examples/` folder as a JSON file.

Click **Example** to browse saved models. Click any entry to load it, or the x button to delete.

---

## 12. CCD Imaging

1. Add a **CCD** connected to an optical node.
2. Add a **Gauss** defining beam parameters (`w0`, `z`) upstream of the CCD.
3. Click **Run**, then **View CCD** in the output panel.

The beam profile image opens in a new window.

---

## 13. Jupyter Integration

Click **Jupyter** in the output panel to open a built-in code editor. The current model is available as the `model` variable:

```python
print(model.m1.R)
sol = model.run("noxaxis()")
print(sol['pd1'])
```

---

## 14. Light / Dark Theme

Click the sun/moon icon in the header to toggle the theme.
