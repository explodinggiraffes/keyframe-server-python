# Copyright 2023 John Koszarek

"""Utility functions for working with ffmpeg and ffprobe."""

from typing import Any
import subprocess

import ffmpeg


def copy(video_pathname, output_pathname, timestamp_begin, frame_span) -> None:
    """Copies part of the specified video file without re-encoding. The output is written to a new file, using the name
    of the supplied output file pathname.

    If a file with the supplied output pathname already exists it will be overwitten.

    Implementation Note: Couldn't get the copy option working properly with the ffmpeg library, so calling ffmpeg
    directly as a subprocess.

    Args:
      video_pathname: The pathname of the file on which ffprobe will operate.
      output_pathname: The new video file.
      timestamp_begin: The timestamp used for "input seeking" (finding where we'll start copying the original file).
      frame_span: Determines the number of frames to be copied.
    """
    start_frame = frame_span['start_frame']
    end_frame = frame_span['end_frame']
    number_of_frames = end_frame - start_frame

    # Build the ffmpeg command.
    # Note the --ss argument MUST come before the -i argument to perform input seeking. Input seeking is fast; ffmpeg
    # will see the nearest I-Frame to the beginning timestamp. Since we derived this timestamp from an I-Frame, it
    # should be spot-on. Input seeking seems to create more accurate copies (slices) than output seeking (where -ss is
    # specified after -i).
    # Short article explaining input / output seeking:
    # https://ottverse.com/trim-cut-video-using-start-endtime-reencoding-ffmpeg/
    command = f"ffmpeg -hide_banner -loglevel error -ss {timestamp_begin} -i {video_pathname} -frames:v {number_of_frames} -c copy {output_pathname}"
    subprocess.call(command, shell=True)

def group_of_pictures_frame_span(iframes, group_of_pictures_index, video_pathname) -> dict[int, int]:
    """Returns the start and end frames for the specified group-of-pictures.

    If the supplied index is for the last group-of-pictures, the number of frames for the entire video will be used as
    the end frame.

    Args:
      iframes: A list of I-Frame data that was returned by ffprobe.
      group_of_pictures_index: The index of the group-of-pictures for which we want the start and end frames.
      video_pathname: The pathname of the file used if we need to obtain the number of frames for the entire video.

    Raises:
      RuntimeError
    """
    start_frame = iframes[group_of_pictures_index]['coded_picture_number']
    if group_of_pictures_index < (len(iframes) - 1):
        end_frame = iframes[group_of_pictures_index + 1]['coded_picture_number'] - 1
    else:
        try:
          ffprobe_frames_nbr = ffmpeg.probe(video_pathname, count_frames=None, show_entries="stream=nb_read_frames")
        except ffmpeg.Error as e:
          raise RuntimeError(e.stderr)
        streams = ffprobe_frames_nbr['streams']
        end_frame = int(streams[0]['nb_read_frames'])

    frame_span = {
        'start_frame': start_frame,
        'end_frame': end_frame
    }

    return frame_span

def iframes(video_pathname) -> list[str: Any]:
    """Returns a list of I-Frame data generated by ffprobe for the specified video file.

    Args:
      video_pathname: The pathname of the file on which ffprobe will operate.

    Returns:
      A list of I-Frame data.

    Raises:
      RuntimeError
    """
    try:
      ffprobe_all_frames = ffmpeg.probe(video_pathname, show_frames=None)
    except ffmpeg.Error as e:
      raise RuntimeError(e.stderr)
    iframes = [frame for frame in ffprobe_all_frames['frames'] if frame['pict_type'] == 'I']

    return iframes
