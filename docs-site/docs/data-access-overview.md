# 9. Data Access Overview

This document provides comprehensive technical guidance for developers and system integrators who wish to integrate data from Isurlog devices into third-party platforms, such as SCADA, Business Intelligence (BI) tools, or custom applications. The Isurlog platform is designed to be open and flexible, allowing data to be accessed in a manner that best suits the client's needs.

Isurlog provides two primary methods for data access, each designed for a different use case:

### 1. Historical Data via InfluxDB API (Pull Method)

* **Use Case:** Ideal for analytics, reporting, and populating dashboards with past measurements.
* **Mechanism:** This method allows clients to query the database on-demand to retrieve data from any time period.
* **Data Format:** Data provided through the API is already **decoded** and presented in a human-readable format.

### 2. Real-Time Data via MQTT (Push Method)

* **Use Case:** Perfect for live monitoring, immediate alerts, and event-driven applications.
* **Mechanism:** This method provides a continuous stream of data pushed directly from the Isurlog server to a client's systems the moment a new measurement is received.
* **Data Format:** This stream consists of the **raw device payload**, which **requires decoding** on the client's end.
