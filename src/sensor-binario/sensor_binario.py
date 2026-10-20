# --- PROTOCOLO DE LECTURA DE <NOMBRE DE TU SENSOR ELÉCTRICO> ---
# Orden de bytes: Big-Endian (>)
# Cabecera del lote: >I (4 bytes, uint32: número de lecturas N)
# Formato de cada lectura: >...
# - ...
# Tamaño total por lectura: ... bytes

import random
import socket
import struct
import time

# --- CONFIGURACIÓN DE RED ---
HOST = 'localhost'
PORT = 65432
TIEMPO_ENTRE_ENVIOS = 5  # Segundos entre envíos de lotes
MIN_LECTURAS_LOTE = 1
MAX_LECTURAS_LOTE = 10

# =====================================================================
# PARTE 1: DISEÑO DEL MENSAJE BINARIO (A COMPLETAR POR EL ALUMNO)
# =====================================================================

# Formato struct de la cabecera (obligatorio: entero sin signo de 4 bytes Big-Endian)
FORMATO_CABECERA = '>I'

# TODO: Define el formato struct de una lectura individual de tu sensor (ej. '>HdfffIB')
FORMATO_LECTURA = ''


def simular_lectura() -> tuple:
    """
    Simula una lectura individual del sensor eléctrico y devuelve una tupla
    con los valores en el mismo orden definido en FORMATO_LECTURA.
    """
    # TODO: Generar y devolver la tupla con las medidas simuladas de tu sensor
    raise NotImplementedError("Debes implementar simular_lectura()")


def construir_mensaje_lote() -> tuple[bytes, int]:
    """
    Genera un lote aleatorio de lecturas (entre MIN_LECTURAS_LOTE y MAX_LECTURAS_LOTE),
    lo empaqueta siguiendo el protocolo [CABECERA][PAYLOAD] y devuelve:
      (mensaje_completo_en_bytes, numero_de_lecturas)
    """
    # TODO:
    # 1. Elegir un número aleatorio de lecturas (num_lecturas) entre MIN_LECTURAS_LOTE y MAX_LECTURAS_LOTE.
    # 2. Empaquetar la cabecera con struct.pack(FORMATO_CABECERA, num_lecturas).
    # 3. Llamar a simular_lectura() 'num_lecturas' veces y empaquetar cada lectura con struct.pack(FORMATO_LECTURA, ...).
    # 4. Concatenar cabecera_bytes + payload_bytes y devolver (mensaje_completo, num_lecturas).
    raise NotImplementedError("Debes implementar construir_mensaje_lote()")


# =====================================================================
# PARTE 2: INFRAESTRUCTURA DE SOCKETS (PROPORCIONADA - NO MODIFICAR)
# =====================================================================


def run_cliente() -> None:
    """Gestiona la conexión TCP con el servidor y el envío periódico de lotes."""
    tamano_lectura = struct.calcsize(FORMATO_LECTURA)
    print(f"--- Sensor Binario Autónomo ({tamano_lectura} bytes/lectura) ---")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Intentando conectar al Data Logger en {HOST}:{PORT}...")
            client_socket.connect((HOST, PORT))
            print("¡Conexión establecida!")

            while True:
                mensaje_completo, num_lecturas = construir_mensaje_lote()

                print(
                    f"\nEnviando lote de {num_lecturas} lecturas "
                    f"({len(mensaje_completo)} bytes en total)..."
                )
                client_socket.sendall(mensaje_completo)
                print("Lote binario enviado correctamente.")

                time.sleep(TIEMPO_ENTRE_ENVIOS)

    except ConnectionRefusedError:
        print("Error: Conexión rechazada. Asegúrate de que el Data Logger está en marcha.")
    except KeyboardInterrupt:
        print("\nSensor detenido por el usuario.")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    print("--- Sensor finalizado ---")


if __name__ == '__main__':
    run_cliente()
