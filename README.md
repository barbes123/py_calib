# py_calib

Python-based calibration toolkit for radiation detector systems used in nuclear spectroscopy experiments.

## Overview

`py_calib` provides automatic calibration and validation utilities for multi-detector experimental setups.  
It is designed to support detector response correction and preparation of calibrated datasets for downstream physics analysis.

The toolkit is used together with the broader ELIADE analysis framework and supports workflows involving:

- Energy calibration of detector channels
- Time calibration and alignment
- Update and management of lookup tables (LUTs)
- Batch calibration workflows
- Validation of calibration stability and detector response

---

## Physics Context

The package is intended for calibration of heterogeneous detector arrays used in nuclear physics experiments, including gamma-ray, neutron, and charged-particle systems.

Typical challenges addressed include:

- Matching measured detector response to known calibration references
- Correcting gain drifts and channel-to-channel offsets
- Time alignment across multiple acquisition channels
- Maintaining reproducible calibration parameters for experimental campaigns

---

## Main Components

- `py_calib.py` → main calibration workflow
- `py_calib_batch.py` → batch processing of calibration tasks
- `update_json.py` → update and maintenance of run/configuration metadata
- `py_addback.py`, `py_addback_ener.py` → addback-related analysis utilities
- `json/` → experiment metadata
- `tools/`, `utils/`, `lib/` → helper scripts and shared functionality

---

## Methodology

### 1. Input Preparation
- Load detector spectra and metadata
- Select relevant run information and configuration files
- Attach lookup tables for the detector setup under study

### 2. Calibration
- Identify reference peaks
- Fit calibration points and determine correction parameters
- Apply energy and time corrections

### 3. Validation
- Check peak positions after calibration
- Evaluate channel-to-channel consistency
- Monitor calibration stability across runs

---

## Example Use Cases

- Calibration of HPGe and associated detector channels
- Batch processing of multiple calibration runs
- Updating experiment metadata and lookup tables
- Preparing calibrated inputs for event sorting and physics analysis

---

## Repository Role in the Full Workflow

This repository is part of a larger analysis ecosystem:

- [EliadeSorting](https://github.com/barbes123/EliadeSorting) → event building and sorting
- [py_calib](https://github.com/barbes123/py_calib) → calibration workflows
- [EliadeManual](https://github.com/barbes123/EliadeManual) → detailed documentation and user instructions

---

## Requirements

Typical dependencies include:

- Python 3.x
- NumPy
- SciPy
- JSON-based configuration files
- CERN ROOT (where applicable in the wider workflow)

---

## Documentation

Detailed setup, experiment-specific instructions, and operational procedures are maintained in:

👉 [EliadeManual wiki](https://github.com/barbes123/EliadeManual/wiki)

---

## Notes

This repository reflects real experimental calibration workflows and may include setup-specific configuration dependencies.

---

## Author

Dmitry Testov  
