#!/bin/sh

# adjust camera here if needed
v4l2-ctl -d /dev/video0 -c exposure_auto=1 -c exposure_absolute=5

. /home/pi/.virtualenvs/cv/bin/activate
python /home/pi/2017-vision/hunt.py --release
