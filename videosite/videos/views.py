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
        # Output returned by ffprobe as JSON for the specified file.
        ffprobe_output = ffmpeg.probe(f"videos/static/videos/{video_filename}", show_frames=None)
    except ffmpeg.Error as e:
        return HttpResponse(f"An error occurred while using ffprobe on {video_filename}:<br>{e.stderr}")

    video_frames = [frame for frame in ffprobe_output['frames'] if frame['pict_type'] == 'I']
    if video_frames.count == 0:
        return HttpResponse(f"No I-Frames were found ffprobe on {video_filename}")

    # Return the list of I-Frames as JSON. The safe=False argument allows JsonResponse to parse a list.
    return JsonResponse(video_frames, json_dumps_params={'indent': 4}, safe=False)

def group_of_of_pictures_video(request, video_filename, group_of_pictures_index):
    """Returns an MP4 file containing the video data for the group of pictures requested (zero-indexed)."""
    pass

def custom_page_not_found_view(request, exception):
    response = render(request, "videos/index.html")
    response.status_code = 404
    return response
