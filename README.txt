NOTE: These steps are only required if you are creating VideoKeyframeServer from scratch.

** Creating the environment

cd /parent/directory/to/VideoKeyframeServer
python -m venv VideoKeyframeServer

Activate the vitual environment (see below) and install dependencies:

Django: python -m pip install Django
ffmpeg-python: pip install ffmpeg-python


** Activating and deactivating the virtual environment

Activating (Windows):
VideoKeyframeServer\Scripts\activate.bat

Activating (macOS and Linux):
source VideoKeyframeServer/bin/activate

Deactivating:
From within the virtual environment, you can deactivate it by executing:
deactivate


* Running:

cd VideoKeyframeServer/videosite
python manage.py runserver
