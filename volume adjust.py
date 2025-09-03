import math
import cv2
import mediapipe as mp
import numpy as np
import time
import HandTrackingModule as htm

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# CAMERA DIMENSIONS
Wcam, Hcam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, Wcam)
cap.set(4, Hcam)
pTime = 0

# Initialize hand detector
detector = htm.handDetector(detectionCon=0.8)

# Initialize audio interface using pycaw
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Get volume range
minVol, maxVol, volStep = volume.GetVolumeRange()
print(f"Volume Range: {minVol}, {maxVol}")


while True:
    success, img = cap.read()
    if not success:
        continue

    img = detector.findHands(img)
    lmList = detector.findPosition(img, draw=False)

    if lmList:
        # Get coordinates of thumb tip (id 4) and index finger tip (id 8)
        x1, y1 = lmList[4][1], lmList[4][2]
        x2, y2 = lmList[8][1], lmList[8][2]
        cx, cy = int((x1 + x2) / 2), int((y1 + y2) / 2)

        # CIRCLE BETWEEN THE TIP OF THE FINGERS

        cv2.circle(img, (x1, y1), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED)
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
        cv2.circle(img, (cx, cy), 10, (0, 0, 255), cv2.FILLED)

        #  total distance between the finger tips
        length = math.hypot(x2 - x1, y2 - y1)

        # hand distance from volume range
        vol = np.interp(length, [20, 200], [minVol, maxVol])  # Adjust [20,200] based on your setup
        volume.SetMasterVolumeLevel(vol, None)

        if length < 40:
            cv2.circle(img, (cx, cy), 15, (0, 255, 0), cv2.FILLED)

        #VOLUME BAR
        volBar = np.interp(length, [20, 200], [400, 150])
        volPerc = np.interp(length, [20, 200], [0, 100])
        cv2.rectangle(img, (50, 150), (85, 400), (0, 0, 255), 2)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (0, 0, 255), cv2.FILLED)
        cv2.putText(img, f'{int(volPerc)} %', (40, 430), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 3)

    # FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, f'FPS: {int(fps)}', (40, 45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 3)
    cv2.imshow('Image', img)
    cv2.waitKey(1)
