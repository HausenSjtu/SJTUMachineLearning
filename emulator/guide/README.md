### What is this repository for? ###

This repository provides code to access the Fceux emulator using lua on the Emulator side to communicate with the emulator and python to communicate with the lua code.

This code can technically work for any rom to control the character, but we currently only implemented Super Mario Bros. which is also the main game for our topic.

It was done for th Machine Learning Class of SJTU in 2015.

### How do I get set up? ###

####Dependencies####

You first need to download Fceux.
On Windows refer to [this](http://sourceforge.net/projects/fceultra/files/Binaries/2.2.2/fceux-2.2.2-win32.zip/download) link.

Moreover we use [OpenCV](http://opencv.org/downloads.html) as our image frontend processing library.

If you use windows , please download and install [PyWin](http://sourceforge.net/projects/pywin32/files/pywin32/).
##### Linux #####
For Linux, if youre on debian based distributions just run:
```
#!bash

sudo apt-get install fceux
```
For other distributions please refer to your package manager (e.g. yum or pacman)

Moreover you need OpenCV.

Run:

```
#!bash

sudo apt-get install python-opencv
```
##### Windows #####

Please better not use Windows! Install Linux/MacOSx

You need to [install Lua](https://code.google.com/p/luaforwindows/) on your system and [python](https://www.python.org/ftp/python/2.7.9/Python-2.7.9.tar.xz).

####Downloading a rom####

Currently we recommend to somewhere get a Mario rom. We can provide [ours](http://www77.zippyshare.com/v/pnoVz5WZ/file.html).

####Running the code####

Put the mario.nes file into your cloned directory.
Simply execute

```
#!bash

python mario.py
```

or 

```
#!bash

mario.py
```
on windows, if python is in your PATH (default).

On windows you might need to specify the directory of Fceux. As default we expect having a directory in the cloned directory called fceux-2.2.2-win32.
If it is any other directory please open up emulator.py and change in the class WinEmulator the attribute FCEUX_BASEDIR to your directory.

If any errors occur, make sure the file is called mario.nes and that it is in the same directory.

###Extending the Code###

We provide already a template in the file *Mario.py* how to use Mario to do certain actions.

Mario has certain attributes to control him:

* self.BUTTON_UP
* self.BUTTON_UP
* self.BUTTON_DOWN
* self.BUTTON_LEFT
* self.BUTTON_RIGHT
* self.BUTTON_A
* self.BUTTON_B

And some buttons to control the game flow:

* self.BUTTON_START
* self.BUTTON_SELECT
* self.SOFTRESET