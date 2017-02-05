#! /bin/bash

raspivid --bitrate 800000 -o testvideo.h264 --timeout 25000 --framerate 5 --save-pts timecodes.txt
mediainfo --full testvideo.h264
mkvmerge -o testvideo.mkv --timecodes 0:timecodes.txt testvideo.h264

