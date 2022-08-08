import cv2
import mediapipe as mp
import time
import cvzone
import numpy as np
from flask import Flask, render_template, Response

from Fret import Fret

app = Flask(__name__)

# COLORS
COLOR_GREEN = (140, 234, 153)
# camera = cv2.VideoCapture(0)

# hand tracking start
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
# images for overlay & size
logo = cv2.imread("static/images/Group 3.png")
height = 150
width = 1270
logo = cv2.resize(logo, (width, height))
img2gray = cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 5, 255, cv2.THRESH_BINARY)



def hand_tracking(camera_frame):
    image_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    # adds number to fi
    fontScale = int (1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                        h, w, c = camera_frame.shape
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        print(id, cx, cy)

                        if id == 4:
                            cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                            cv2.putText(camera_frame, "T", (cx - 8, cy+10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA )

                        if id == 8:
                            cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                            cv2.putText(camera_frame, "1", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                        if id == 12:
                            cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                            cv2.putText(camera_frame, "2", (cx - 8, cy+10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                        if id == 16:
                            cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                            cv2.putText(camera_frame, "3", (cx - 8, cy+10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                        if id == 20:
                            cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                            cv2.putText(camera_frame, "4", (cx - 8, cy+10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                mpDraw.draw_landmarks(camera_frame, handLms, mpHands.HAND_CONNECTIONS)


def fret_overlay(frame):
    # Region of Image (ROI), where we want to insert logo
    roi = frame[-height - 10:-10, -width - 10:-10]
    roi[np.where(mask)] = 0
    roi += logo


def render_frets(frame, frets):
    for fret in frets:
        # only move and print if circle has not moved out of screen
        if fret.x > -fret.radius:
            # update x pos - moves right to left
            fret.update_x()
            # create circle
        else:
            fret.reset(frame.shape[1], frame.shape[0])
        cv2.circle(frame, (fret.x, fret.y), fret.radius, COLOR_GREEN, -1)



# Starts the playing the song
# Once total song time length has elapsed,
# end game
def start_song():
    camera = cv2.VideoCapture(0)  # CHANGE BACK TO CAM 0
    is_playing = True
    frets_ready = False
    song_minutes = 4
    song_seconds = 30
    song_total_seconds = song_minutes * 60 + song_seconds

    # create frets
    frets = [
        Fret(2000, 300, 15, 1),
        Fret(2000, 200, 15, 2),
        Fret(2000, 300, 15, 3),
        Fret(2000, 300, 15, 4),
        Fret(2000, 300, 15, 5),
        # Fret(2000, 300, 15, 6),
    ]

    # get start time
    prevTime = time.time()

    while song_total_seconds > 0:
        # start reading camera frames
        success, frame = camera.read()

        # handle camera err
        if not success:
            is_playing = False
            break

        if not frets_ready:
            for fret in frets:
                fret.reset(frame.shape[1], frame.shape[0])
            frets_ready = True

        # adds fret overlay to video feed
        fret_overlay(frame)

        hand_tracking(frame)
        render_frets(frame, frets)

        # encode to jpg and render to screen
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        currTime = time.time()

        # has sec passed
        if currTime - prevTime >= 1:
            prevTime = currTime
            song_total_seconds = song_total_seconds - 1



    print('done')












# def gen_frames():
#     while True:
#         success, frame = camera.read()
#         if not success:
#             break
#         else:
#             hand_tracking(frame)
#             fret_overlay(frame)
#             greendots(frame, circlex)
#             ret, buffer = cv2.imencode('.jpg', frame)
#             frame = buffer.tobytes()
#             yield (b'--frame\r\n'
#                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play_page')
def play_page():
    return render_template('play_page.html')


@app.route('/camera_feed')
def camera_feed():
    return render_template('camera_feed.html')


@app.route('/video_camera')
def video_camera():
    return Response(start_song(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/thebeatlesplaypage.html')
def thebeatlesplaypage():
    return render_template('thebeatlesplaypage.html')

@app.route('/record_replay.html')
def record_replay():
    return render_template('record_replay.html')

if __name__ == '__main__':
    app.run()
