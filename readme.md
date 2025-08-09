# Kinect Skeleton Tracker

Este proyecto en python 3.6 utiliza OpenNI2 y NiTE2 para rastrear usuarios y sus articulaciones mediante un dispositivo Kinect. El código inicializa el dispositivo, configura el flujo de color y utiliza el rastreador de usuarios para obtener datos de esqueleto. Además, implementa un servidor WebSocket para transmitir los datos del esqueleto en tiempo real, probado en windows 10/11.

## Requisitos

- Python 3.6 
- Kinect v1 con su adaptador de energia/usb (se vende por separado)
- OpenNI2
- NiTE2

## Instalación

1. **Instalar OpenNI2 y NiTE2**:
   - Descarga e instala OpenNI2 desde [OpenNI2 Releases](https://github.com/OpenNI/OpenNI2/releases).
   - Descarga e instala NiTE2 desde un repositorio confiable.
   - Si usas SO version de 64bits instala las 2 versiones de cada software
   - En las Notas dejo enlace de carpeta drive con lo necesario

2. **Activar entorno virtual con ENV**
En terminal:
    py -m venv venv
   .\venv\Scripts\activate

  Esto es recomendado, pero no necesario

3. **Instalar dependencias de Python**:
  Instala las siguientes dependencias:

  pip install scikit-build
  pip install opencv-python
  pip install pywin32
  pip install argparse
  pip install numpy
  pip install primesense
  pip install openni
  pip install websockets==6.0
  pip install asyncio

  Quiza tengas que actualizar pip para que opencv-python instale la version adecuada a tu version de python:

  python -m pip install --upgrade pip 

4. **Configurar Rutas**:
    Asegúrate de que las rutas a las bibliotecas de OpenNI2 y NiTE2 estén configuradas correctamente en el código:

    openni2.initialize("C:/Program Files/OpenNI2/Redist")
    nite2.initialize("C:/Program Files/PrimeSense/NiTE2/Redist")

    - Si usas SO de 64 bits, de preferencia usa las librerias de 64bits. Las de 32 a veces dan error.

5. **Mover archivos**
    Baja y luego ve a \site-packages\openni en tu entorno virtual si lo creaste con VENV o si no usas entorno y decidiste ir a lo loco ve a: C:\Users\Tuusuario\AppData\Local\Programs\Python\Python36\Lib\site-packages\openni
    y mueve el contenido de la carpeta "openni python master/openni", esto esta en la carpeta drive o en el repositorio:
    https://github.com/severin-lemaignan/openni-python/tree/master

    Busca ahora C:\Program Files\PrimeSense\NiTE2\Redist
    y Copia la carpeta NiTE2 al root de tu proyecto.

## Uso
1. Conecta el dispositivo Kinect a tu computadora.
2. Ejecuta el script principal:

    python app.py

3. El programa inicializará el dispositivo Kinect, comenzará a rastrear usuarios y mostrará datos de articulaciones. Además, transmitirá los datos del esqueleto a través de un servidor WebSocket.

## Funcionalidades
    - Rastreo de usuarios: Detecta y rastrea usuarios en el campo de visión del Kinect.
    - Rastreo de esqueleto: Obtiene las posiciones de las articulaciones principales del cuerpo, como cabeza, cuello, hombros, codos, manos, torso, caderas y rodillas.
    - Flujo de color: Captura el flujo de video en color del Kinect.
    - Servidor WebSocket: Transmite los datos del esqueleto en tiempo real a través de un servidor WebSocket.

## WebSocket
El servidor WebSocket está implementado utilizando la biblioteca websockets. Los datos del esqueleto se envían en formato JSON a los clientes conectados.

Ejemplo de datos enviados:

{
  "user_id": 1,
  "joints": {
    "head": {"x": 0.5, "y": 0.2, "z": 1.0},
    "neck": {"x": 0.5, "y": 0.3, "z": 1.0},
    ...
  }
}

## Mouse.py
Este script permite controlar el puntero del mouse de windows con la mano derecha y con la mano izquierda generas un click, dobla o acerca la mano izquierda al hombro izquierdo para mousedown y alejalo o relaja el brazo para mouseup. Con esta ccion puedes mantener el click y generar click&drag.

## Conexión al servidor WebSocket:

El servidor WebSocket se ejecuta en ws://localhost:8765.
Puedes conectarte al servidor utilizando cualquier cliente WebSocket, como una aplicación personalizada, se incluye un ejemplo con html y js(index.html)


## Estructura del Código
**Inicialización:**
Configura OpenNI2 y NiTE2.
Inicia el flujo de color del Kinect.
**Rastreo de usuarios**
Utiliza nite2.UserTracker para rastrear usuarios y sus articulaciones.
**Articulaciones:**
Define un diccionario JOINT_NAMES para mapear los IDs de NiTE2 a nombres de articulaciones.
**Servidor WebSocket**
Implementa un servidor WebSocket que transmite los datos del esqueleto en tiempo real.


## Notas
    - Este proyecto está diseñado para Kinect v1. No es compatible con Kinect v2 ni con Azure Kinect, es lo que habia a la mano
    - Asegúrate de que los controladores del Kinect estén instalados correctamente.
    - Si encuentras errores relacionados con OpenNI2 o NiTE2, verifica que las rutas a las bibliotecas sean correctas.
    - app copy.py es un script que controla el puntero del mouse en relacion al movimiento de la mano derecha entro de un cuadro delimitado, si acercas la mano al kinect cuenta como click derecho.
    - Script creado por chatGPT y ajustado a manopla.
    - Vas a encontrar muchos problemas para instalar Nite2 y openni2, echale ganas.
    - Instala Nite2 y openni 32 y 64 bits si usas SO de 64bits.
    - Es probable que necesites agregar openni al PATH de windows.
    - La carpeta NiTE2 incluye archivos necesarios para la ejecucion, estos provienen de C:\Program Files\OpenNI2\Redist\OpenNI2
    - Nunca confies en lo que dice la IA, te va a tener dando vueltas a lo wey, requirements.txt es prueba de ello.
    - Zelda: https://drive.google.com/drive/folders/1_raBT25tHLTheTAeqAd02X6gzUoQ2dgs

## Referencias
https://www.youtube.com/watch?v=m5uTH3S9P9g
