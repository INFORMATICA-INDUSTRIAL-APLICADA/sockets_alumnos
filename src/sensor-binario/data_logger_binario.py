# --- PROTOCOLO DE LECTURA DE <NOMBRE DE TU SENSOR ELÉCTRICO> ---
# Orden de bytes: Big-Endian (>)
# Cabecera del lote: >I (4 bytes, uint32: número de lecturas N)
# Formato de cada lectura: >...
# - ...
# Tamaño total por lectura: ... bytes

import csv
import socket
import struct
from pathlib import Path

# --- CONFIGURACIÓN DE RED Y ARCHIVOS ---
HOST = '0.0.0.0'
PORT = 65432
LOG_FILE = Path(__file__).resolve().parent / 'sensor_data.csv'

# =====================================================================
# PARTE 1: MANIPULACIÓN DEL MENSAJE BINARIO (A COMPLETAR POR EL ALUMNO)
# =====================================================================

# TODO: Define los nombres de las columnas del CSV (deben corresponder con las medidas de tu protocolo)
CSV_HEADER: list[str] = []

# Definición del protocolo binario (debe coincidir exactamente con el del sensor)
FORMATO_CABECERA = '>I'

# TODO: Define el formato struct de una lectura individual (idéntico al de sensor_binario.py)
FORMATO_LECTURA = ''


def desempaquetar_cabecera(cabecera_bytes: bytes) -> int:
    """
    Recibe los 4 bytes de la cabecera binaria y devuelve el número de lecturas (N)
    que componen el lote usando struct.unpack().
    """
    # TODO: Desempaquetar cabecera_bytes usando FORMATO_CABECERA y devolver el entero N
    raise NotImplementedError("Debes implementar desempaquetar_cabecera()")


def procesar_y_guardar_payload(payload_bytes: bytes) -> int:
    """
    Recibe los bytes del payload completo, desempaqueta las lecturas siguiendo
    FORMATO_LECTURA (por ejemplo, con struct.iter_unpack) y las añade al fichero CSV.
    Devuelve el número de lecturas guardadas.
    """
    # TODO:
    # 1. Abrir el fichero LOG_FILE en modo 'a' (append), con newline='' y encoding='utf-8'.
    # 2. Recorrer las lecturas empaquetadas en payload_bytes usando struct.iter_unpack(FORMATO_LECTURA, payload_bytes).
    # 3. Escribir cada fila en el CSV usando csv.writer(f).writerow([...]).
    # 4. Devolver cuántas lecturas se han guardado.
    raise NotImplementedError("Debes implementar procesar_y_guardar_payload()")


# =====================================================================
# PARTE 2: INFRAESTRUCTURA DE SOCKETS (PROPORCIONADA - NO MODIFICAR)
# =====================================================================


def setup_csv_file() -> None:
    """Crea el fichero CSV con su cabecera si aún no existe."""
    if not LOG_FILE.exists():
        with open(LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
            csv.writer(f).writerow(CSV_HEADER)
        print(f"Fichero '{LOG_FILE.name}' creado en {LOG_FILE.parent}.")


def recv_all(sock: socket.socket, n: int) -> bytes | None:
    """
    Recibe exactamente 'n' bytes de un socket TCP.
    Dado que TCP es un flujo continuo de bytes, sock.recv(n) podría devolver menos
    de 'n' bytes si el paquete llega fragmentado; este bucle garantiza leer el bloque completo.
    Devuelve None si el cliente cierra la conexión antes de completar la lectura.
    """
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return bytes(data)


def handle_client_connection(connection: socket.socket) -> None:
    """Gestiona la recepción de lotes binarios de un cliente conectado."""
    tamano_cabecera = struct.calcsize(FORMATO_CABECERA)
    tamano_lectura_unitaria = struct.calcsize(FORMATO_LECTURA)

    try:
        with connection:
            while True:
                # 1. Leer los 4 bytes de la cabecera
                cabecera_bytes = recv_all(connection, tamano_cabecera)
                if not cabecera_bytes:
                    break  # El cliente cerró la conexión limpiamente

                # 2. Obtener cuántas lecturas vienen en este lote (función del alumno)
                num_lecturas = desempaquetar_cabecera(cabecera_bytes)
                print(f"\nCabecera recibida: se esperan {num_lecturas} lecturas.")

                # 3. Calcular el tamaño exacto del payload y leerlo de la red
                tamano_payload = num_lecturas * tamano_lectura_unitaria
                payload_bytes = recv_all(connection, tamano_payload)
                if not payload_bytes:
                    print("Error: El cliente se desconectó antes de completar el envío del payload.")
                    break

                # 4. Desempaquetar el payload y guardarlo en el CSV (función del alumno)
                guardadas = procesar_y_guardar_payload(payload_bytes)
                print(f"Lote procesado: {guardadas} lecturas guardadas en '{LOG_FILE.name}'.")

    except ConnectionResetError:
        print("El cliente cerró la conexión de forma abrupta.")
    except Exception as e:
        print(f"Ocurrió un error durante la comunicación: {e}")


def run_server() -> None:
    """Inicia el servidor TCP y espera conexiones de sensores de forma continua."""
    setup_csv_file()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"--- Data Logger Binario escuchando en {HOST}:{PORT} ---")

        while True:
            try:
                client_conn, client_addr = server_socket.accept()
                print(f"\nConexión aceptada de {client_addr}")
                handle_client_connection(client_conn)
                print(f"Conexión con {client_addr} cerrada.")
            except KeyboardInterrupt:
                print("\nServidor detenido por el usuario.")
                break


if __name__ == '__main__':
    run_server()
