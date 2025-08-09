import cv2
import numpy as np
import win32api, win32con
from openni import openni2, nite2
import time
import math

# Inicializar OpenNI2 y NiTE2
openni2.initialize("C:/Program Files/OpenNI2/Redist")
nite2.initialize("C:/Program Files/PrimeSense/NiTE2/Redist")

# Abrir Kinect
dev = openni2.Device.open_any()
color_stream = dev.create_color_stream()
color_stream.start()

# Tracker de usuarios/esqueleto
user_tracker = nite2.UserTracker(dev)

# Articulaciones para el control
JOINT_RIGHT_HAND = 7
JOINT_LEFT_HAND = 6
JOINT_HEAD = 1
JOINT_LEFT_SHOULDER = 2


#0: HEAD 1: NECK 2: LEFT_SHOULDER 3: RIGHT_SHOULDER 4: LEFT_ELBOW 5: RIGHT_ELBOW 6: LEFT_HAND 7: RIGHT_HAND 8: TORSO 9: LEFT_HIP 10: RIGHT_HIP 11: LEFT_KNEE 12: RIGHT_KNEE 13: LEFT_FOOT 14: RIGHT_FOOT

SKELETON_TRACKED = 2

# Tamaño ventana
FRAME_W, FRAME_H = 640, 480
BOX_W, BOX_H = FRAME_W // 2, FRAME_H // 2
BOX_X1 = (FRAME_W - BOX_W) // 2
BOX_Y1 = (FRAME_H - BOX_H) // 2
BOX_X2 = BOX_X1 + BOX_W
BOX_Y2 = BOX_Y1 + BOX_H

# Tamaño de pantalla Windows
screen_w = win32api.GetSystemMetrics(0)
screen_h = win32api.GetSystemMetrics(1)

clicking = False
smooth_joints = {}
smooth_alpha = 0.2

# Umbral para activar click cuando la mano izquierda está cerca del cuello/cabeza (25 cm)
LEFT_HAND_CLICK_THRESHOLD = 350  # mm

scale = 0.9
prev_distance_left = None

def move_mouse_from_box(x, y):
    x = max(BOX_X1, min(x, BOX_X2))
    y = max(BOX_Y1, min(y, BOX_Y2))
    x_norm = (x - BOX_X1) / BOX_W
    y_norm = (y - BOX_Y1) / BOX_H
    win32api.SetCursorPos((int(x_norm * screen_w), int(y_norm * screen_h)))

def click_mouse(down=True):
    global clicking
    if down and not clicking:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        clicking = True
    elif not down and clicking:
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        clicking = False

def joint_to_pixel(joint):
    px = int(FRAME_W / 2 + joint.position.x * scale / 2)
    py = int(FRAME_H / 2 - joint.position.y * scale / 2)
    return (px, py)

def smooth_point(joint_id, new_point):
    if joint_id not in smooth_joints:
        smooth_joints[joint_id] = new_point
    else:
        old_x, old_y = smooth_joints[joint_id]
        new_x = old_x + smooth_alpha * (new_point[0] - old_x)
        new_y = old_y + smooth_alpha * (new_point[1] - old_y)
        smooth_joints[joint_id] = (new_x, new_y)
    return tuple(map(int, smooth_joints[joint_id]))

print("Control de mouse con mano derecha, click con mano izquierda (acercar al cuello).")

try:
    while True:
        color_frame = color_stream.read_frame()
        color_data = np.frombuffer(color_frame.get_buffer_as_uint8(), dtype=np.uint8)
        color_data = color_data.reshape((FRAME_H, FRAME_W, 3))
        frame_bgr = cv2.cvtColor(color_data, cv2.COLOR_RGB2BGR)

        user_frame = user_tracker.read_frame()
        for user in user_frame.users:
            if user.is_new():
                user_tracker.start_skeleton_tracking(user.id)
            elif user.skeleton.state == SKELETON_TRACKED:
                joints = user.skeleton.joints

                # Dibujar esqueleto
                for j1, j2 in [
                    (0, 1), (1, 2), (1, 3), (2, 4), (3, 5),
                    (4, 6), (5, 7), (2, 8), (3, 8), (8, 9),
                    (8, 10), (9, 11), (10, 12), (11, 13), (12, 14)
                ]:
                    if joints[j1].positionConfidence > 0.5 and joints[j2].positionConfidence > 0.5:
                        p1 = smooth_point(j1, joint_to_pixel(joints[j1]))
                        p2 = smooth_point(j2, joint_to_pixel(joints[j2]))
                        cv2.line(frame_bgr, p1, p2, (0, 0, 255), 2)

                # Control puntero con mano derecha
                right_hand = joints[JOINT_RIGHT_HAND]
                if right_hand.positionConfidence > 0.5:
                    hand_px = smooth_point(JOINT_RIGHT_HAND, joint_to_pixel(right_hand))
                    move_mouse_from_box(hand_px[0], hand_px[1])

                # Click con mano izquierda cerca del cuello (cabeza)
                left_hand = joints[JOINT_LEFT_HAND]
                shoulder = joints[JOINT_LEFT_SHOULDER]  # Usar hombro izquierdo como referencia

                if left_hand.positionConfidence > 0.5 and shoulder.positionConfidence > 0.5:
                    dx = left_hand.position.x - shoulder.position.x
                    dy = left_hand.position.y - shoulder.position.y
                    dz = left_hand.position.z - shoulder.position.z
                    distancia_3d_izquierda = math.sqrt(dx*dx + dy*dy + dz*dz)

                    # Activar click si la distancia es menor al umbral
                    if distancia_3d_izquierda < LEFT_HAND_CLICK_THRESHOLD:
                        click_mouse(True)
                        cv2.putText(frame_bgr, "CLICK ACTIVO", (20, 80),
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    else:
                        click_mouse(False)

                    cv2.putText(frame_bgr, f"Distancia mano-cuello: {distancia_3d_izquierda:.0f} mm",
                                (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        cv2.imshow("Kinect v1 - Mouse con click en cuello", frame_bgr)
        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    pass

color_stream.stop()
nite2.shutdown()
openni2.shutdown()
cv2.destroyAllWindows()