
import socket
import json
import random
import time
import struct
import base64

# --- CONFIGURACIÓN ---
HOST = 'localhost'
PORT = 65432
SENSOR_ID = "TEMP-HUM-01"
TIEMPO_ENTRE_ENVIOS = 5  # Segundos
LECTURAS_POR_LOTE = 5    # Enviaremos 5 lecturas a la vez

# --- DEFINICIÓN DEL PROTOCOLO BINARIO INTERNO ---
# > : Big-Endian (Network Byte Order)
# d : Double (8 bytes) para el timestamp
# f : Float (4 bytes) para temperatura y humedad
FORMATO_LECTURA = '>dff'

def simular_lectura():
    """Simula una lectura de sensor y devuelve (timestamp, temperatura, humedad)."""
    timestamp = time.time()
    temperatura = 22.5 + random.uniform(-1.5, 1.5)
    humedad = 45.0 + random.uniform(-5.0, 5.0)
    return timestamp, temperatura, humedad

def run_cliente():
    print(f"--- Sensor con Payload Binario ({SENSOR_ID}) ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Intentando conectar al Data Logger en {HOST}:{PORT}...")
            client_socket.connect((HOST, PORT))
            print("¡Conexión establecida!")

            while True:
                payload_binario = b""
                print(f"\nGenerando un lote de {LECTURAS_POR_LOTE} lecturas...")

                # 1. GENERAR Y EMPAQUETAR UN LOTE DE LECTURAS
                for _ in range(LECTURAS_POR_LOTE):
                    timestamp, temperatura, humedad = simular_lectura()
                    payload_binario += struct.pack(FORMATO_LECTURA, timestamp, temperatura, humedad)

                # 2. CODIFICAR EL PAYLOAD BINARIO A BASE64
                payload_b64 = base64.b64encode(payload_binario).decode('ascii')
                print(f"Payload binario de {len(payload_binario)} bytes codificado a Base64.")

                # 3. CREAR EL OBJETO JSON CONTENEDOR
                data_container = {
                    "sensor_id": SENSOR_ID,
                    "timestamp_envio": time.time(),
                    "payload_b64": payload_b64
                }

                # 4. SERIALIZAR A JSON Y ENVIAR
                mensaje_json = json.dumps(data_container)
                client_socket.sendall(mensaje_json.encode('utf-8') + b'\n')
                print("Contenedor JSON con payload binario enviado.")

                time.sleep(TIEMPO_ENTRE_ENVIOS)

    except ConnectionRefusedError:
        print("Error: Conexión rechazada. Asegúrate de que el Data Logger está en marcha.")
    except KeyboardInterrupt:
        print("\nSensor detenido por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == '__main__':
    run_cliente()
