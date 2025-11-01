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

print(f"¡Conexión establecida con {client_address}!")

# --- 5. COMUNICACIÓN ---
# Ahora usamos el 'client_connection' para hablar.
# Recibimos hasta 1024 bytes de datos.
data = client_connection.recv(1024)

# Los datos viajan como 'bytes', una secuencia de números.
# Para verlos como texto, tenemos que decodificarlos.
mensaje_recibido = data.decode('utf-8')
print(f"El cliente dice: '{mensaje_recibido}'")

# Enviamos una respuesta. También debemos codificarla a bytes.
respuesta = "¡Hola, cliente! Mensaje recibido."
client_connection.sendall(respuesta.encode('utf-8'))

# --- 6. CIERRE ---
# Cerramos la conexión con el cliente y luego el socket del servidor.
client_connection.close()
server_socket.close()

print("Servidor finalizado.")
