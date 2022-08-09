import vlc
import time

sound_file = vlc.MediaPlayer("file:///static/mp3music/BlackBird.mp3")
sound_file.play()
time.sleep(10)

#sound_file.stop()