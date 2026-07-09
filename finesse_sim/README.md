# Finesse3 Optics Simulator

> Drag-and-drop optical interferometer designer for [Finesse 3](https://finesse.ifosim.org/). Paste a Jupyter cell, click Run — done.

[![License: GPLv3](https://img.shields.io/badge/license-GPLv3-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12-green)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey)]()

**Built on [Finesse 3](https://gitlab.com/ifosim/finesse/finesse3) (GPLv3) by the LIGO Scientific Collaboration & Nikhef.**
_Code generated with LLM assistance (DeepSeek, Claude) under human direction._

**Install:** `setup.bat` / `bash setup.sh` → **Run:** `run.bat` / `bash run.sh` → open `http://localhost:5000`

---

## Quick Start

### Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) (Windows or macOS)
- A dedicated `finesse_sim` conda environment (finesse 3.x + flask), created automatically by `setup.bat`. **Do NOT use the `finesse` env** — it does not have flask installed, and the app will fail to start.

### Install & Launch

**Windows — double-click or run in terminal:**

```bash
setup.bat          # Install everything (one time)
run.bat            # Launch — opens http://localhost:5000
```

**macOS — open Terminal and run:**

```bash
bash setup.sh      # Install everything (one time)
bash run.sh        # Launch — opens http://localhost:5000
```

If port 5000 is in use, the next available port is selected automatically.

---

## Features

- **Visual layout** — 12 component types: laser, mirror, beamsplitter, lens, modulator, isolator, photodetector, CCD, cavity, gauss, amplitude detector, and custom KatScript components
- **KatScript generation** — real-time Finesse 3 script preview
- **Variables & expressions** — define Python variables with `numpy`, reference them in parameters with `{var}` syntax
- **Import from Jupyter** — paste entire notebook cells; the importer strips non-model code, evaluates Python variables, and parses KatScript blocks automatically
- **Simulation** — static (`noxaxis`) and parameter sweep (`xaxis`) with Chart.js plots
- **Export** — `.kat`, `.ipynb` (Jupyter notebook), and JSON state files
- **Light / dark theme**

Full documentation: [USER_MANUAL.pdf](USER_MANUAL.pdf) (3 Michelson interferometer examples included).

---

## Acknowledgements

This project is built on **[Finesse 3](https://finesse.ifosim.org/)** ([repo](https://gitlab.com/ifosim/finesse/finesse3)), the frequency-domain interferometer simulation engine developed by the LIGO Scientific Collaboration and maintained by the Finesse team at Nikhef. Finesse 3 is licensed under GPLv3.

The majority of the source code in this repository was generated with the assistance of large language models (LLMs), including DeepSeek and Claude, under human direction and review.

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

GPLv3 — see [LICENSE](LICENSE). This project uses [Finesse 3](https://gitlab.com/ifosim/finesse/finesse3) (also GPLv3).
