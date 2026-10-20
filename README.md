# Práctica: Sockets y Protocolos de Comunicación

Este repositorio contiene el material de referencia y el enunciado para la práctica de sockets. El objetivo es construir, paso a paso, un sistema de comunicación cliente-servidor, evolucionando desde un simple intercambio de texto hasta un protocolo binario eficiente para la transmisión de datos de telemetría.

## Fases de Aprendizaje (Código de Ejemplo Proporcionado)

Las primeras tres carpetas contienen ejemplos funcionales que debes estudiar y comprender. Representan la base sobre la que construirás la solución final.

### 1. `cliente-servidor-basico`

*   **`client.py`**: Cliente sencillo que se conecta al servidor, envía un único mensaje y termina.
*   **`server.py`**: Servidor básico que espera una conexión, recibe un mensaje y responde una vez antes de cerrar.
*   **Propósito**: Introducir los conceptos fundamentales de `socket`, `bind`, `listen`, `accept`, `connect`, `sendall` y `recv`. Es el "Hola Mundo" de la programación de redes.

**¿Cómo ejecutar el servidor y el cliente en Visual Studio Code?**

Como el servidor y el cliente son dos programas independientes que deben estar funcionando **al mismo tiempo**, necesitarás **dos terminales abiertas** en VS Code (este mismo procedimiento se aplica a todas las fases de la práctica):

1.  **Importante (error muy común):** Si ejecutas `server.py` con el botón de *Play* (`▷`) de arriba a la derecha y luego abres `client.py` y vuelves a pulsar *Play* (`▷`), VS Code intentará escribir el comando del cliente **dentro de la misma terminal** donde el servidor está bloqueado esperando en `accept()`, por lo que no funcionará.
2.  **Paso 1 — Lanzar primero el Servidor (Terminal 1):**
    *   Abre una terminal en VS Code (`Terminal` $\rightarrow$ `New Terminal` o `` Ctrl+Shift+` ``).
    *   Ejecuta el servidor:
        ```powershell
        python src/cliente-servidor-basico/server.py
        ```
    *   Verás el mensaje `Servidor escuchando, esperando a un cliente...`. La terminal se quedará detenida ahí (bloqueada en `accept()`) esperando la llamada del cliente. **No la cierres.**
3.  **Paso 2 — Lanzar después el Cliente (Terminal 2):**
    *   En el panel de la terminal de VS Code, pulsa el icono de **Dividir terminal** (*Split Terminal*, icono de dos paneles `[|]`) o el botón **`+`** para abrir una segunda terminal independiente. Tener la terminal dividida te permitirá ver ambos programas conversar en tiempo real.
    *   En esta segunda terminal, ejecuta el cliente:
        ```powershell
        python src/cliente-servidor-basico/client.py
        ```
    *   *(Nota: Si ejecutas el cliente antes de que el servidor esté en marcha, obtendrás el error `ConnectionRefusedError`).*
    *   **¿Qué significa el mensaje `¡Conexión establecida con ('127.0.0.1', 55613)!` en el servidor?** Esa tupla es el `client_address` (el "identificador de llamada" del cliente): `'127.0.0.1'` es la IP local (`localhost`) desde la que llama el cliente, y el segundo número (`55613`, que cambiará en cada ejecución) es el **puerto efímero** que el sistema operativo asigna temporalmente al cliente como origen de su llamada para comunicarse con el puerto fijo `65432` del servidor.
4.  **¿Cómo detener un servidor en bucle?** En las fases siguientes, cuando quieras parar un servidor o un sensor que se ejecuta en un bucle infinito (`while True`), haz clic en su terminal y pulsa **`Ctrl + C`**.

### 2. `sesion-interactiva`

*   **`client_interactive.py`**: Cliente interactivo que permite al usuario enviar múltiples mensajes al servidor en una misma sesión, hasta que se escribe el comando `exit`.
*   **`server_interactive.py`**: Servidor que mantiene la conexión abierta, procesando mensajes en un bucle hasta que el cliente se desconecta o solicita salir.
*   **Propósito**: Mostrar cómo gestionar una sesión persistente, procesar múltiples intercambios, validar entradas vacías y manejar un cierre de conexión ordenado.

**¿En qué consiste?**

A diferencia del ejemplo básico (donde cliente y servidor intercambian una sola frase y "cuelgan" inmediatamente), aquí la llamada se mantiene abierta dentro de un bucle `while True`. El cliente solicita comandos por teclado (`input()`) y el servidor actúa como un equipo industrial que responde a distintas órdenes remotas:
*   `get_status`: devuelve el estado del sistema (`STATUS: OK, 100%`).
*   `get_temp`: devuelve el valor actual de temperatura (`TEMP: 25.3 C`).
*   `exit`: solicita finalizar la sesión educadamente; el servidor envía un mensaje de despedida y ambos cierran la conexión.
*   Cualquier otro texto: el servidor informa de que el comando no es reconocido, pero mantiene la sesión abierta.

**Conceptos Clave a Observar:**
1.  **Conexión única, múltiples mensajes:** Las llamadas a `connect()` y `accept()` ocurren **una sola vez** antes del bucle `while True`; dentro del bucle solo se ejecutan `sendall()` y `recv()`.
2.  **Detección de desconexión (`if not data`):** Si el cliente cierra el programa abruptamente, `recv()` en el servidor devuelve bytes vacíos (`b""`), lo que permite detectar que han "colgado" al otro lado y salir del bucle.
3.  **Tiempo máximo de espera (`settimeout`):** Al enviar `exit`, el cliente configura un *timeout* de 2 segundos (`client_socket.settimeout(2.0)`) para evitar quedarse esperando indefinidamente si el servidor cerrara sin responder.

### 3. `sensor-JSON`

*   **`sensor_json.py`**: Simula un sensor autónomo (IoT) que genera lotes periódicos de lecturas de temperatura y humedad y los envía en formato JSON.
*   **`data_logger_json.py`**: Servidor que actúa como un registrador de datos (*Data Logger*). Escucha las conexiones de los sensores y guarda las lecturas recibidas.
*   **`sensor_data.csv`**: Fichero de texto donde el servidor almacena las lecturas recibidas.

**Descripción Detallada:**

Esta fase simula un caso de uso muy común en la industria: un dispositivo de campo que envía lotes de lecturas a un servidor central para su almacenamiento y posterior análisis. La comunicación se realiza usando **JSON (JavaScript Object Notation)**, un formato de texto estándar.

**Conceptos Clave a Observar:**

1.  **Serialización (en el sensor):** El sensor agrupa los datos en diccionarios y listas nativas de Python. Para poder enviarlos a través de la red, debe convertirlos (serializarlos) a una cadena de texto JSON mediante `json.dumps()` y codificarla a bytes UTF-8.
2.  **Deserialización (en el servidor):** El servidor recibe los bytes, los decodifica a texto y utiliza `json.loads()` para reconstruir el diccionario de Python y acceder a los datos de forma estructurada (por ejemplo, `payload["sensor_id"]` y cada lectura dentro de `payload["lecturas"]`).
3.  **Delimitación de Mensajes (*Framing*):** Los sockets TCP trabajan con un flujo continuo de bytes (*stream*), no con mensajes discretos. ¿Cómo sabe el servidor dónde termina un mensaje JSON y empieza el siguiente? El convenio implementado aquí es añadir un carácter de nueva línea (`\n`) al final de cada mensaje JSON. Como `json.dumps()` genera por defecto todo el JSON en una única línea compacta (y si hubiera algún salto de línea dentro de un texto lo escaparía como dos caracteres `\n`), el carácter de salto de línea real (`\n`) **nunca forma parte del contenido del JSON**, por lo que no da lugar a equívocos. El servidor acumula los bytes recibidos en un `buffer` y extrae mensajes completos buscando ese delimitador.
4.  **¿Por qué transmitimos en JSON y guardamos en CSV?:** Como vimos en el tema de JSON, para transmitir mensajes en continuo (*streaming*) por la red necesitamos un formato **autocontenido**, capaz de representar **estructuras anidadas** (metadatos del envío + lista de lecturas) y flexible ante evoluciones (si mañana el sensor añade un campo extra en el JSON, `data_logger_json.py` no se rompe porque accede por clave y no por posición). En cambio, el servidor guarda finalmente las lecturas en un fichero `.csv` asumiendo que esa tabla final de 4 columnas es un **esquema cerrado que no va a evolucionar**, pensado para abrirse directamente en una hoja de cálculo. Si el registro en disco tuviera que evolucionar con nuevas medidas en el futuro, lo guardaríamos como `.jsonl` o en una base de datos.
5.  **Ventajas y Desventajas:** JSON es legible por humanos y autodescriptivo, lo que facilita enormemente la depuración y la evolución del sistema (y es perfectamente válido cuando el ancho de banda sobra). Sin embargo, es **ineficiente en tamaño**: las claves (`"timestamp"`, `"temperatura_c"`, `"humedad_rel"`) se repiten en cada lectura del lote, y los números se representan como caracteres de texto ASCII, ocupando muchos más bytes de los necesarios. En escenarios industriales donde **el ancho de banda es limitado**, se transmiten miles de muestras por segundo o el consumo energético de la radio es crítico, este desperdicio resulta inaceptable. Esto nos lleva a tu misión...

---

## Práctica Final: Protocolo Binario Eficiente

### Tu Misión

Hemos visto que JSON es cómodo pero verboso. En entornos industriales de alto rendimiento o con ancho de banda y energía limitados (como dispositivos IIoT a batería o enlaces radio), cada byte cuenta. Tu objetivo es completar los scripts para el sensor y el *data logger* en la carpeta `src/sensor-binario`, reemplazando JSON por un **protocolo binario puro y compacto** mediante el módulo `struct` de Python.

Toda la **infraestructura de sockets TCP** (conexión, envío, recepción exacta de bloques de bytes con `recv_all`, gestión de errores y creación del archivo CSV) **ya te viene dada y resuelta** en ambos ficheros. Tu trabajo se centrará exclusivamente en el **diseño y empaquetado del mensaje en el cliente** y en el **desempaquetado y almacenamiento en el servidor**.

### Especificación del Protocolo

Un protocolo es un **contrato** estricto que cliente y servidor deben cumplir. En un protocolo binario puro **no podemos usar `\n` como delimitador**, ya que el byte `0x0A` (equivalente a `\n`) puede aparecer de forma natural dentro de cualquier número binario. Por ello, utilizaremos un esquema de **cabecera de longitud fija + payload**.

#### Parte 1: La Estructura del Mensaje (Obligatoria)

Todo mensaje enviado por la red debe seguir esta estructura para poder manejar lotes de datos de tamaño variable:

**Mensaje = `[CABECERA][PAYLOAD]`**

*   **La Cabecera:**
    *   **Propósito**: Indicar cuántas lecturas de sensor (`N`) contiene el payload que sigue a continuación.
    *   **Formato**: Un único **entero sin signo de 4 bytes** en orden de bytes de red (*Big-Endian*).
    *   **Formato `struct`**: `>I` (4 bytes).

*   **El Payload:**
    *   **Propósito**: Contener los datos binarios de las `N` lecturas empaquetadas una tras otra, sin separadores, donde `N` es el número indicado en la cabecera.
    *   **Tamaño en bytes**: `N * struct.calcsize(FORMATO_LECTURA)`.

> **Nota importante sobre TCP (`recv_all`):** Dado que TCP es un flujo continuo de bytes, una llamada a `socket.recv(tamano)` no garantiza devolver todos los bytes solicitados de una sola vez si el paquete se fragmenta en la red. Por ello, el servidor debe leer en un bucle hasta completar exactamente los 4 bytes de la cabecera y, a continuación, leer exactamente los `N * tamano_lectura` bytes del payload.

#### Parte 2: La Estructura de la Lectura Individual (Tu Diseño)

Aquí es donde tomarás tus propias decisiones de ingeniería. En lugar de limitarte a temperatura y humedad, diseñarás el protocolo de telemetría de un equipo eléctrico.

**Pasos a seguir:**

1.  **Elige un Sensor / Equipo:** Investiga y elige un tipo de sensor industrial o equipo de medida relevante para la **ingeniería eléctrica** (por ejemplo: analizador de redes eléctricas, monitor de transformador de potencia, inversor fotovoltaico, cargador de vehículo eléctrico, variador de frecuencia, etc.).

2.  **Define las Medidas:** Define **entre 3 y 5 medidas numéricas** (incluyendo o además del *timestamp*) y **alguna medida identificativa o de estado** del dispositivo. Debe existir mezcla de tipos de datos: **enteros y reales (coma flotante)**.

3.  **Elige los Tipos de Datos:** Para cada campo, elige el especificador más adecuado de la librería `struct` (usando orden de red Big-Endian `>`), justificando el rango y la precisión necesarios:
    *   ¿Cuándo basta un `float` de 4 bytes (`f`) y cuándo es imprescindible un `double` de 8 bytes (`d`, por ejemplo para `time.time()`)?
    *   ¿Qué campos son enteros sin signo o con signo de 1 byte (`B`/`b`), 2 bytes (`H`/`h`) o 4 bytes (`I`/`i`), como un identificador numérico del sensor, un contador de energía en Wh o un código de estado/alarma?

4.  **Documenta tu Protocolo:** Define tu **formato `struct`** para una lectura individual (ej. `>HdfffIB`, `>Hdfih`, etc.) y documéntalo en un bloque de comentarios al principio de tus dos scripts siguiendo esta plantilla:
    ```python
    # --- PROTOCOLO DE LECTURA DE <NOMBRE DEL SENSOR> ---
    # Orden de bytes: Big-Endian (>)
    # Cabecera del lote: >I (4 bytes, uint32: número de lecturas N)
    # Formato de cada lectura: >HdfffIB
    # - sensor_id:          unsigned short (H, 2 bytes) - ID numérico del equipo
    # - timestamp:          double         (d, 8 bytes) - Marca de tiempo Unix (s)
    # - magnitud_1:         float          (f, 4 bytes) - Descripción y unidades
    # - magnitud_2:         float          (f, 4 bytes) - Descripción y unidades
    # - magnitud_3:         float          (f, 4 bytes) - Descripción y unidades
    # - contador_entero:    unsigned int   (I, 4 bytes) - Descripción y unidades
    # - estado_alarma:      unsigned char  (B, 1 byte)  - Código de estado (0=OK, ...)
    # Tamaño total por lectura: 27 bytes
    ```

### Tarea 1: Completar `sensor_binario.py` (Lado Cliente)

En la **Parte 1** de `src/sensor-binario/sensor_binario.py` deberás:
1.  Definir la cadena de formato `FORMATO_LECTURA` de tu sensor eléctrico (y documentar el protocolo en la cabecera del archivo).
2.  Implementar `simular_lectura()`, que devuelve una tupla con los valores simulados de una lectura en el orden de `FORMATO_LECTURA`.
3.  Implementar `construir_mensaje_lote()`, que elige un número aleatorio de lecturas (entre `MIN_LECTURAS_LOTE` y `MAX_LECTURAS_LOTE`), empaqueta la cabecera (`>I`) y las `N` lecturas con `struct.pack()`, y devuelve `(mensaje_completo, num_lecturas)`.

### Tarea 2: Completar `data_logger_binario.py` (Lado Servidor)

En la **Parte 1** de `src/sensor-binario/data_logger_binario.py` deberás:
1.  Definir la lista `CSV_HEADER` con los nombres de las columnas de tu sensor y la misma cadena `FORMATO_LECTURA` que en el cliente.
2.  Implementar `desempaquetar_cabecera(cabecera_bytes)`, que recibe los 4 bytes de la cabecera y devuelve el entero `N` usando `struct.unpack()`.
3.  Implementar `procesar_y_guardar_payload(payload_bytes)`, que desempaqueta las `N` lecturas del bloque binario (por ejemplo con `struct.iter_unpack(FORMATO_LECTURA, payload_bytes)`), las escribe en el archivo CSV (`LOG_FILE`) y devuelve el número de lecturas guardadas.
