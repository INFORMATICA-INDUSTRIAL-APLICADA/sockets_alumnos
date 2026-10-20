import json
import random
import socket
import time
from typing import Any

# --- CONFIGURACIÓN ---
HOST = 'localhost'
PORT = 65432
SENSOR_ID = "TEMP-HUM-01"
TIEMPO_ENTRE_ENVIOS = 5  # Segundos
LECTURAS_POR_LOTE = 5    # Enviaremos 5 lecturas a la vez


def simular_lectura() -> dict[str, float]:
    """Simula una lectura de sensor y devuelve un diccionario con sus valores."""
    return {
        "timestamp": round(time.time(), 4),
        "temperatura_c": round(22.5 + random.uniform(-1.5, 1.5), 2),
        "humedad_rel": round(45.0 + random.uniform(-5.0, 5.0), 2),
    }


def run_cliente() -> None:
    print(f"--- Sensor con Protocolo JSON ({SENSOR_ID}) ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Intentando conectar al Data Logger en {HOST}:{PORT}...")
            client_socket.connect((HOST, PORT))
            print("¡Conexión establecida!")

            while True:
                print(f"\nGenerando un lote de {LECTURAS_POR_LOTE} lecturas...")

                # 1. GENERAR UN LOTE DE LECTURAS COMO DICCIONARIOS DE PYTHON
                lecturas_lote: list[dict[str, float]] = [
                    simular_lectura() for _ in range(LECTURAS_POR_LOTE)
                ]

                # 2. CREAR EL OBJETO JSON CONTENEDOR
                data_container: dict[str, Any] = {
                    "sensor_id": SENSOR_ID,
                    "timestamp_envio": round(time.time(), 4),
                    "lecturas": lecturas_lote,
                }

                # 3. SERIALIZAR A TEXTO JSON Y CODIFICAR A BYTES CON DELIMITADOR '\n'
                mensaje_json = json.dumps(data_container)
                mensaje_bytes = mensaje_json.encode('utf-8') + b'\n'

                # 4. ENVIAR POR LA RED
                client_socket.sendall(mensaje_bytes)
                print(
                    f"Lote JSON enviado: {len(mensaje_bytes)} bytes en total "
                    f"(~{len(mensaje_bytes) // LECTURAS_POR_LOTE} bytes/lectura)."
                )

                time.sleep(TIEMPO_ENTRE_ENVIOS)

    except ConnectionRefusedError:
        print("Error: Conexión rechazada. Asegúrate de que el Data Logger está en marcha.")
    except KeyboardInterrupt:
        print("\nSensor detenido por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")


if __name__ == '__main__':
    run_cliente()
