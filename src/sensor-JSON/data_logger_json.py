import socket
import json
import csv
import os
import struct
import base64

# --- CONFIGURACIÓN ---
HOST = '0.0.0.0'
PORT = 65432
LOG_FILE = 'sensor_data.csv'
CSV_HEADER = ['timestamp', 'sensor_id', 'temperatura_c', 'humedad_rel']

# --- DEFINICIÓN DEL PROTOCOLO BINARIO INTERNO (debe ser idéntico al del cliente) ---
FORMATO_LECTURA = '>dff'


def setup_csv_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, mode='w', newline='') as f:
            csv.writer(f).writerow(CSV_HEADER)
        print(f"Fichero '{LOG_FILE}' creado.")


def handle_client_connection(connection):
    buffer = b""
    with connection:
        while True:
            data = connection.recv(1024)
            if not data:
                break

            buffer += data
            while b'\n' in buffer:
                json_part, buffer = buffer.split(b'\n', 1)
                try:
                    # 1. DESERIALIZAR EL CONTENEDOR JSON
                    payload = json.loads(json_part.decode('utf-8'))
                    sensor_id = payload.get('sensor_id')
                    payload_b64 = payload.get('payload_b64')

                    # 2. DECODIFICAR DE BASE64 A BYTES
                    payload_binario = base64.b64decode(payload_b64)
                    print(f"\nJSON de {sensor_id} recibido. Payload binario de {len(payload_binario)} bytes.")

                    # 3. DESEMPAQUETAR LAS LECTURAS DEL PAYLOAD BINARIO
                    # struct.iter_unpack es ideal para procesar secuencias de estructuras
                    lecturas_guardadas = 0
                    for ts, temp, hum in struct.iter_unpack(FORMATO_LECTURA, payload_binario):
                        with open(LOG_FILE, mode='a', newline='') as f:
                            writer = csv.writer(f)
                            writer.writerow([ts, sensor_id, round(temp, 2), round(hum, 2)])
                        lecturas_guardadas += 1

                    print(f"{lecturas_guardadas} lecturas guardadas en '{LOG_FILE}'.")

                except (json.JSONDecodeError, KeyError, TypeError) as e:
                    print(f"Error procesando el mensaje: {e}. Mensaje: {json_part}")


def run_server():
    setup_csv_file()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"--- Data Logger (JSON+Binary) escuchando en {HOST}:{PORT} ---")

        while True:
            try:
                conn, addr = server_socket.accept()
                print(f"\nConexión aceptada de {addr}")
                handle_client_connection(conn)
                print(f"Conexión con {addr} cerrada.")
            except KeyboardInterrupt:
                print("\nServidor detenido.")
                break


if __name__ == '__main__':
    run_server()
