"""Views accepting an HTTP request and returning an HTTP response."""
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

import ffmpeg


def index(request):
    """Returns an HTML page detailing the Video Keyframe Server endpoints."""
    return render(request, "videos/index.html")

def video_elements(request, video_filename):
    """Returns an HTML page containing a grid of all the groups of pictures in playable <video> elements and their
    timestamps.
    """
    context = {"video_filename": video_filename}
    return render(request, "videos/video_elements.html", context)

def video_iframe_detail(request, video_filename):
    """Returns JSON-encoded data showing details of all the I-frames in a video."""
    try:
        probe = ffmpeg.probe(f"videos/static/videos/{video_filename}")
    except ffmpeg.Error as e:
        return HttpResponse(f"An error occurred while using ffprobe with {video_filename}:<br>{e.stderr}")

    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
    width = int(video_stream['width'])
    height = int(video_stream['height'])

    response_data = {}
    response_data['video_filename'] = width
    response_data['ffprobe_response'] = height

    return JsonResponse(response_data, json_dumps_params={'indent': 4})

def group_of_of_pictures_video(request, video_filename, group_of_pictures_index):
    """Returns an MP4 file containing the video data for the group of pictures requested (zero-indexed)."""
    pass

def custom_page_not_found_view(request, exception):
    response = render(request, "videos/index.html")
    response.status_code = 404
    return response
