=======
PyLapse
=======

A simple application to build timelapses using a webcam, V4l2 and ImageMagick


Install
=======

    $ cd pylapse
    $ pip-2.7 -r requirements.txt --upgrade

Or setup a virtualenv environment with...

    $ virtualenv2 venv  --distribute ; Maybe you need just virtualenv
    $ venv/bin/activate
    $ pip -r install requirements.txt --upgrade


Install ImageMagick with:

ArchLinux

    # pacman -S imagemagick

Debian/Ubuntu

    # apt-get install imagemagick


Configuration
=============


After installing you can go to your home and change the current
captures and videos paths. The configuration is in $HOME/.pylapse/config.cfg

By default the captures and videos will stored in $HOME/.pylapse/captures and
$HOME/.pylapse/videos respectively.

You can add your own configuration below the [pylapse] tag.


Usage
=====

You can define the variables for the captures and video generation in `config.py`.

Then you can create the images with:

    $ pylapse capture

Then you could generate the video with:

    $ pylapse video

You can access the program help:

    $ pylapse  -h ; Global help information
    $ pylapse capture -h ; Capture Image Help
    $ pylapse video -h ; Video generation help

Have fun! :-)
