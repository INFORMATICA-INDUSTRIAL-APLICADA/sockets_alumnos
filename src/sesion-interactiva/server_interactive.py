# Importamos la librería 'socket', que nos da las herramientas necesarias.
import socket

# --- 0. CONFIGURACIÓN ---
# La dirección 'HOST' donde operará nuestro servidor.
# '0.0.0.0' es una dirección especial que significa "escuchar en todas las
# interfaces de red disponibles en esta máquina".
HOST = '0.0.0.0'

# El 'PORT' (puerto) es como el número de extensión en una centralita.
# Elegimos uno alto (>1023) para evitar conflictos.
PORT = 65432

# --- 1. CREACIÓN DEL SOCKET ---
# Creamos nuestro socket servidor. Los detalles de los parámetros
# los veremos en el próximo tema. Por ahora, esta es nuestra "receta"
# para una conexión fiable.
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# --- 2. VINCULAR (BIND) ---
# Asociamos nuestro socket a la dirección y puerto que hemos definido.
# A partir de aquí, nuestro programa "es dueño" de esa extensión.
server_socket.bind((HOST, PORT))
print(f"Servidor vinculado al puerto {PORT}...")

# --- 3. ESCUCHAR (LISTEN) ---
# Ponemos el servidor en modo de escucha.
server_socket.listen()
print("Servidor escuchando, esperando a un cliente...")

# --- 4. ACEPTAR (ACCEPT) ---
# Esta es una línea bloqueante. El programa se detiene aquí hasta que
# un cliente se conecta.
# Cuando ocurre, nos devuelve dos cosas: un nuevo socket para hablar
# con ese cliente y la dirección del cliente.
client_connection, client_address = server_socket.accept()

print(f"¡Cliente de comandos conectado desde {client_address}!")

# --- 5. BUCLE DE PROCESAMIENTO DE COMANDOS ---
while True:
    data = client_connection.recv(1024)
    if not data:
        print("El cliente ha cerrado la sesión.")
        break

    # Intentamos decodificar el comando recibido
    try:
        comando_recibido = data.decode('utf-8')
    except UnicodeDecodeError:
        print("Error al decodificar el comando recibido.")
        client_connection.sendall("Error: comando no válido (decodificación)".encode('utf-8'))
        continue

    print(f"Comando recibido: '{comando_recibido}'")

    # Procesamiento de comandos
    if comando_recibido.lower() == 'get_status':
        # Responde con el estado del sistema
        respuesta = "STATUS: OK, 100%"
    elif comando_recibido.lower() == 'get_temp':
        # Responde con la temperatura simulada
        respuesta = "TEMP: 25.3 C"
    elif comando_recibido.lower() == 'exit':
        # Permite al cliente cerrar la sesión de forma educada
        respuesta = "Sesión finalizada por el cliente. ¡Hasta pronto!"
        # client_connection.sendall(respuesta.encode('utf-8'))
        print("El cliente ha solicitado salir.")
        break
    else:
        # Comando no reconocido
        respuesta = f"Comando '{comando_recibido}' no reconocido."

    # Enviamos la respuesta al cliente (si no es exit)
    if comando_recibido.lower() != 'exit':
        client_connection.sendall(respuesta.encode('utf-8'))

# --- 6. CIERRE ---
# Este código se ejecuta cuando salimos del bucle.
client_connection.close()
# En un servidor real, aquí volveríamos a accept() para esperar otro cliente.
server_socket.close()

print("Servidor finalizado.")
