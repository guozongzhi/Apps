# main.py
# 作者: Gemini 资深 Python 计算机视觉工程师
# 日期: 2025-11-22
#
# 描述:
# 该脚本使用网络摄像头进行实时手势识别。
# 它利用 OpenCV 进行图像捕捉和渲染，并使用 MediaPipe 进行稳健的手部跟踪和关键点检测。
# 该脚本可以识别多种手势，包括数字和基本手势。

import cv2
import mediapipe as mp
import numpy as np
import math

def calculate_angle(a, b, c):
    """
    计算三点之间的角度（单位：度）。
    点 'b' 是角度的顶点。
    """
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle

def recognize_gesture(hand_landmarks):
    """
    使用角度计算从检测到的手部关键点中识别特定手势。
    此版本增加了对数字1, 2, 3, 4的识别。
    """
    landmarks = hand_landmarks.landmark
    
    finger_joints = {
        'index': (5, 6, 8), 'middle': (9, 10, 12),
        'ring': (13, 14, 16), 'pinky': (17, 18, 20)
    }
    finger_angles = {}
    for finger, joints in finger_joints.items():
        mcp = [landmarks[joints[0]].x, landmarks[joints[0]].y]
        pip = [landmarks[joints[1]].x, landmarks[joints[1]].y]
        tip = [landmarks[joints[2]].x, landmarks[joints[2]].y]
        angle = calculate_angle(mcp, pip, tip)
        finger_angles[finger] = angle

    thumb_angle = calculate_angle(
        [landmarks[2].x, landmarks[2].y],
        [landmarks[3].x, landmarks[3].y],
        [landmarks[4].x, landmarks[4].y]
    )
    is_thumb_straight = thumb_angle > 160.0

    fingers_straight = [
        finger_angles['index'] > 160.0, finger_angles['middle'] > 160.0,
        finger_angles['ring'] > 160.0, finger_angles['pinky'] > 160.0
    ]
    
    is_thumb_pointing_up = landmarks[4].y < landmarks[3].y and landmarks[4].y < landmarks[5].y
    if is_thumb_straight and not any(fingers_straight) and is_thumb_pointing_up:
        return "Thumbs Up"

    if not is_thumb_straight:
        if fingers_straight == [True, False, False, False]: return "1"
        if fingers_straight == [True, True, False, False]: return "2"
        if fingers_straight == [True, True, True, False]: return "3"
        if fingers_straight == [True, True, True, True]: return "4"

    if is_thumb_straight and all(fingers_straight):
        return "Open Palm"
    if not is_thumb_straight and not any(fingers_straight):
        return "Closed Fist"
    
    return "Unknown"

def main():
    """
    主函数，负责捕获视频、处理视频并显示输出。
    """
    print("Initializing computer vision components...")

    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands(
        max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    mp_drawing_styles = mp.solutions.drawing_styles

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Cannot open camera. Please check if a webcam is connected.")
        return

    window_name = 'Real-Time Gesture Recognition'
    print(f"Initialization complete. Press 'q' or click the 'X' on the '{window_name}' window to quit.")

    # --- 主循环 ---
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_flipped = cv2.flip(image_rgb, 1)
        results = hands.process(image_flipped)
        
        image.flags.writeable = True
        image = cv2.cvtColor(image_flipped, cv2.COLOR_RGB2BGR)

        # --- 手势识别与可视化 ---
        gesture_name = "No Hand Detected"
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
                gesture_name = recognize_gesture(hand_landmarks)
        
        # --- 显示信息 ---
        cv2.putText(
            image, f'Gesture: {gesture_name}', (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3, cv2.LINE_AA)

        # 显示最终图像
        cv2.imshow(window_name, image)

        # --- 退出条件 ---
        key = cv2.waitKey(5) & 0xFF
        # 条件1: 按下 'q' 键
        if key == ord('q'):
            break
        # 条件2: 用户点击了窗口的 'X' 按钮
        # 当窗口被关闭时，WND_PROP_VISIBLE 属性会变为 < 1
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    # --- 清理 ---
    print("Shutting down...")
    hands.close()
    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()