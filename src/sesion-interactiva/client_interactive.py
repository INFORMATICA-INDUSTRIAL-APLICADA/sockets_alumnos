import socket

# --- 1. CONFIGURACIÓN ---
# La dirección del servidor al que nos queremos conectar.
# 'localhost' es un nombre especial que siempre apunta a nuestra
# propia máquina. Es perfecto para probar nuestro cliente y servidor
# en el mismo ordenador.
HOST = 'localhost'

# El puerto al que vamos a llamar. Debe ser EXACTAMENTE el mismo
# en el que el servidor está escuchando.
PORT = 65432

# --- 2. CREACIÓN Y CONEXIÓN ---
# Creamos nuestro socket y, en un solo bloque 'with', intentamos conectar.
# El bloque 'with' se encargará de cerrar el socket automáticamente al final.
print("--- Cliente de Sockets ---")
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # Intentamos establecer la conexión con el servidor.
        print(f"Intentando conectar a {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))
        print("¡Conexión exitosa con el servidor!")

        # --- 3. BUCLE DE COMUNICACIÓN ---
        # Iniciamos un bucle para permitir al usuario enviar múltiples mensajes.
        sesion_activa = True
        while sesion_activa:
            comando = input(
                "Introduzca un comando:\n- 'get_status'\n- 'get_temp'\n- 'exit'\n> "
            ).strip()

            # Validamos que el comando no esté vacío: enviar b"" con sendall() no transmite
            # ningún byte por la red y dejaría a cliente y servidor esperando indefinidamente en recv().
            if not comando:
                print("Aviso: El comando no puede estar vacío.")
            else:
                if comando.lower() == 'exit':
                    sesion_activa = False
                    # Establecemos un tiempo máximo de espera (2 s) para la despedida del servidor
                    client_socket.settimeout(2.0)

                # Enviamos el comando al servidor
                client_socket.sendall(comando.encode('utf-8'))

                # Recibimos la respuesta del servidor y manejamos posibles errores
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        print("El servidor ha cerrado la conexión.")
                        sesion_activa = False
                    else:
                        respuesta_servidor = data.decode('utf-8')
                        print(f"Respuesta del servidor: {respuesta_servidor}")
                except socket.timeout:
                    print("No se recibió respuesta de cierre del servidor (timeout).")
                except UnicodeDecodeError:
                    print("Error al decodificar la respuesta del servidor.")

    # --- 4. CIERRE ---
    # Al salir del bucle, el bloque 'with' se encargará de cerrar el socket.
    # Este cierre es lo que el servidor detecta en su `if not data`.
    print("Cerrando conexión.")

except ConnectionRefusedError:
    print("Error: Conexión rechazada. ¿Está el servidor en marcha?")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

print("--- Cliente finalizado ---")
