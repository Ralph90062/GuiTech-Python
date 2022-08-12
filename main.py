import json
import math
import os
from datetime import datetime
from threading import Thread

import cv2
import mediapipe as mp
from time import time as timer, sleep
import cvzone
import numpy as np
from flask import Flask, render_template, Response, request, jsonify
from numpy import unicode

from Fret import Fret, Fret_Set
from utils import utilsVideo

app = Flask(__name__)

# COLORS
COLOR_GREEN = (152, 234, 140)
COLOR_BLACK = (0, 0, 0)
COLOR_GREY = (115, 115, 113)
# camera = cv2.VideoCapture(0)

# hand tracking start
mpHands = mp.solutions.hands
hands = mpHands.Hands()
mpDraw = mp.solutions.drawing_utils
# images for overlay & size
logo = cv2.imread("static/images/GuitarFrets_3.png")
height = 190
width = 1270
logo = cv2.resize(logo, (width, height))
img2gray= cv2.cvtColor(logo, cv2.COLOR_BGR2GRAY)
ret, mask = cv2.threshold(img2gray, 0, 255, cv2.THRESH_BINARY)

# is the song playing
isPlaying = False
# are we recording
isRecording = False
# are we viewing playback
isPlayingRecording = True
isPlaybackDone = False
# name for the latest recording
recording_name = '_recordings/08_11_2022_21_23_59.avi'
# get directory name
directory = os.getcwd()
render_ok = False

def hand_tracking(camera_frame):
    global render_ok
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
                print(cy)

                if (cy < 400):
                    render_ok = True
                else:
                    render_ok = False

                if id == 4:


                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "T", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 8:
                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "1", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 12:
                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "2", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 16:
                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "3", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

                if id == 20:
                    cv2.circle(camera_frame, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
                    cv2.putText(camera_frame, "4", (cx - 8, cy + 10), font, fontScale, (255, 255, 255), 2, cv2.LINE_AA)

            mpDraw.draw_landmarks(camera_frame, handLms, mpHands.HAND_CONNECTIONS)
    else:
        render_ok = False

def fret_overlay(frame, frame_height, frame_width):
    # Region of Image (ROI), where we want to insert logo
    # roi = frame[-height - 10:-10, -width - 10:-10]
    # roi[np.where(mask)] = 0
    # roi += logo

    cv2.line(frame, (0, frame_height - 50), (frame_width, frame_height - 50), COLOR_BLACK, 2)
    cv2.line(frame, (0, frame_height - 82), (frame_width, frame_height - 82), COLOR_BLACK, 2)
    cv2.line(frame, (0, frame_height - 112), (frame_width, frame_height - 112), COLOR_BLACK, 2)
    cv2.line(frame, (0, frame_height - 142), (frame_width, frame_height - 142), COLOR_BLACK, 2)
    cv2.line(frame, (0, frame_height - 173), (frame_width, frame_height - 173), COLOR_BLACK, 2)
    cv2.line(frame, (0, frame_height - 203), (frame_width, frame_height - 203), COLOR_BLACK, 2)

    cv2.line(frame, (frame_width - 27, frame_height - 30), (frame_width - 27, frame_height - 215),
             COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 130, frame_height - 30), (frame_width - 130, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 240, frame_height - 30), (frame_width - 240, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 360, frame_height - 30), (frame_width - 360, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 480, frame_height - 30), (frame_width - 480, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 610, frame_height - 30), (frame_width - 610, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 744, frame_height - 30), (frame_width - 744, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 880, frame_height - 30), (frame_width - 880, frame_height - 215), COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 1016, frame_height - 30), (frame_width - 1016, frame_height - 215),
             COLOR_BLACK, 2)
    cv2.line(frame, (frame_width - 1150, frame_height - 30), (frame_width - 1150, frame_height - 215), COLOR_BLACK, 2)


def render_frets(frame, frets, time_elapsed):
    for fret_set_index, fret_set in enumerate(frets):
        fret_set.animate_frets(frame)


# Starts the playing the song
# Once total song time length has elapsed,
# end game

def render_Ok(frame):

    font_scale = int(1)
    font = cv2.FONT_HERSHEY_SIMPLEX
    x = frame.shape[1] - 80
    y = frame.shape[0] - 400
    if render_ok:
        cv2.circle(frame, (x, y), 50, (69, 195, 9), cv2.FILLED)
        cv2.putText(frame, 'OK', (x - 22, y + 10), font, font_scale, (255, 255, 255), 2, cv2.LINE_AA)


def start_song():
    global isRecording
    global isPlaying  # use global isPlaying variable
    global recording_name
    isPlaying = True
    game_over = False
    global curr_position

    camera = cv2.VideoCapture(1)  # CHANGE BACK TO CAM 0

    is_playing = True
    frets_ready = False
    song_minutes = 4
    song_seconds = 30
    song_total_seconds = song_minutes * 60 + song_seconds
    time_elapsed = 0

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
    out = cv2.VideoWriter(recording_name, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), 15, (frame_width, frame_height))

    frets = [
        Fret_Set('g_chord', 0),
        Fret_Set('c_chord', 1),
        Fret_Set('g_chord', 2),
        Fret_Set('c_chord', 3),
        Fret_Set('c_chord', 4),
        Fret_Set('g_chord', 5),
        Fret_Set('g_chord', 6),
        Fret_Set('c_chord', 7),
        Fret_Set('g_chord', 8),
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
                for fret_set in frets:
                    fret_set.prep_frets(frame)
                frets_ready = True

            # adds fret overlay to video feed

            hand_tracking(frame)
            fret_overlay(frame, frame_height, frame_width)
            render_frets(frame, frets, time_elapsed)
            render_Ok(frame)


            # only write to file if we are recording
            if isRecording:
                out.write(frame)

            # encode to jpg and render to screen
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

            cv2.waitKey(1)

            currTime = timer()

            # has sec passed
            if currTime - prevTime >= 1:
                prevTime = currTime
                song_total_seconds = song_total_seconds - 1
                time_elapsed = time_elapsed + 1


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
    frame_width = int(camera.get(3))
    frame_height = int(camera.get(4))

    start = timer()

    uv = utilsVideo(camera)
    (fps, frame_count, durationSec) = uv.getStats()
    print("Total time: {}sec FrameRate: {} FrameCount: {}".format(durationSec, fps, frame_count))


    while not game_over:
        if reset_recording:
            print('resetting vid')
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
            reset_recording = False
            isPlaybackDone = False

        while isPlayingRecording:
            # start reading camera frames
            success, frame = camera.read()

            # handle camera err
            if not success:
                # print('playback done')
                isPlaybackDone = True
                break

            nextFrameNo = camera.get(cv2.CAP_PROP_POS_FRAMES)
            # get total number of frames in the video
            totalFrames = camera.get(cv2.CAP_PROP_FRAME_COUNT)
            # calculate the percent complete based on the frame currently
            # playing. OpenCV does provide a variable to access this
            # property directly (CAP_PROP_POS_AVI_RATIO), however
            # it seems to not work all the time, hence we calculate internally
            complete = nextFrameNo / totalFrames

            # progress bar thickness
            lineThickness = 3
            # progress bar will be displayed 4% from the bottom of the frame
            y = math.ceil(frame_height - 8)
            # display progress bar across the width of the video
            x = math.ceil((frame_width * (1/4))) + 180 #
            w = math.ceil((frame_width * (1/4))) + 440
            # white line as background for progressb + 50 ar

            # red line as progress on top of that

            redX = math.ceil((w-x) * complete) + x

            print(redX)
            #
            if redX > w-1:
                redX = w

            print(redX)
            cv2.line(frame, (x, y), (w-1, y), (255, 255, 255), lineThickness)
            cv2.line(frame, (x, y), (redX, y), (0, 0, 255), lineThickness)


            # encode to jpg and render to screen
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            key = cv2.waitKey(45)
            # key = cv2.waitKey(35)
            #
            # diff = timer() - start
            # while diff < fps:
            #     diff = timer() - start
            #
            # elapsed += 1
            # if elapsed % 5 == 0:
            #     print('\r')
            #     print('{0:3.3f} FPS'.format(elapsed / (timer() - framerate)))



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
    print(recording_name)
    camera = cv2.VideoCapture(recording_name)
    fps_s = camera.get(cv2.CAP_PROP_FPS)  # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(camera.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps_s
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
