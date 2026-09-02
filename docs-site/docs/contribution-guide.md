# 7. Contribution Guide

The **ISURLOG** firmware is an open-source project, and we welcome contributions from the community! Whether you are providing a simple bug fix, suggesting a new feature, or optimizing power consumption routines, your help is highly valued.

!!! note "Where does ISURKI's own code actually live?"
    This repository is a **full fork of MicroPython** — the vast majority of the source tree (`py/`, `extmod/`, most of `ports/`, etc.) is upstream MicroPython, kept in sync via the `upstream` remote. ISURKI's own code — the part you'll actually be contributing to in most cases — lives in just two places: **`app/`** (the application, `main.py` + config) and **`ports/esp32/modules/{modules,lib}`** (the wrappers and drivers). See **[2. Architecture Overview](architecture-overview.md)** and **[2.1 Module & Library Reference](module-library-reference.md)** before diving in — they explain the `lib`/`modules` split and document every existing file, so you know where a new sensor driver or feature belongs.

## 7.1 Ways to Contribute

We accept contributions in the following areas:

* **Code Contributions (Pull Requests):** Bug fixes, new sensor drivers, performance optimizations, or new functionalities.
* **Documentation:** Improving the quality, clarity, and completeness of this Wiki or inline comments.
* **Bug Reports:** Submitting clear, detailed reports via the GitHub Issues tracker.
* **Feature Requests:** Suggestions for future functionality or hardware integration, via GitHub Discussions.
* **Hardware (Printables):** Providing new or improved accessories, mounts, or enclosures for the datalogger.

## 7.2 Prerequisites for Code Submission

Before submitting a **Pull Request (PR)**, please ensure you meet the following requirements:

1.  **Environment:** You must use the recommended **Ubuntu/WSL** development environment, as detailed in **1. Build Environment Setup**.
2.  **Code Base:** Your development branch must be forked from and up-to-date with the `main` branch of the official **ISURLOG** repository.
3.  **Code Quality:** Adhere to Python/MicroPython coding standards (e.g., PEP 8 where applicable). Commit messages should follow the project's `CODECONVENTIONS.md` (inherited from upstream MicroPython) — prefix each commit with the directory or file path it affects, e.g. `modules/nb_iot: Fix eDRX timeout handling.`
4.  **Test Locally:** Changes touching hardware-facing code (sensors, power management, communications) must be tested on a physical **ISURLOG** device. Contributions that don't touch hardware at all (e.g. a payload codec fix in `IsurlogLPP.py`, or a pure logic fix) may be reviewed with unit-level testing instead — mention in your PR how you tested it either way.
5.  **License:** By contributing, you agree your code is licensed under the project's **GPL-3.0** license (see `LICENSE`). New files should carry the same copyright header used throughout the codebase:

    ```python
    # Copyright (C) 2026 ISURKI
    #
    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # (at your option) any later version.
    #
    # SPDX-License-Identifier: GPL-3.0-or-later
    ```

## 7.3 The Contribution Process

Follow these steps for a clean and efficient contribution:

### 1. Fork the Repository

Start by forking the main `isurlog-firmware` repository to your personal GitHub account.

### 2. Create a Topic Branch

Create a dedicated branch for your specific fix or feature. This keeps the changes isolated.
```bash
git checkout -b feature/your-awesome-feature

```

### 3. Implement Changes
Commit your changes frequently with descriptive commit messages following `CODECONVENTIONS.md` (e.g., `modules/max31865_sensor: Fix float conversion in PT100 driver.`).

### 4. Create a Pull Request (PR)
1. Push your topic branch to your personal fork on GitHub.
2. Go to the official ISURLOG repository page and initiate a new Pull Request.
3. PR Description: Clearly describe the problem solved or the feature added. Include details on how you tested the change.

## 7.4 Using Issues and Discussions

We use two separate tools depending on how concrete your feedback is:

* **[GitHub Discussions](https://github.com/isurki-tecnica/isurlog-firmware/discussions)** — for open-ended ideas, feature suggestions, hardware/accessory requests, and general questions. Use the **Ideas** category for suggestions ("would X be useful?"), and **Q&A** for support questions. Start here if you're not sure yet whether something belongs in Issues.
* **GitHub Issues** — for confirmed bugs, and for feature requests that are already well-defined and ready to be tracked as actual work:
    * **Bug Reports**: Include clear steps to reproduce the bug, the expected behavior, and the actual behavior observed.
    * **Feature Requests**: Describe the new functionality and why it would be valuable to the ISURLOG community.

## 7.5 Where to Look, Depending on What You Want to Touch

| You want to... | Start here |
| :--- | :--- |
| Understand the codebase layout | **[2. Architecture Overview](architecture-overview.md)** / **[2.1 Module & Library Reference](module-library-reference.md)** |
| Add or fix a sensor driver | **[2.1 Module & Library Reference](module-library-reference.md)** |
| Change a GPIO/hardware assignment | **[4. GPIO Mapping (Hardware-Software)](gpio-mapping.md)** |
| Work on the NB-IoT (nRF9160/nRF9151) modem | **[5. Advanced NB-IoT Modem Guide](nbiot-modem-guide.md)** |
| Work on the LoRaWAN (RAK3172) modem | **[6. Advanced LoRaWAN Modem Guide](lorawan-modem-guide.md)** |
| Flash your build for local testing | **[3. Flashing and Application Upload](flashing-application-upload.md)** |
