"""Views accepting an HTTP request and returning an HTTP response."""
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render

from django.conf import settings

import ffmpeg


def index(request):
    """Returns an HTML page detailing the Video Keyframe Server endpoints."""
    return render(request, "videos/index.html")

def video_elements(request, video_filename):
    """Returns an HTML page containing a grid of all the groups of pictures in playable <video> elements and their
    timestamps.
    """
    context = {
        video_filename: video_filename
    }
    return render(request, "videos/video_elements.html", context)

# TODO: Refactor
def video_iframe_detail(request, video_filename):
    """Returns JSON-encoded data showing details of all the I-frames in a video."""
    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    try:
        # Output returned by ffprobe as JSON for the specified file.
        ffprobe_iframes_as_json = ffmpeg.probe(video_pathname, show_frames=None)
    except ffmpeg.Error as e:
        return HttpResponse(f"An error occurred while using ffprobe on {video_filename}:<br>{e.stderr}")

    video_frames = [frame for frame in ffprobe_iframes_as_json['frames'] if frame['pict_type'] == 'I']
    if len(video_frames) == 0:
        return HttpResponse(f"No I-Frames were found ffprobe on {video_filename}")

    # Return the list of I-Frames as JSON. The safe=False argument allows JsonResponse to parse a list.
    return JsonResponse(video_frames, json_dumps_params={'indent': 4}, safe=False)

# TODO: Refactor
def group_of_of_pictures_video(request, video_filename, group_of_pictures_index):
    """Returns an MP4 file containing the video data for the group of pictures requested (zero-indexed)."""

    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    try:
        # Output returned by ffprobe as JSON for the specified file.
        ffprobe_iframes_as_json = ffmpeg.probe(video_pathname, show_frames=None)
    except ffmpeg.Error as e:
        return HttpResponse(f"An error occurred while using ffprobe on {video_filename}:<br>{e.stderr}")

    video_frames = [frame for frame in ffprobe_iframes_as_json['frames'] if frame['pict_type'] == 'I']
    number_of_video_frames = len(video_frames)
    if number_of_video_frames == 0:
        return HttpResponse(f"No I-Frames were found ffprobe on {video_filename}")
    elif group_of_pictures_index >= number_of_video_frames:
        return HttpResponse(f"Requested group-of-pictures index {group_of_pictures_index} doesn't exist in  {video_filename}")

    start_frame = video_frames[group_of_pictures_index]['coded_picture_number']
    if group_of_pictures_index < (number_of_video_frames - 1):
        end_frame = video_frames[group_of_pictures_index + 1]['coded_picture_number']
    else:
        try:
            ffprobe_frames_nbr_as_json = ffmpeg.probe(video_pathname, count_frames=None, show_entries="stream=nb_read_frames")
            streams_as_list = ffprobe_frames_nbr_as_json['streams']
            end_frame = streams_as_list[0]['nb_read_frames']
        except ffmpeg.Error as e:
            return HttpResponse(f"An error occurred while using ffprobe on {video_filename}:<br>{e.stderr}")

    video_pathname = f"{str(settings.VIDEOS_STATIC_ROOT)}/{video_filename}"
    output_pathname = f"{str(settings.VIDEOS_MEDIA_ROOT)}/{video_filename}"
    try:
        (
            ffmpeg
            .input(video_pathname)
            .trim(start_frame=start_frame, end_frame=end_frame)
            .output(output_pathname)
            .overwrite_output()
            .run()
        )
    except ffmpeg.Error as e:
        return HttpResponse(f"An error occurred while using ffmpeg on {video_filename}:<br>{e.stderr}")

    template_output_pathname = f"videos/media/{video_filename}"
    context = {
        'group_of_pictures_index': group_of_pictures_index,
        'output_pathname': template_output_pathname
    }
    return render(request, "videos/group_of_of_pictures_video.html", context)

def custom_page_not_found_view(request, exception):
    response = render(request, "videos/index.html")
    response.status_code = 404
    return response
