# 5. LoRaWAN with Your Own ChirpStack Server

The LoRaWAN version of the ISURLOG works with a standard LoRaWAN network server: it joins with OTAA, uses the 868 MHz band and runs as a Class A device (see [Technical Specifications](technical-specifications.md)). So you can run your own gateways and your own server, and keep your LoRaWAN network open and under your control.

This page explains how to do it with **ChirpStack**, an open-source LoRaWAN network server.

## 5.1 What You Need

* An **ISURLOG with the LoRaWAN module** (868 MHz).
* A **LoRaWAN gateway** for the EU868 band, connected to your ChirpStack server.
* **ChirpStack v4**. For the installation of the server and the gateway bridge, follow the [official ChirpStack documentation](https://www.chirpstack.io/docs/).

## 5.2 Device Profile

Create a device profile for the ISURLOG in ChirpStack:

* **Region:** EU868.
* **Activation:** OTAA.
* **Class:** A or B are recommended for battery-powered devices. Class A is the most power-efficient and gives the maximum battery life; Class B is not optimal for maximum battery life, and ISURKI has not tested it. Class C is only recommended where the ISURLOG has external power, since it keeps the radio listening all the time.
* **ADR:** enabled, so the device does not transmit with more power or a lower data rate than the link needs.

See [LoRaWAN-specific: device class and ADR](troubleshooting.md) in the troubleshooting page for the reasons.

## 5.3 Payload Decoder

The ISURLOG sends its readings in a compact binary format (see [3.4 Payload Decoding](realtime-data-mqtt.md#34-payload-decoding-nb-iotcayenne-lpp)). ChirpStack turns it into readable values with a decoder.

1. Download the decoder: [`IsurlogLPP_Decoder.js`](https://github.com/isurki-tecnica/isurlog-firmware/blob/main/data_integration/chirpstack/IsurlogLPP_Decoder.js).
2. In ChirpStack, open the **device profile** of your ISURLOGs, go to the **Codec** tab and choose **JavaScript functions**.
3. Paste the content of the file and save.

From then on, every uplink event includes the decoded values in the `object` key:

```json
"object": {
  "AnalogInput0": -0.99,
  "DigitalInput0": 0,
  "HumiditySensor0": 67.5,
  "TemperatureSensor0": 24.7,
  "UnixTime0": 1757953501,
  "VoltageInput0": 4071,
  "extracted_payload_timestamp": 1757953501
}
```

* **Field names** are the type of the reading followed by its channel, and they are the same names that IsurDASH stores in InfluxDB (see [2.4 Data Schema](historical-data-influxdb.md)). For example, an accelerometer reading produces `AccelerometerX0`, `AccelerometerY0` and `AccelerometerZ0`.
* **Time of the reading:** `UnixTime0` is the time the ISURLOG took the reading, in seconds since 1970 (UTC). `extracted_payload_timestamp` repeats it.
* **Unknown data:** if a payload contains a data type the decoder does not know, it keeps what it decoded up to that point and adds a `warnings` list to the result, and an `error` field to the `object`.

## 5.4 Register the Device

Create an application in ChirpStack and add each ISURLOG as a device with its LoRaWAN credentials. Use the **DEV EUI**, **APP EUI** and **APP KEY** that are configured on the device (see the [LoRaWAN parameters](reference-parameters.md#lorawan)), and assign the device profile of the previous step.

When the ISURLOG powers on, it joins the network and starts sending.

## 5.5 Getting the Data Out

ChirpStack publishes every uplink on its MQTT integration, in the topic `application/{application-id}/device/{device_eui}/event/up`. The format is described in [3.3.1 LoRaWAN Devices (via ChirpStack)](realtime-data-mqtt.md#331-lorawan-devices-via-chirpstack).

## 5.6 Connecting Your Server to IsurDASH

Your ChirpStack server can be connected to **IsurDASH**, our free platform for viewing and configuring dataloggers. You keep your own network and your own gateways, and you also get the dashboards, alarms and remote configuration of IsurDASH (see [6. IsurDASH Platform](isurdash-platform.md)).

This connection is set up by ISURKI. [Contact us](mailto:tecnica@isurki.com?subject=ISURLOG%20LoRaWAN%20-%20Connect%20my%20ChirpStack%20server) and we will arrange it with you.

## 5.7 Using the Data in a SCADA

The readings that reach IsurDASH are stored in InfluxDB, in a bucket of your own, with a private read-only token. Any SCADA or application that can make HTTP requests can read them with a Flux query. See [2. Historical Data (InfluxDB)](historical-data-influxdb.md), including the reference implementation with a working query, for the connection parameters and field names.

If you prefer to get the data in real time, subscribe to the MQTT integration of your ChirpStack server (see [5.5](#55-getting-the-data-out)).
