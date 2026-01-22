import subprocess
import os

def convert_480p(source):
    """
    Creates a 480p version of the video.
    """
    _convert(source, '480p', 'hd480')


def convert_720p(source):
    """
    Creates a 720p version of the video.
    """
    _convert(source, '720p', 'hd720')


def convert_1080p(source):
    """
    Creates a 1080p version of the video.
    """
    _convert(source, '1080p', 'hd1080')


def _convert(source, label, resolution_cmd):
    """
    Internal helper function to run the ffmpeg command.

    Args:
        source (str): Path to the source file.
        label (str): Label for the new filename (e.g., '720p').
        resolution_cmd (str): FFmpeg resolution flag (e.g., 'hd720').
    """
    base, ext = os.path.splitext(source)
    target = base + '_' + label + ext

    cmd = [
        'ffmpeg', '-i', source, '-s', resolution_cmd, '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', target
    ]

    subprocess.run(cmd, capture_output=True)