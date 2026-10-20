import csv
import json
import socket
from pathlib import Path

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 65432
LOG_FILE = Path(__file__).resolve().parent / 'sensor_data.csv'
CSV_HEADER = ['timestamp', 'sensor_id', 'temperatura_c', 'humedad_rel']


def setup_csv_file() -> None:
    """Crea el fichero CSV con su cabecera si aún no existe."""
    if not LOG_FILE.exists():
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(CSV_HEADER)
        print(f"Fichero '{LOG_FILE.name}' creado en {LOG_FILE.parent}.")


def handle_client_connection(connection: socket.socket) -> None:
    """Recibe mensajes JSON delimitados por '\\n', los deserializa y los guarda en CSV."""
    buffer = b""
    try:
        with connection:
            while True:
                data = connection.recv(1024)
                if not data:
                    break

                buffer += data
                # Extraemos todos los mensajes completos (terminados en '\n') que haya en el buffer
                while b'\n' in buffer:
                    json_part, buffer = buffer.split(b'\n', 1)
                    if not json_part.strip():
                        continue

                    try:
                        # 1. DESERIALIZAR EL MENSAJE JSON A DICCIONARIO DE PYTHON
                        payload = json.loads(json_part.decode('utf-8'))
                        sensor_id = payload['sensor_id']
                        lecturas = payload['lecturas']

                        print(
                            f"\nJSON de '{sensor_id}' recibido ({len(json_part)} bytes, "
                            f"{len(lecturas)} lecturas)."
                        )

                        # 2. GUARDAR TODAS LAS LECTURAS DEL LOTE EN EL FICHERO CSV
                        lecturas_guardadas = 0
                        with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            for lectura in lecturas:
                                ts = lectura['timestamp']
                                temp = lectura['temperatura_c']
                                hum = lectura['humedad_rel']
                                writer.writerow([ts, sensor_id, round(temp, 2), round(hum, 2)])
                                lecturas_guardadas += 1

                        print(f"{lecturas_guardadas} lecturas guardadas en '{LOG_FILE.name}'.")

                    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError) as e:
                        print(f"Error procesando el mensaje: {e}. Mensaje: {json_part!r}")
    except ConnectionResetError:
        print("El cliente cerró la conexión de forma abrupta.")


def run_server() -> None:
    setup_csv_file()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"--- Data Logger JSON escuchando en {HOST}:{PORT} ---")

        while True:
            try:
                conn, addr = server_socket.accept()
                print(f"\nConexión aceptada de {addr}")
                handle_client_connection(conn)
                print(f"Conexión con {addr} cerrada.")
            except KeyboardInterrupt:
                print("\nServidor detenido por el usuario.")
                break


if __name__ == '__main__':
    run_server()
