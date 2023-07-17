Video Keyframe Server
=====

Video Keyframe Server is a Django-based HTTP server that uses ffprobe and ffmpeg to extract [keyframes](https://en.wikipedia.org/wiki/Video_compression_picture_types)
and [group-of-pictures](https://en.wikipedia.org/wiki/Group_of_pictures) from a video and dispay them in different ways:
- I-Frames return as JSON indicating where a group-of-pictures begins
- Display a single group-of-pictures as a video
- Display all group-of-pictures as a grid of videos

Information on the environment, running Video Keyframe Server, and available endpoints / functionality can be found at the end of this README in the "Usage" section.

# Overview

Video Keyframe Server is implemented as a Django project with one app, "videos". Noteworthy source code files and directory structures are detailed below.

## Source code files:

- `videos.py` <br>
Handles rendering to views as well as logic to create those views.
As noted in that file's TODO, a future refactor should move that logic to a different module and/or classes.
- `videos_ffmpeg` <br>
Module wrapping the `ffmpeg` library, as well as calling `ffmpeg` directly as a subprocess. Currently called by the view.
- `templates/videos/*html`
Django templates used by the view.
- `urls.py` <br>
Maps endpoints to the view.
- `videosite/videosite/settings.py` <br>
Informs Django of the "videos" app (`INSTALLED_APPS`). Also defines settings used by app code, such as `static`, `VIDEOS_STATIC_ROOT`, and `VIDEOS_MEDIA_ROOT`.
- `videosite/videosite/urls.py` <br>
Adds the "videos" app and defines a custom 404 page (only works in production).

## Directories
- `static\videos` <br>
MP4 file(s) used by Video Keyframe Server, such as "CoolVideo.mp4"
- `static\videos\media` <br>
Temporary MP4 files created by Video Keyframe Server when endpoints are accessed. Currently needs to be manually cleaned up.

## Implementation notes

### Design decisions

Per the Overview, Video Keyframe Server is implemented as a Django project with one app, "videos". While this is my first Django project -- my previous experience with
Python is with Blender Add-Ons -- I tried to be as idiomatic as possible.

I initially wanted to use the [ffmpeg-python](https://github.com/kkroening/ffmpeg-python) library rather than using a Python subprocess and calling `ffmpeg` directly.
However, while ffmpeg-python supports ffmpeg "trim" operations out-of-the-box, I couldn't figure out how to get it to support "copy" operations; it was easier and cleaner
just to call `ffmeg`. Trimming involves re-encoding the output video, which is slow. Copying is newer ffmpeg functionality that allows slices of video to be created without
re-encoding the output.

### Responding to future feature requests

As noted in both this README and view.py itself... the view has gotten very "chunky". It has logic for creating the views that should be moved to a separate module and/or
classes. This refactor should be done _first_, before any new features are added.

After the above refactor is complete, follow this general pattern:
1. Add a new route / endpoint to `urls.py`
1. Implement the endpoint in `videos.py`; the code here should be minimal moving foward
1. Add logic for the view in whatever module/class(es) were produced from the refactor above
1. If needed, add a new template to `templates/videos/*html`
1. If needed, add new ffprobe / ffmpeg functionality to the `videos_ffmpeg` module

### Adding support for dynamically cropping and filtering videos, with parameters supplied via a query string

I would add each new feature as its own module/class, rather than trying to come up with a magically generic way to handle query string functionality. That is, cropping would
have its own module / class, filtering would have its own module / class, etc:
- Cleaner code that uses a SOLID (single responsibilty) approach
- Easier to document
- Helps avoid security issues because we can more easily whitelist incoming parameters as new functionality as added

### Performance

The key performance issues are:
- Video Keyframe Server handles requests synchronously
- The app uses Django's development HTTP server instead of a standalone server
- Since this a development environment, there's currently no load balancing

Using Python to working with ffmpeg seems to be more-or-less industry standard (e.g., [Runway](https://runwayml.com/) "Magic Tools" seem to do this). However, using Node.js
might make scaling up easier, as Node is built from the ground-up to handle requests asynchronously.

While not a perfomance issue per se, `static\videos\media` currently needs to be manually cleaned up.

# Usage

## Running

Note: Only tested on my Windows 10 development machine.

`cd /parent/directory/to/VideoKeyframeServer`

Activate the Python virtual environment:
Windows:
`VideoKeyframeServer\Scripts\activate.bat`
macOS and Linux:
`source VideoKeyframeServer/bin/activate`

Run the Django development server:
`python manage.py runserver`

## Endpoints

Endpoint returning an HTML page containing a grid of all the groups of pictures in playable video elements and their timestamps.
Example:<br>
http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures

Endpoint returning JSON-encoded data showing details of all the I-frames in a video. <br>
Example:<br>
http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures.json

Endpoint returning an MP4 file containing the video data for the group of pictures requested (zero-indexed). <br>
Example:<br>
http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures/0

## Example output

<img src="README-VideoKeyframeServer-screenshot-grid.png" width="938"/>

<img src="README-VideoKeyframeServer-screenshot-json.png" width="938"/>

<img src="README-VideoKeyframeServer-screenshot-gop.png" width="938"/>
