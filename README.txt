* Creating the virtual Python environment

cd /parent/directory/to/VideoKeyframeServer
python -m venv VideoKeyframeServer


* Activating and deactivating the virtual environment

Activating (Windows):
VideoKeyframeServer\Scripts\activate.bat

Activating (macOS and Linux):
source VideoKeyframeServer/bin/activate

Deactivating:
From within the virtual environment, you can deactivate it by executing:
deactivate


* Dependencies:

Django: python -m pip install Django
ffmpeg-python: pip install ffmpeg-python
