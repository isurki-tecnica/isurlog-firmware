// ChirpStack payload decoder for ISURLOG (LoRaWAN).
//
// ISURLOG payloads use IsurlogLPP, a variant of Cayenne LPP. Every chunk is:
//
//     channel (1 byte) | type (1 byte) | value (N bytes, big-endian)
//
// See "3.4 Payload Decoding" in the docs for the full format:
// https://docs.isurlog.isurki.com/realtime-data-mqtt/
//
// How to use it: in ChirpStack, open the device profile of your ISURLOGs, go to
// the Codec tab, choose "JavaScript functions" and paste this file.
//
// The decoded values appear in the `object` key of the uplink event, with the
// same field names that IsurDASH stores in InfluxDB (AnalogInput0, DigitalInput1,
// TemperatureSensor0, ...). The reference implementation of the format is
// IsurlogLPP.py, in the same data_integration folder of the firmware repository.

// name:    field name prefix. The channel number is appended to it.
// size:    bytes of the value.
// multipl: the raw integer is divided by this number.
// signed:  two's complement.
// labels:  for chunks that pack several values (accelerometer, GPS): the raw
//          bytes are split in equal parts, and each part gets its label
//          between the name and the channel (AccelerometerX0, AccelerometerY0, ...).
const SENSOR_TYPES = {
    0x00: { name: "DigitalInput",       size: 1, multipl: 1,     signed: false },
    0x01: { name: "DigitalOutput",      size: 1, multipl: 1,     signed: false },
    0x02: { name: "AnalogInput",        size: 2, multipl: 100,   signed: true  },
    0x03: { name: "AnalogOutput",       size: 2, multipl: 100,   signed: true  },
    0x04: { name: "ModbusInput",        size: 2, multipl: 100,   signed: true  },
    0x05: { name: "ModbusGenericInput", size: 2, multipl: 1,     signed: false },
    0x66: { name: "TemperatureInput",   size: 2, multipl: 10,    signed: true  },
    0x67: { name: "TemperatureSensor",  size: 2, multipl: 10,    signed: true  },
    0x68: { name: "HumiditySensor",     size: 1, multipl: 2,     signed: false },
    0x71: { name: "Accelerometer",      size: 6, multipl: 1000,  signed: true,  labels: ["X", "Y", "Z"] },
    0x74: { name: "VoltageInput",       size: 2, multipl: 1,     signed: false },
    0x75: { name: "UnixTime",           size: 4, multipl: 1,     signed: false },
    0x76: { name: "SoCInput",           size: 2, multipl: 10,    signed: false },
    0x77: { name: "CRateInput",         size: 1, multipl: 10,    signed: true  },
    0x78: { name: "ModemData",          size: 1, multipl: 1,     signed: false },
    0x79: { name: "ScriptError",        size: 1, multipl: 1,     signed: false },
    0x88: { name: "GPSData",            size: 9, multipl: 10000, signed: true,  labels: ["Lat", "Lon", "Alt"] }
};

// Reads a big-endian integer. It multiplies instead of shifting bits, because
// JavaScript shifts work on 32-bit signed integers and would turn a 4-byte
// value such as a Unix time (from 2038 on) into a negative number.
function readInteger(bytes, start, size, signed) {
    let value = 0;
    for (let i = 0; i < size; i++) {
        value = value * 256 + bytes[start + i];
    }
    const range = Math.pow(2, size * 8);
    if (signed && value >= range / 2) {
        value -= range;
    }
    return value;
}

function decodeUplink(input) {
    const bytes = input.bytes;
    const decoded = {};
    const warnings = [];

    let i = 0;
    while (i < bytes.length) {
        if (i + 2 > bytes.length) {
            warnings.push("Payload ends in the middle of a chunk header (byte " + i + ")");
            break;
        }
        const channel = bytes[i];
        const type = bytes[i + 1];
        i += 2;

        const sensor = SENSOR_TYPES[type];
        if (!sensor) {
            // The size of an unknown type is not known, so the rest of the
            // payload cannot be read. What was decoded so far is kept.
            warnings.push("Unknown sensor type 0x" + type.toString(16).padStart(2, "0") +
                " on channel " + channel + ". The rest of the payload was not decoded");
            break;
        }
        if (i + sensor.size > bytes.length) {
            warnings.push("Payload too short for " + sensor.name + " on channel " + channel);
            break;
        }

        if (sensor.labels) {
            const partSize = sensor.size / sensor.labels.length;
            for (let k = 0; k < sensor.labels.length; k++) {
                const raw = readInteger(bytes, i + k * partSize, partSize, sensor.signed);
                decoded[sensor.name + sensor.labels[k] + channel] = raw / sensor.multipl;
            }
        } else {
            decoded[sensor.name + channel] = readInteger(bytes, i, sensor.size, sensor.signed) / sensor.multipl;
        }
        i += sensor.size;

        // Kept for existing integrations: the Unix time of the record.
        if (type === 0x75) {
            decoded.extracted_payload_timestamp = decoded[sensor.name + channel];
        }
    }

    const result = { data: decoded };
    if (warnings.length > 0) {
        result.warnings = warnings;
        decoded.error = warnings[0]; // Kept for existing integrations that look for `error`.
    }
    return result;
}
