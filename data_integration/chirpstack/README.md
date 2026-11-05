# ISURLOG decoder for ChirpStack

`IsurlogLPP_Decoder.js` turns the binary payloads of an ISURLOG (LoRaWAN) into readable values inside ChirpStack.

To use it, paste the file in the **Codec** tab (JavaScript functions) of the device profile of your ISURLOGs. The full guide is in the wiki: [5. LoRaWAN with Your Own ChirpStack Server](https://docs.isurlog.isurki.com/chirpstack-integration/).

The format it reads is described in [3.4 Payload Decoding](https://docs.isurlog.isurki.com/realtime-data-mqtt/), and [`IsurlogLPP.py`](../IsurlogLPP.py) is its reference implementation. The decoder was checked against that implementation with payloads of every data type, including values that need more than 32 bits.
