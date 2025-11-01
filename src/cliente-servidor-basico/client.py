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

        # --- 3. COMUNICACIÓN ---
        # Una vez conectados, podemos enviar nuestro mensaje.
        # Recuerda: ¡siempre hay que codificar el texto a bytes!
        mensaje = "Hola, servidor. Soy el cliente."
        print(f"Enviando mensaje: '{mensaje}'")
        client_socket.sendall(mensaje.encode('utf-8'))

        # Esperamos la respuesta del servidor.
        # La llamada a .recv() es bloqueante, espera hasta recibir algo.
        data = client_socket.recv(1024)
        respuesta_servidor = data.decode('utf-8')
        print(f"El servidor responde: '{respuesta_servidor}'")

except ConnectionRefusedError:
    print("Error: Conexión rechazada. ¿Está el servidor en marcha?")
except Exception as e:
    print(f"Ocurrió un error inesperado: {e}")

print("--- Cliente finalizado ---")
