# Práctica: Sockets y Protocolos de Comunicación

Este repositorio contiene el material de referencia y el enunciado para la práctica de sockets. El objetivo es construir, paso a paso, un sistema de comunicación cliente-servidor, evolucionando desde un simple intercambio de texto hasta un protocolo binario eficiente para la transmisión de datos de telemetría.

## Fases de Aprendizaje (Código de Ejemplo Proporcionado)

Las primeras tres carpetas contienen ejemplos funcionales que debes estudiar y comprender. Representan la base sobre la que construirás la solución final.

### 1. `cliente-servidor-basico`

*   **`client.py`**: Cliente sencillo que se conecta al servidor, envía un único mensaje y termina.
*   **`server.py`**: Servidor básico que espera una conexión, recibe un mensaje y responde una vez antes de cerrar.
*   **Propósito**: Introducir los conceptos fundamentales de `socket`, `bind`, `listen`, `accept`, `connect`, `send` y `recv`. Es el "Hola Mundo" de la programación de redes.

### 2. `sesion-interactiva`

*   **`client_interactive.py`**: Cliente interactivo que permite al usuario enviar múltiples mensajes al servidor en una misma sesión, hasta que se escribe el comando 'exit'.
*   **`server_interactive.py`**: Servidor que mantiene la conexión abierta, procesando mensajes en un bucle hasta que el cliente se desconecta.
*   **Propósito**: Mostrar cómo gestionar una sesión persistente, procesar múltiples intercambios y manejar un cierre de conexión ordenado por parte del cliente.

### 3. `sensor-JSON`

*   **`sensor_json.py`**: Simula un sensor autónomo (IoT) que genera lecturas periódicas de temperatura y humedad.
*   **`data_logger_json.py`**: Servidor que actúa como un registrador de datos. Escucha las conexiones de los sensores y guarda la información.
*   **`sensor_data.csv`**: Fichero de texto donde el servidor almacena las lecturas recibidas.

**Descripción Detallada:**

Esta fase simula un caso de uso muy común: un dispositivo de campo que envía datos a un servidor central para su almacenamiento y posterior análisis. La comunicación se realiza usando **JSON (JavaScript Object Notation)**, un formato de texto estándar en la industria.

**Conceptos Clave a Observar:**

1.  **Serialización (en el sensor):** El sensor genera los datos como un diccionario de Python, una estructura de datos nativa. Para poder enviarlo a través de la red, debe convertirlo (serializarlo) a un formato universal: una cadena de texto JSON. Fíjate en el uso de `json.dumps()`.
2.  **Payload binario en JSON:** El sensor empaqueta lotes de lecturas en formato binario y los codifica en base64 para enviarlos como parte del mensaje JSON. 
3.  **Deserialización (en el servidor):** El servidor recibe esta cadena de texto. Para poder acceder a los datos de forma estructurada (por ejemplo, `payload['values']['temperatura_c']`), debe reconvertirla (deserializarla) a un diccionario de Python. Fíjate en el uso de `json.loads()`.
4.  **Delimitación de Mensajes:** Los sockets trabajan con un flujo continuo de bytes. ¿Cómo sabe el servidor dónde termina un mensaje JSON y empieza el siguiente? La solución implementada aquí es un convenio simple: el cliente añade un carácter de nueva línea (`\n`) al final de cada envío. El servidor lee del buffer hasta encontrar ese delimitador.
5.  **Ventajas y Desventajas:** JSON es legible por humanos, lo que facilita enormemente la depuración. Además, es muy flexible, ya que podemos añadir nuevos campos sin _romper_ el sistema. Sin embargo, es **ineficiente en tamaño**. Las claves (`"sensor_id"`, `"temperatura_c"`) se repiten en cada mensaje, y los números se representan como texto, ocupando más bytes de los necesarios. Esto nos lleva a tu misión...


---

## Práctica Final: Protocolo Binario Eficiente

### Tu Misión

Hemos visto que JSON es cómodo pero puede ser ineficiente. En entornos de alto rendimiento o con ancho de banda limitado (como en dispositivos IoT a baterías), cada byte cuenta. Tu objetivo es **crear desde cero** los scripts para el sensor y el data logger, reemplazando el protocolo JSON por un **protocolo binario puro y compacto** diseñado para máxima eficiencia.

Deberás crear dos ficheros: `sensor_binario.py` y `data_logger_binario.py`.

### Especificación del Protocolo

Un protocolo es un **contrato** que cliente y servidor deben seguir. Vuestro protocolo tendrá dos partes: una estructura de mensaje fija y un contenido de datos que vosotros diseñaréis.

#### Parte 1: La Estructura del Mensaje

Todo mensaje enviado por la red debe seguir esta estructura para poder manejar lotes de datos de tamaño variable.

**Mensaje = `[CABECERA][PAYLOAD]`**

*   **La Cabecera:**
    *   **Propósito**: Indicar cuántas lecturas de sensor contiene el payload.
    *   **Formato**: Un único **entero sin signo de 4 bytes** en orden de bytes de red (Big-Endian).
    *   **Formato `struct`**: `>I`

*   **El Payload:**
    *   **Propósito**: Contener los datos de `N` lecturas, una tras otra, sin separadores, donde `N` es el número indicado en la cabecera.

#### Parte 2: La Estructura de la Lectura Individual (Tu Diseño)

Aquí es donde tomarás tus propias decisiones de ingeniería. En lugar de usar temperatura y humedad, deberás definir tu propio sensor.

**Pasos a seguir:**

1.  **Elige un Sensor:** Investiga y elige un tipo de sensor industrial o de laboratorio relevante para la **ingeniería eléctrica**.

2.  **Define las Medidas:** Define **entre 3 y 5 medidas numéricas** y alguna **identificativa** del sensor que el dispositivo proporcionaría. Debe haber alguna mezcla de tipos de datos: enteros y reales.

3.  **Elige los Tipos de Datos:** Para cada medida, elige el tipo de dato binario más adecuado de la librería `struct`, justificando la precisión y el rango necesarios. ¿Es suficiente un `float` de 4 bytes (`f`) o necesitas un `double` de 8 bytes (`d`)? ¿Alguna medida es un contador que podría ser un `int` (`i`) o un `short` (`h`)?

4.  **Documenta tu Protocolo:** Define tu **formato `struct`** para una lectura individual (ej. `>dfff`, `>ffiH`, etc.) y documéntalo en un comentario al principio de tus dos scripts. Por ejemplo:
    ```python
    # --- PROTOCOLO DE LECTURA DE sssss ---
    # Formato: >dfff
    # - xxxx: double (8 bytes)
    # - yyyy: float (4 bytes)
    # - zzzz: float (4 bytes)
    # - wwww: float (4 bytes)
    # Tamaño total por lectura: 20 bytes
    ```

### Tarea 1: Implementar `sensor_binario.py`

Crea un script que simule el sensor que has diseñado. Debe generar **lotes de lecturas** (con un tamaño aleatorio, por ejemplo, entre **1** y **10**), empaquetarlas siguiendo **tu protocolo** y enviarlas al servidor.

### Tarea 2: Implementar `data_logger_binario.py`

Crea un servidor que reciba los lotes binarios, los desempaquete según la especificación de tu protocolo y almacene las lecturas en un fichero CSV. Las columnas del CSV deben corresponder a las medidas que has definido.




