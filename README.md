# Finesse-visualization

> Drag-and-drop optical interferometer designer with Finesse 3 simulation engine.

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10-green)](https://www.python.org/)

This project is built upon [Finesse 3](https://finesse.ifosim.org/), which is licensed under GPLv3 ([repo](https://gitlab.com/ifosim/finesse/finesse3)).
Code generated with LLM assistance (DeepSeek, Claude) under human direction.

---

## Quick Start

**Prerequisites:** Windows 10/11, [Miniconda](https://docs.conda.io/en/latest/miniconda.html)/[Anaconda](https://www.anaconda.com/download).

```bash
#Windows
setup.bat    # Create conda env "finesse_sim" and install dependencies (one time)
run.bat      # Launch — browser opens at http://localhost:5000
```
```bash
#MacOS
bash setup.sh    # Create conda env "finesse_sim" and install dependencies (one time)
bash run.sh      # Launch — browser opens at http://localhost:5000
```

---

## Features

- **Visual layout** with 12 component types (laser, mirror, beamsplitter, lens, modulator, isolator, detector, CCD, cavity, gauss, custom)
- **KatScript generation** for Finesse 3 in real time
- **Variables** with Python expressions and `numpy`
- **Import** entire Jupyter cells — auto-extracts variables and KatScript blocks
- **Simulation** — `noxaxis` and `xaxis` parameter sweeps with Chart.js
- **Export** to `.kat`, `.ipynb`, and JSON
- Light / dark theme

---

## Documentation

See [USER_MANUAL.pdf](USER_MANUAL.pdf) for the full guide with three Michelson interferometer examples.

---

## Dependencies

| Package | Use | License |
|---------|-----|---------|
| [Finesse 3](https://finesse.ifosim.org/) | Simulation engine | GPLv3 |
| [Flask](https://flask.palletsprojects.com/) | Web server | BSD |
| [NumPy](https://numpy.org/) | Numerical computation | BSD |
| [PlaneGCS](https://github.com/salusoft89/planegcs) | Constraint solver | MIT |
| [Chart.js](https://www.chartjs.org/) | Plotting (CDN) | MIT |

---

## License

GPLv3 — see [LICENSE](LICENSE).

This project uses [Finesse 3](https://gitlab.com/ifosim/finesse/finesse3) (GPLv3).
