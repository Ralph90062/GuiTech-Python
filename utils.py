# Video basics utility written by Pranjal Srivastava
# You can contact author on pranjal@codefire.in

# import required packages
import cv2
import math


# This class provides a way to easily access the basic paramenters of the video
# Also it adds a utility function to display progress bar on the video when
# displayed with OpenCV imshow function
class utilsVideo:
    # Ctor that takes following arguments
    # capture - video capture class object from OpenCV
    def __init__(self, capture):
        self.capture = capture

    # function used access and return basic details of the video
    def getStats(self):
        # get frames per seconds (fps) from the video
        fps = self.capture.get(cv2.CAP_PROP_FPS)
        # total frame counts
        frame_count = int(self.capture.get(cv2.CAP_PROP_FRAME_COUNT))
        # codec used to capture the video. This is useful when you are saving the
        # video to disc, currently not used anywhere
        # full parameter list at
        # https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html
        codec = self.capture.get(cv2.CAP_PROP_FOURCC)
        # total duraiton of video in milli seconds
        durationSec = frame_count / fps * 1000
        return (fps, frame_count, durationSec)

    # This function implements display of progress bar on video frame.
    # Parametes:
    # currentframe: the current frame of video to be saved. This frame
    #		will be modified by adding progress bar on top of it and
    #		returned to the caller

    def displayProgressBar(self, currentframe):
        # get next frame number out of all the frames for video
        nextFrameNo = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        # get total number of frames in the video
        totalFrames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT) - 250
        # calculate the percent complete based on the frame currently
        # playing. OpenCV does provide a variable to access this
        # property directly (CAP_PROP_POS_AVI_RATIO), however
        # it seems to not work all the time, hence we calculate internally
        complete = nextFrameNo / totalFrames

        # progress bar thickness
        lineThickness = 2
        # progress bar will be displayed 4% from the bottom of the frame
        y = math.ceil(currentframe.shape[1] - 75)
        # display progress bar across the width of the video
        x = 0
        w = currentframe.shape[0]
        # white line as background for progressbar
        cv2.line(currentframe, (x, y), (w, y), (255, 255, 255), lineThickness)
        # red line as progress on top of that
        cv2.line(currentframe, (x, y), (math.ceil(w * complete), y), (0, 0, 255), lineThickness)
