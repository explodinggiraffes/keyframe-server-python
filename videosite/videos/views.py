"""Views accepting an HTTP request and returning an HTTP response.

    TODO:
    This view implementation is starting to get pretty "chucky", even with ffprobe and ffmpeg functionality moved
    to the videos_ffmpeg module. The next refactor should move all business logic out of this file and into its own
    module, or even further refactored into class(es).
"""

import time

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

import videos.videos_ffmpeg as videos_ffmpeg


def index(request):
    """Returns an HTML page detailing the Video Keyframe Server endpoints."""

    return render(request, "videos/index.html")

def video_elements(request, video_filename):
    """Returns an HTML page containing a grid of all the groups of pictures in playable <video> elements and their
    timestamps.
    """

    # Get I-Frames.
    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    try:
        video_frames = videos_ffmpeg.iframes(video_pathname)
    except RuntimeError as e:
        return HttpResponse(f"An error occurred getting I-Frames for {video_filename}:<br>{repr(e)}")

    number_of_video_frames = len(video_frames)
    if number_of_video_frames == 0:
        return HttpResponse(f"No I-Frames were found using ffprobe on {video_filename}")

    # Create a list of video data to be displayed on an HTML page.
    group_of_pictures_list = []
    group_of_pictures_index = 0
    for frame in video_frames:
        # Get the timestamp used for "input seeking" (finding where we'll start copying the original file).
        # This timestamp, as well as the ending timestamp, will also be stored in the context being passed to the
        # template.
        timestamp_begin = video_frames[group_of_pictures_index]['best_effort_timestamp_time']
        if group_of_pictures_index < (number_of_video_frames - 1):
            timestamp_end = video_frames[group_of_pictures_index + 1]['best_effort_timestamp_time']
        else:
            timestamp_end = "end"

        # Determine the number of frames to be copied.
        try:
            frame_span = videos_ffmpeg.group_of_pictures_frame_span(video_frames, group_of_pictures_index, video_pathname)
        except RuntimeError as e:
            return HttpResponse(f"An error occurred getting I-Frames for {video_filename}:<br>{repr(e)}")

        # Make a copy of the original video for the group-of-pictures for this I-Frame.
        output_pathname = f"{str(settings.VIDEOS_MEDIA_ROOT)}/video_elements.{time.time()}.{video_filename}"
        videos_ffmpeg.copy(video_pathname, output_pathname, timestamp_begin, frame_span)

        # Calculate which display group the new video should be displayed within on the HTML page.
        # Would be better to calculate this within the template itself; someone who knows the Django template language
        # well could probably do this....
        display_index = group_of_pictures_index + 1
        display_group_begin = True if display_index % 6 == 1 else False
        display_group_end = True if display_index % 6 == 0 else False

        group_of_pictures_list.append({
            'display_group_begin': display_group_begin,
            'display_group_end': display_group_end,
            'display_index': display_index,
            'output_pathname': output_pathname,
            'timestamp_begin': timestamp_begin,
            'timestamp_end': timestamp_end
        })

        group_of_pictures_index += 1

    # Convert the list created about to a tuple so it can be hashed for the context being passed to the template.
    group_of_pictures_tuple = tuple(group_of_pictures_list)

    context = {
        'group_of_pictures_tuple': group_of_pictures_tuple
    }

    return render(request, "videos/video_elements.html", context)

def video_iframe_detail(request, video_filename):
    """Returns JSON-encoded data showing details of all the I-frames in a video."""

    # Get I-Frames.
    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    try:
        video_frames = videos_ffmpeg.iframes(video_pathname)
    except RuntimeError as e:
        return HttpResponse(f"An error occurred getting I-Frames for {video_filename}:<br>{repr(e)}")

    if len(video_frames) == 0:
        return HttpResponse(f"No I-Frames were found using ffprobe on {video_filename}")

    # Return and render the list of I-Frames as JSON. The safe=False argument allows JsonResponse to parse a list.
    return JsonResponse(video_frames, json_dumps_params={'indent': 4}, safe=False)

def group_of_of_pictures_video(request, video_filename, group_of_pictures_index):
    """Returns an MP4 file containing the video data for the group of pictures requested (zero-indexed)."""

    # Get I-Frames.
    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    try:
        video_frames = videos_ffmpeg.iframes(video_pathname)
    except RuntimeError as e:
        return HttpResponse(f"An error occurred getting I-Frames for {video_filename}:<br>{repr(e)}")

    number_of_video_frames = len(video_frames)
    if number_of_video_frames == 0:
        return HttpResponse(f"No I-Frames were found using ffprobe on {video_filename}")
    elif group_of_pictures_index >= number_of_video_frames:
        return HttpResponse(f"Requested group-of-pictures index {group_of_pictures_index} doesn't exist in  {video_filename}")

    # Get the timestamp used for "input seeking" (finding where we'll start copying the original file).
    timestamp_begin = video_frames[group_of_pictures_index]['best_effort_timestamp_time']

    # Determine the number of frames to be copied.
    try:
        frame_span = videos_ffmpeg.group_of_pictures_frame_span(video_frames, group_of_pictures_index, video_pathname)
    except RuntimeError as e:
        return HttpResponse(f"An error occurred getting I-Frames for {video_filename}:<br>{repr(e)}")

    # Make a copy of the original video for the specified group-of-pictures.
    output_pathname = f"{str(settings.VIDEOS_MEDIA_ROOT)}/group_of_of_pictures_video.{time.time()}.{video_filename}"
    videos_ffmpeg.copy(video_pathname, output_pathname, timestamp_begin, frame_span)

    context = {
        'group_of_pictures_index': group_of_pictures_index,
        'output_pathname': output_pathname
    }

    return render(request, "videos/group_of_of_pictures_video.html", context)

# Note: This only works when DEBUG = False in videosite\videosite\settings.py; otherwise, the debug 404 page is
# rendered.
def custom_page_not_found_view(request, exception):
    response = render(request, "videos/index.html")
    response.status_code = 404
    return response
