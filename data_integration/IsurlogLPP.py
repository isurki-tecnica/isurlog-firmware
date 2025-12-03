import ctypes
import sys

sensor_types = {
    'addDigitalInput' : {'type':"00", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
    'addDigitalOutput' : {'type':"01", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
    'addAnalogInput' : {'type':"02", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
    'addAnalogOutput' : {'type':"03", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
    'addModbusInput' : {'type':"04", 'size':2, 'multipl':100, 'signed':True, 'min':-327.67, 'max':327.67, 'arrLen':3},
    'addModbusGenericInput' : {'type':"05", 'size':2, 'multipl':1, 'signed':False, 'min':0, 'max':65534, 'arrLen':3},
    'addTemperatureInput' : {'type':"66", 'size':2, 'multipl':10, 'signed':True, 'min':-3276.7, 'max':3276.7, 'arrLen':3},
    'addTemperatureSensor' : {'type':"67", 'size':2, 'multipl':10, 'signed':True, 'min':-3276.7, 'max':3276.7, 'arrLen':3},
    'addHumiditySensor' : {'type':"68", 'size':1, 'multipl':2, 'signed':False, 'min':0, 'max':100, 'arrLen':3}, #'max':127.5
    'addVoltageInput' : {'type':"74", 'size':2, 'multipl':1, 'signed':False, 'min':0, 'max':65534, 'arrLen':3},
    'addUnixTime' : {'type':"75", 'size':4, 'multipl':1, 'signed':False, 'min':0, 'max':4294967295, 'arrLen':3}
}

config_types = {
    'setLatencyTime':    {'type': "F0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 1, 'max': 255, 'arrLen':3},
    'setRtcSync':        {'type': "F1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setRegisterMode':   {'type': "F2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setRegisterAccumulator': {'type': "F3", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255, 'arrLen':3},
    'setMagnetWakeup':   {'type': "F4", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setLoRaWANDevEUI': {'type': "F5", 'size': 8, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFF, 'arrLen':3},
    'setLoRaWANAppEUI': {'type': "F6", 'size': 8, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFF, 'arrLen':3},
    'setLoRaWANAppKey': {'type': "F7", 'size': 16, 'multipl': 1, 'signed': False, 'min': 0, 'max': 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF, 'arrLen':3},
    'setNB_IoTeDRX':     {'type': "F8", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setAnalogPreAcquisition': {'type': "F9", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535, 'arrLen':3},
    'setAnalogInputEnable':    {'type': "FA", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setAnalogInputZero':      {'type': "FB", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setAnalogInputFullScale': {'type': "FC", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setAnalogInputLow':       {'type': "FD", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setAnalogInputHigh':      {'type': "FE", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setAnalogInputLowCond':   {'type': "FF", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setAnalogInputHighCond':  {'type': "E0", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setDigitalEnable':   {'type': "E1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setDigitalCounter':  {'type': "E2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setDigitalPulseWeight': {'type':"E3", 'size': 1, 'multipl':1, 'signed':False, 'min': 0, 'max': 255, 'arrLen':3},
    'setDigitalWake' : {'type':"E4", 'size': 1, 'multipl':1, 'signed':False, 'min': 0, 'max':255, 'arrLen':3},
    'setDigitalLow' : {'type': "E5", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
    'setDigitalHigh' : {'type': "E6", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':255, 'arrLen':3},
    'setDigitalLowCond' : {'type': "E7", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':1, 'arrLen':3},
    'setDigitalHighCond' : {'type': "E8", 'size':1, 'multipl':1, 'signed':False, 'min':0, 'max':1, 'arrLen':3},
    'setModbusPreAcquisition': {'type': "EA", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535, 'arrLen':3},
    'setModbusInputEnable': {'type': "EB", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setModbusInputSlaveAddress': {'type': "EC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255, 'arrLen':3},
    'setModbusInputRegisterAddress': {'type': "ED", 'size': 2, 'multipl': 1, 'signed': False, 'min': 0, 'max': 65535, 'arrLen':3},
    'setModbusInputFc': {'type': "EE", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255, 'arrLen':3},
    'setModbusInputNumberOfDecimals': {'type': "EF", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 255},
    'setModbusInputIsFP': {'type': "F1", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setModbusInputInvert': {'type': "F2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setModbusInputOffset': {'type': "F3", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setModbusInputLow': {'type': "F4", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setModbusInputHigh': {'type': "F5", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setModbusInputLowCond': {'type': "F6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setModbusInputHighCond': {'type': "F7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1}, 'arrLen':3,
    'setPT100Enable':   {'type': "F8", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setPT100Wires':   {'type': "F9", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setPT100Low': {'type': "FA", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setPT100High': {'type': "FB", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setPT100LowCond': {'type': "FC", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setPT100HighCond': {'type': "FD", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setBME680Enable':   {'type': "FE", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setBME680TemperatureLow': {'type': "FF", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setBME680Tempe ratureHigh': {'type': "E1", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setBME680TemperatureLowCond': {'type': "E2", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setBME680TemperatureHighCond': {'type': "E3", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setBME680HumidityLow': {'type': "E4", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setBME680HumidityHigh': {'type': "E5", 'size': 2, 'multipl': 100, 'signed': True, 'min': -327.68, 'max': 327.67, 'arrLen':3},
    'setBME680HumidityLowCond': {'type': "E6", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3},
    'setBME680HumidityHighCond': {'type': "E7", 'size': 1, 'multipl': 1, 'signed': False, 'min': 0, 'max': 1, 'arrLen':3}

}

def encodeIsurlogLPP(lpp):
    # (Tu función encodeIsurlogLPP original, sin cambios)
    payload = ""
    onePayload = ""

    for i in range(0,len(lpp)):
        sensorInfo = sensor_types.get(lpp[i][1])

        if sensorInfo == None:
            print("Unknown type " + str(lpp[i][1]) + " in channel " + str(lpp[i][0]) + ".")
            continue

        if len(lpp[i]) != sensorInfo.get("arrLen"):
            print("Too few/many values in channel " + str(lpp[i][0]) + " of the type " + str(lpp[i][1]))

        else:
            try:
                onePayload += str(f'{lpp[i][0]:02x}')    # channel
            except:
                print("The channel number is in the wrong format!")
                continue

            onePayload += sensorInfo.get("type")          # sensor type

            for j in range(2,len(lpp[i])):
                error = False
                value = lpp[i][j]

                if type(value) != int and type(value) != float:
                    print("The value in channel " + str(lpp[i][0]) + " of the type " + lpp[i][1] + " is not a number.")
                    error = True
                    break

                if not (value >= sensorInfo.get("min") and value <= sensorInfo.get("max")):
                    print("Value " + str(value) + " in channel " + str(lpp[i][0]) + " of the type " + lpp[i][1] + " is outside the " + str(sensorInfo.get("min")) + " - " + str(sensorInfo.get("max")) + " range!")
                    error = True
                    break
                valueConversion = int(value * sensorInfo.get("multipl"))

                # Signed conversion
                sign = False

                if value < 0:
                    sign = True

                if sensorInfo.get("signed") & sign:
                    valueConversion = ctypes.c_uint16(valueConversion).value

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


def decodeIsurlogLPP(payload):
    """Decodes a simplified CayenneLPP payload (IsurlogLPP format)."""
    data = []
    i = 0
    while i < len(payload):
        try:
            channel = int(payload[i:i+2], 16)  # Obtiene el canal
            i += 2
            sensor_type_hex = payload[i:i+2] #Obtiene el tipo
            i += 2

            sensor_type = None #Busca el tipo en base al type
            for name, info in sensor_types.items():
                if info['type'] == sensor_type_hex:
                    sensor_type = name
                    sensor_info = info
                    break

            if sensor_type is None:
                print(f"Unknown sensor type: {sensor_type_hex}")
                # Opción 1:  Ignorar el dato desconocido y continuar (recomendado)
                #i += sensor_info['size'] * 2  # Avanzar al siguiente dato (si supiéramos el tamaño)
                #continue
                # Opción 2:  Detener el decodificado si encontramos un tipo desconocido
                raise ValueError(f"Unknown sensor type: {sensor_type_hex}")


            size = sensor_info['size']
            value_hex = payload[i:i + size * 2]
            i += size * 2

            # Conversión del valor
            value_int = int(value_hex, 16)
            if sensor_info['signed']:  #Comprobar si es signed
                # Convertir a entero con signo (complemento a 2)
                max_val = 2**(size * 8)
                if value_int >= max_val // 2:
                    value_int -= max_val

            value = value_int / sensor_info['multipl']

            data.append({'channel': channel, 'name': sensor_type, 'value': value})
            print(f"Decoded data: {data}", file = sys.stderr)
        except Exception as e:
            print(f"Error decoding payload at index {i}: {e}", file = sys.stderr)
            # Considerar si quieres continuar o detenerte aquí.  Si continúas,
            # podrías perder datos.  Es mejor detenerse si el formato es crítico.
            break #Detener

    return data

