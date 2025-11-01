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
        while True:
            comando = input("Introduzca un comando:\n- 'get_status'\n- 'get_temp'\n- 'exit'\n> ")

            if comando.lower() == 'exit':
                # Enviamos el comando 'exit' para cerrar la sesión correctamente en el servidor
                client_socket.sendall('exit'.encode('utf-8'))
                # Esperamos la hipotética despedida del servidor, pero solo unos segundos
                # En el ejemplo del servidor vemos que no es necesario, el timeout
                # ya que tras exit() el servidor cierra la conexión directamente.
                # y recv() ya no bloquearía.
                # Se añade a efectos educativos.
                client_socket.settimeout(2.0)  # segundos
                try:
                    respuesta_servidor = client_socket.recv(1024).decode('utf-8')
                    print(f"Respuesta del servidor: {respuesta_servidor}")
                except socket.timeout:
                    print("No se recibió respuesta de cierre del servidor (timeout). Cerrando sesión igualmente.")
                except Exception:
                    print("No se pudo recibir la respuesta de cierre.")
                client_socket.settimeout(None)  # Quitar el timeout
                print("Cerrando sesión.")
                break

            client_socket.sendall(comando.encode('utf-8'))

            # Recibimos la respuesta del servidor y manejamos posibles errores de decodificación
            try:
                respuesta_servidor = client_socket.recv(1024).decode('utf-8')
                print(f"Respuesta del servidor: {respuesta_servidor}")
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
