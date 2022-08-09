import json
import os
from datetime import datetime
from threading import Thread

import cv2
import mediapipe as mp
from time import time as timer
import cvzone
import numpy as np
from flask import Flask, render_template, Response, request, jsonify

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
ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)

# is the song playing
isPlaying = False
# are we recording
isRecording = False
# are we viewing playback
isPlayingRecording = True
isPlaybackDone = False
# name for the latest recording
recording_name = ''
# get directory name
directory = os.getcwd()


def hand_tracking(camera_frame):
    image_rgb = cv2.cvtColor(camera_frame, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)
    # adds number to fi
    fontScale = int(1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    # print(results.multi_hand_landmarks)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = camera_frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)

                if id == 4:
                    cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "T", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 8:
                    cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "1", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 12:
                    cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "2", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 16:
                    cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "3", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 20:
                    cv2.circle(camera_frame, (cx, cy), 20, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "4", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

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
    global isRecording
    global isPlaying  # use global isPlaying variable
    global recording_name
    isPlaying = True
    game_over = False

    camera = cv2.VideoCapture(1)  # CHANGE BACK TO CAM 0
    is_playing = True
    frets_ready = False
    song_minutes = 4
    song_seconds = 30
    song_total_seconds = song_minutes * 60 + song_seconds

    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))

    # get project path/directory
    absolute_path = os.path.abspath(__file__)
    # current date and time
    now = datetime.now()
    # update current name
    recording_name = os.path.dirname(absolute_path) + '/_recordings/' + now.strftime("%m_%d_%Y_%H_%M_%S") + '.avi'
    print(recording_name)
    # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
    out = cv2.VideoWriter(recording_name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 30, (frame_width, frame_height))

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
    prevTime = timer()

    while not game_over:
        while song_total_seconds > 0 and isPlaying:
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

            # only write to file if we are recording
            if isRecording:
                out.write(frame)

            # encode to jpg and render to screen
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            currTime = timer()

            # has sec passed
            if currTime - prevTime >= 1:
                prevTime = currTime
                song_total_seconds = song_total_seconds - 1
        # game_over = True  # end game loop


reset_recording = False


def play_recording():
    global isPlayingRecording
    global recording_name
    global reset_recording
    global isPlaybackDone
    game_over = False
    elapsed = int()
    camera = cv2.VideoCapture(recording_name)
    fps = camera.get(cv2.CAP_PROP_FPS)
    print(fps)
    fps /= 1000
    framerate = timer()

    start = timer()

    while not game_over:
        if reset_recording:
            print('resetting vid')
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            reset_recording = False

        while isPlayingRecording:
            # start reading camera frames
            success, frame = camera.read()

            # handle camera err
            if not success:
                # print('playback done')
                isPlaybackDone = True
                break

            # encode to jpg and render to screen
            ret, buffer = cv2.imencode('.jpg', frame)

            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            cv2.waitKey(1)

            diff = timer() - start
            while diff < fps:
                diff = timer() - start

            elapsed += 1
            if elapsed % 5 == 0:
                print('\r')
                #print('{0:3.3f} FPS'.format(elapsed / (timer() - framerate)))



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/play_page')
def play_page():
    return render_template('play_page.html')


@app.route('/camera_feed')
def camera_feed():
    return render_template('camera_feed.html')


@app.route('/view_recording')
def view_recording():
    camera = cv2.VideoCapture(recording_name)
    fps = camera.get(cv2.CAP_PROP_FPS)  # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    print(duration)
    data = {'duration': duration}
    return render_template('view_recording.html', data=data)


@app.route('/toggle_record', methods=['POST'])
def toggle_record():
    global isRecording
    isRecording = not isRecording
    return jsonify({'recording': isRecording, 'url': 'song_completed'})


@app.route('/toggle_play', methods=['POST'])
def toggle_play():
    global isPlaying
    isPlaying = not isPlaying
    return jsonify(isPlaying)


@app.route('/toggle_play_recording', methods=['POST'])
def toggle_play_recording():
    global reset_recording
    reset_recording = not reset_recording
    return jsonify(reset_recording)


@app.route('/video_camera')
def video_camera():
    return Response(start_song(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/recording_feed')
def recording_feed():
    return Response(play_recording(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/thebeatlesplaypage.html')
def thebeatlesplaypage():
    return render_template('thebeatlesplaypage.html')


@app.route('/song_completed')
def song_completed():
    return render_template('song_completed.html')


@app.route('/playback_time_check', methods=['POST'])
def playback_time_check():
    return jsonify(isPlaybackDone)


if __name__ == '__main__':
    app.run()
