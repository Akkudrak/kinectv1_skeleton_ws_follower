import cv2
import numpy as np
import json
import asyncio
import websockets
from openni import openni2, nite2

# Inicializar OpenNI2 y NiTE2
openni2.initialize("C:/Program Files/OpenNI2/Redist")
nite2.initialize("C:/Program Files/PrimeSense/NiTE2/Redist")

# Abrir Kinect
dev = openni2.Device.open_any()
color_stream = dev.create_color_stream()
color_stream.start()

# Tracker de usuarios/esqueleto
user_tracker = nite2.UserTracker(dev)

# Articulaciones (ID de NiTE2)
JOINT_NAMES = {
    0: "head",
    1: "neck",
    2: "left_shoulder",
    3: "right_shoulder",
    4: "left_elbow",
    5: "right_elbow",
    6: "left_hand",
    7: "right_hand",
    8: "torso",
    9: "left_hip",
    10: "right_hip",
    11: "left_knee",
    12: "right_knee",
    13: "left_foot",
    14: "right_foot"
}

SKELETON_TRACKED = 2
FRAME_W, FRAME_H = 640, 480

# Lista de websockets conectados
clients = set()
skeleton_data = {}  # Último frame procesado

def joint_to_pixel(joint):
    """Convierte coordenadas del joint a píxeles de la ventana."""
    scale = 0.9
    px = int(FRAME_W / 2 + joint.position.x * scale / 2)
    py = int(FRAME_H / 2 - joint.position.y * scale / 2)
    return (px, py)

async def ws_handler(websocket, path):
    """Maneja nuevos clientes WebSocket."""
    clients.add(websocket)
    print("Cliente conectado:", websocket.remote_address)
    try:
        while True:
            await asyncio.sleep(0.03)  # ~30 FPS
            if skeleton_data:
                await websocket.send(json.dumps(skeleton_data))
    except websockets.exceptions.ConnectionClosed:
        print("Cliente desconectado:", websocket.remote_address)
    finally:
        clients.remove(websocket)

async def start_ws_server():
    """Inicia servidor WebSocket."""
    server = await websockets.serve(ws_handler, "0.0.0.0", 8765)
    print("Servidor WebSocket escuchando en ws://localhost:8765")
    await server.wait_closed()

async def kinect_loop():
    """Captura datos del Kinect y actualiza skeleton_data."""
    global skeleton_data
    while True:
        # Imagen RGB
        color_frame = color_stream.read_frame()
        color_data = np.frombuffer(color_frame.get_buffer_as_uint8(), dtype=np.uint8)
        color_data = color_data.reshape((FRAME_H, FRAME_W, 3))
        frame_bgr = cv2.cvtColor(color_data, cv2.COLOR_RGB2BGR)

        # Tracking usuario
        user_frame = user_tracker.read_frame()
        for user in user_frame.users:
            if user.is_new():
                user_tracker.start_skeleton_tracking(user.id)
            elif user.skeleton.state == SKELETON_TRACKED:
                joints = user.skeleton.joints
                json_joints = {}

                # Guardar todos los joints
                for jid, name in JOINT_NAMES.items():
                    if joints[jid].positionConfidence > 0.5:
                        px, py = joint_to_pixel(joints[jid])
                        z = joints[jid].position.z  # Distancia en mm
                        json_joints[name] = {
                            "x": px,
                            "y": py,
                            "z": z
                        }

                skeleton_data = {"user_id": user.id, "joints": json_joints}

                # Dibujar esqueleto
                for (j1, j2) in [
                    (0, 1), (1, 2), (1, 3), (2, 4), (3, 5),
                    (4, 6), (5, 7), (2, 8), (3, 8), (8, 9),
                    (8, 10), (9, 11), (10, 12), (11, 13), (12, 14)
                ]:
                    if joints[j1].positionConfidence > 0.5 and joints[j2].positionConfidence > 0.5:
                        p1 = joint_to_pixel(joints[j1])
                        p2 = joint_to_pixel(joints[j2])
                        cv2.line(frame_bgr, p1, p2, (0, 0, 255), 2)

        cv2.imshow("Kinect v1 - WebSocket Skeleton", frame_bgr)
        if cv2.waitKey(1) & 0xFF == 27:
            break
        await asyncio.sleep(0)  # Cede control al loop asyncio

# Ejecutar Kinect + WebSocket en paralelo
loop = asyncio.get_event_loop()
loop.create_task(kinect_loop())
loop.run_until_complete(start_ws_server())

color_stream.stop()
nite2.shutdown()
openni2.shutdown()
cv2.destroyAllWindows()