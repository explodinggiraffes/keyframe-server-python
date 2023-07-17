# Copyright 2023 John Koszarek

from django.urls import path

from . import views


urlpatterns = [
    # Endpoint returning an HTML page detailing the Video Keyframe Server endpoints.
    # Example: http://127.0.0.1:8000/videos/
    path("", views.index, name="index"),

    # Endpoint returning an HTML page containing a grid of all the groups of pictures in playable <video> elements and
    # their timestamps.
    # Example: http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures
    path("<str:video_filename>/group-of-pictures", views.video_elements, name="video_elements"),

    # Endpoint returning JSON-encoded data showing details of all the I-frames in a video.
    # Example: http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures.json
    path("<str:video_filename>/group-of-pictures.json", views.video_iframe_detail, name="video_iframe_detail"),

    # Endpoint returning an MP4 file containing the video data for the group of pictures requested (zero-indexed).
    # Example: http://127.0.0.1:8000/videos/CoolVideo.mp4/group-of-pictures/0
    path("<str:video_filename>/group-of-pictures/<int:group_of_pictures_index>", views.group_of_of_pictures_video, name="group_of_of_pictures_video"),
]
