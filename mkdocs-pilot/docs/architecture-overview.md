# 2. Architecture Overview

For application development and to maximize the use of the **ISURLOG** hardware capabilities, a reference software base developed in MicroPython is provided. This software is open source and available on the GitHub repository.

The main objective of this software structure is to provide the necessary tools to interact with all integrated circuits (ICs) and peripherals of the **ISURLOG**, as well as offering a functional example template of a typical datalogger application.

## 2.1 The Modular Software Structure

The repository software presents a modular structure designed for flexible and easy use, based on the following key components:

### 1. The `/lib` Folder (Base Libraries)

* **Low-Level Drivers:** Contains MicroPython libraries to directly control the different ICs present on the **ISURLOG** board (sensors, communication modem, RTC, etc.).
* **Direct Hardware Management:** These libraries handle direct communication with the hardware (e.g., via I2C, SPI, UART).
* **Third-Party Libraries:** Can include third-party libraries developed specifically for the **ISURLOG** or adapted for it.

### 2. The `/modules` Folder (High-Level Wrappers)

* **Abstraction Layer:** Acts as an abstraction layer over the libraries in the `/lib` folder.
* **Purpose:** These modules (or 'wrappers') simplify the use of hardware functionalities, offering more intuitive interfaces and reducing the amount of necessary application code.

### 3. The `main.py` File (Application Entry Point)

This is the main script that runs on the ESP32. The provided `main.py` is pre-configured to implement a complete and functional datalogger application.

A typical example of this entry point handles the following tasks:

* Initialize sensors and peripherals.
* Read connected sensor data.
* Format the data.
* Establish cloud connection using LoRaWAN or NB-IoT.
* Send data to a LoRaWAN server or an MQTT broker (in the case of NB-IoT).
* Receive new configurations.
* Handle power management.

## 2.2 Compatibility and Adaptability

The software has been designed with adaptability in mind:

### Configuration via JSON

The easiest way to configure the datalogger is by setting the parameters in `dynamic_config.json`. This covers the majority of common use cases.

### Code Modification

For fully customized or highly specific operational logic that cannot be handled solely with JSON configuration, users always have the option to directly modify the `main.py` file or include their modules in the `/modules` folder. As the code is open source, users have total freedom to adapt the code to the exact requirements of each application.

## 2.3 Looking for a specific module?

For a per-file breakdown of every module in `/modules` and driver in `/lib` — purpose, public API, dependencies, and which config keys each one reads — see **[2.1 Module & Library Reference](module-library-reference.md)**.
