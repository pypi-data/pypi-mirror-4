import os
import subprocess
import time
import select

import Image
import v4l2capture

from config import *


def capture(directory, video_device='/dev/video0',
            resolution=[1280, 1024], image_ext='png',
            buffers=1):

    image_resolution = [int(resolution[0]),
                        int(resolution[1])]
    video = v4l2capture.Video_device(video_device)

    size_x, size_y = video.set_format(*image_resolution)

    video.create_buffers(buffers)

    video.queue_all_buffers()

    video.start()

    select.select((video,), (), ())

    image_data = video.read()
    image_name = "%s.%s" % (str(time.time()).split('.')[0], image_ext)
    full_path = os.path.join(directory, image_name)
    video.close()
    image = Image.fromstring("RGB", (size_x, size_y), image_data)
    image.save(full_path)


def create_timelapse(args):
    while True:
        capture(CAPTURES_PATH, **args)
        time.sleep(DELAY)


def generate_video(videos_path, captures_path, delay=20):
    captures_dir = os.path.join(captures_path, '*.%s' % IMAGE_EXT)
    videos_dir = os.path.join(videos_path, 'outvideo.mpeg')
    command = 'convert -delay %d -loop 0 -scale %s %s %s' % (delay, '50%',
                                                             captures_dir,
                                                             videos_dir)
    subprocess.call(command, shell=True)
