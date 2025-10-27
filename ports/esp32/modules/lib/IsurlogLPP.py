from modules import utils

class IsurlogLPPEncoder:
    """
    Encodes data in the Isurlog LPP (LoRaWAN Payload Protocol) format.
    """

    def __init__(self):
        #Sensor types
        self.sensor_types = {
            'addDigitalInput' : {'type':"00", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
            'addDigitalOutput' : {'type':"01", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
            'addAnalogInput' : {'type':"02", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
            'addAnalogOutput' : {'type':"03", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
            'addModbusInput' : {'type':"04", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
            'addModbusGenericInput' : {'type':"05", 'size':2, 'multipl':1, 'signed':False, 'min':0, 'max':65534, 'arrLen':3},
            'addTemperatureInput' : {'type':"66", 'size':2, 'multipl':10, 'signed':True, 'min':-3276.7, 'max':3276.7, 'arrLen':3},
            'addTemperatureSensor' : {'type':"67", 'size':2, 'multipl':10, 'signed':True, 'min':-3276.7, 'max':3276.7, 'arrLen':3},
            'addHumiditySensor' : {'type':"68", 'size':1, 'multipl':2, 'signed':False, 'min':0, 'max':100, 'arrLen':3},
            'addVoltageInput' : {'type':"74", 'size':2, 'multipl':1, 'signed':False, 'min':0, 'max':65534, 'arrLen':3},
            'addUnixTime' : {'type':"75", 'size':4, 'multipl':1, 'signed':False, 'min':0, 'max':4294967295, 'arrLen':3}
        }
        #Configuration types
        self.config_types = {
            'setLatencyTime':               {'type': "A0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 1, 'max': 255},
            'setRtcSync':                 {'type': "A1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setRegisterMode':            {'type': "A2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setRegisterAccumulator':     {'type': "A3", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setMagnetWakeup':            {'type': "A4", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setDebugLED':                {'type': "A5", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setLoRaWANDevEUI':           {'type': "A6", 'size': 8, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFF},
            'setLoRaWANAppEUI':           {'type': "A7", 'size': 8, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFF},
            'setLoRaWANAppKey':           {'type': "A8", 'size': 16, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF},
            'setNB_IoTeDRX':              {'type': "A9", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setAnalogPreAcquisition':    {'type': "AA", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setAnalogInputEnable':       {'type': "AB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setAnalogInputZero':         {'type': "AC", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setAnalogInputFullScale':    {'type': "AD", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setAnalogInputLow':          {'type': "AE", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setAnalogInputHigh':         {'type': "AF", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setAnalogInputLowCond':      {'type': "B0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setAnalogInputHighCond':     {'type': "B1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setDigitalEnable':           {'type': "B2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setDigitalCounter':          {'type': "B3", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setDigitalPulseWeight':      {'type': "B4", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setDigitalWake':             {'type': "B5", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setDigitalLow':              {'type': "B6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setDigitalHigh':             {'type': "B7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setDigitalLowCond':          {'type': "B8", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setDigitalHighCond':         {'type': "B9", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setModbusPreAcquisition':    {'type': "BA", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setModbusInputEnable':       {'type': "BB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setModbusInputSlaveAddress': {'type': "BC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setModbusInputRegisterAddress':{'type': "BD", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setModbusInputFc':           {'type': "BE", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setModbusInputNumberOfDecimals':{'type': "BF", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setModbusInputIsFP':         {'type': "C0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setModbusInputInvert':       {'type': "C1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setModbusInputOffset':       {'type': "C2", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setModbusInputLow':          {'type': "C3", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setModbusInputHigh':         {'type': "C4", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setModbusInputLowCond':      {'type': "C5", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setModbusInputHighCond':     {'type': "C6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setPT100Enable':             {'type': "C7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setPT100Wires':              {'type': "C8", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1}, # Debería ser min:2, max:4 ? Revisar definición
            'setPT100Low':                {'type': "C9", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setPT100High':               {'type': "CA", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setPT100LowCond':            {'type': "CB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setPT100HighCond':           {'type': "CC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setBME680Enable':            {'type': "CD", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setBME680TemperatureLow':    {'type': "CE", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setBME680TemperatureHigh':   {'type': "CF", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setBME680TemperatureLowCond':{'type': "D0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setBME680TemperatureHighCond':{'type': "D1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setBME680HumidityLow':       {'type': "D2", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67}, # Originalmente size:1 multipl:2? Revisar
            'setBME680HumidityHigh':      {'type': "D3", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},# Originalmente size:1 multipl:2? Revisar
            'setBME680HumidityLowCond':   {'type': "D4", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setBME680HumidityHighCond':  {'type': "D5", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            # ----------------- Isurnode Config Types -----------------
            # -- Isurnode General --
            'setIsurnodeEnable': {'type': "D6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeSlaveAddress': {'type': "D7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},

            # -- Isurnode Analog Config --
            'setIsurnodeAnalogPreAcquisition': {'type': "D8", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setIsurnodeAnalogTriggerAddress': {'type': "D9", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setIsurnodeAnalogInputEnable': {'type': "DA", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeAnalogInputZero': {'type': "DB", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeAnalogInputFullScale': {'type': "DC", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeAnalogInputLow': {'type': "DD", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeAnalogInputHigh': {'type': "DE", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeAnalogInputLowCond': {'type': "DF", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeAnalogInputHighCond': {'type': "E0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeAnalogInputAddress': {'type': "E1", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},

            # -- Isurnode SHT30 Sensor --
            'setIsurnodeSHT30Enable': {'type': "E2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeSHT30TriggerAddress': {'type': "E3", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setIsurnodeSHT30Address': {'type': "E4", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setIsurnodeSHT30TempLow': {'type': "E5", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeSHT30TempHigh': {'type': "E6", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeSHT30TempLowCond': {'type': "E7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeSHT30TempHighCond': {'type': "E8", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeSHT30HumLow': {'type': "E9", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeSHT30HumHigh': {'type': "EA", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeSHT30HumLowCond': {'type': "EB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeSHT30HumHighCond': {'type': "EC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},

            # -- Isurnode Digital Outputs --
            'setIsurnodeDigitalOutputEnable': {'type': "ED", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeDigitalOutputType': {'type': "EE", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigitalOutputAddress': {'type': "EF", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            'setIsurnodeDigitalOutputLogicOp': {'type': "F0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigitalOutputRetry': {'type': "FB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigitalOutputRetrySleep': {'type': "FC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigitalOutputOnTime': {'type': "FD", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535},
            # (First )
            'setIsurnodeDigOutCond1Sensor': {'type': "F1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigOutCond1Low': {'type': "F2", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeDigOutCond1High': {'type': "F3", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeDigOutCond1LowCond': {'type': "F4", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeDigOutCond1HighCond': {'type': "F5", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            # (Second output condition)
            'setIsurnodeDigOutCond2Sensor': {'type': "F6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
            'setIsurnodeDigOutCond2Low': {'type': "F7", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeDigOutCond2High': {'type': "F8", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67},
            'setIsurnodeDigOutCond2LowCond': {'type': "F9", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            'setIsurnodeDigOutCond2HighCond': {'type': "FA", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1},
            
            'setModbusInputLongInt': {'type': "FE", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1}
        }
        
    def encode(self, lpp):
        """
        Encodes a list of sensor data into a hexadecimal Isurlog LPP payload.

        Args:
            lpp_data: A list of lists.  Each inner list represents a sensor reading
                      and should be in the format: [channel, sensor_type, value1, value2, ...].
                      'channel' is an integer (0-255).
                      'sensor_type' is a string key from the sensor_types dictionary.
                      'value1', 'value2', ... are the sensor readings (int or float).

        Returns:
            A string representing the hexadecimal payload, or an empty string if an error occurred.
            
        Usage:
        
            encoder = IsurlogLPPEncoder()

            # Example data (list of lists)
            data = [
                [1, "addTemperatureSensor", 25.5],  # Channel 1, Temperature, 25.5 degrees
                [2, "addHumiditySensor", 60.2],    # Channel 2, Humidity, 60.2%
                [3, "addAnalogInput", 1.234],     # Channel 3, Analog Input, 1.234V
                [4, "addVoltageInput", 12345],  # channel 4, Voltage input, 12345mv
                [5, "addDigitalInput", 1],       # channel 5, Digital Input
            ]

            encoded_payload = encoder.encode(data)

            if encoded_payload:
                print(f"Encoded Payload: {encoded_payload}")
            else:
                print("Encoding failed.")
        """
        
        payload = ""
        onePayload = ""

        for i in range(0,len(lpp)):
            sensorInfo = self.sensor_types.get(lpp[i][1])

            if sensorInfo == None:
                utils.log_error("Unknown type " + str(lpp[i][1]) + " in channel " + str(lpp[i][0]) + ".")
                continue

            if len(lpp[i]) != sensorInfo.get("arrLen"):
                utils.log_error("Too few/many values in channel " + str(lpp[i][0]) + " of the type " + str(lpp[i][1]))

            else:
                try:
                    onePayload += str(f'{lpp[i][0]:02x}')    # channel
                except:
                    utils.log_error("The channel number is in the wrong format!")
                    continue

                onePayload += sensorInfo.get("type")          # sensor type

                for j in range(2,len(lpp[i])):
                    error = False
                    value = lpp[i][j]

                    if type(value) != int and type(value) != float:
                        utils.log_error("The value in channel " + str(lpp[i][0]) + " of the type " + lpp[i][1] + " is not a number.")
                        error = True
                        break

                    if not (value >= sensorInfo.get("min") and value <= sensorInfo.get("max")):
                        utils.log_error("Value " + str(value) + " in channel " + str(lpp[i][0]) + " of the type " + lpp[i][1] + " is outside the " + str(sensorInfo.get("min")) + " - " + str(sensorInfo.get("max")) + " range!")
                        error = True
                        break
                    valueConversion = int(value * sensorInfo.get("multipl"))

                    # Signed conversion
                    sign = False

                    if value < 0:
                        sign = True

                    if sensorInfo.get("signed") & sign:
                        valueConversion = valueConversion & 0xFFFF

                    # Size
                    if sensorInfo.get("size") == 1:
                        onePayload += str(f'{valueConversion:02x}')[-2:]
                    elif sensorInfo.get("size") == 2:
                        onePayload += str(f'{valueConversion:04x}')[-4:]
                    elif sensorInfo.get("size") == 4:
                        onePayload += str(f'{valueConversion:08x}')[-8:]
                    elif sensorInfo.get("size") == 6:
                        onePayload += str(f'{valueConversion:04x}')[-4:]
                    elif sensorInfo.get("size") == 9:
                        onePayload += str(f'{valueConversion:06x}')[-6:]

                if error == False:
                    payload += onePayload
                    onePayload = ""
                else:
                    onePayload = ""

        return payload
    

    def decode(self, payload):
        """
        Decodes an Isurlog LPP hexadecimal payload.  Handles both sensor data
        and configuration updates.

        Args:
            payload: The hexadecimal payload string.

        Returns:
            A list of dictionaries.  Each dictionary represent a decoded value
        """
        data = []
        i = 0
        while i < len(payload):
            try:
                channel = int(payload[i:i+2], 16)  # Obtiene el canal
                i += 2
                sensor_type_hex = payload[i:i+2] #Obtiene el tipo
                i += 2

                sensor_type = None #Busca el tipo en base al type
                for name, info in self.config_types.items():
                    if info['type'] == sensor_type_hex:
                        sensor_type = name
                        sensor_info = info
                        break

                if sensor_type is None:
                    utils.log_error(f"Unknown sensor type: {sensor_type_hex}")
                    # Ignorar el dato desconocido y continuar (recomendado)
                    raise ValueError(f"Unknown sensor type: {sensor_type_hex}")


                size = sensor_info['size']
                value_hex = payload[i:i + size * 2]
                i += size * 2

                # Conversión del valor
                value_int = int(value_hex, 16)
                utils.log_info(f"Decoded data 0: {value_int}")
                if sensor_info['signed']:  #Comprobar si es signed
                    # Convertir a entero con signo (complemento a 2)
                    max_val = 2**(size * 8)
                    if value_int >= max_val // 2:
                        value_int -= max_val

                if sensor_info['multipl'] != 1:
                    value_int = value_int / sensor_info['multipl']

                data.append({'channel': channel, 'name': sensor_type, 'value': value_int})
                utils.log_info(f"Decoded data: {data}")
            except Exception as e:
                utils.log_error(f"Error decoding payload at index {i} -->{payload[i:i+2]}error:{e}")
                break #Detener

        return data

