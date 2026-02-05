import subprocess
import os

def convert_480p(source):
    """
    Creates a 480p HLS playlist and segments.
    """
    _convert(source, '480p', 'hd480')


def convert_720p(source):
    """
    Creates a 720p HLS playlist and segments.
    """
    _convert(source, '720p', 'hd720')


def convert_1080p(source):
    """
    Creates a 1080p HLS playlist and segments.
    """
    _convert(source, '1080p', 'hd1080')


def _convert(source, label, resolution_cmd):
    """
    Internal helper function to run the ffmpeg command for HLS conversion.
    Generates an .m3u8 playlist file.
    """
    base, _ = os.path.splitext(source)
    target = f"{base}_{label}.m3u8"

    # HLS conversion command
    cmd = [
        'ffmpeg', '-i', source, '-s', resolution_cmd, 
        '-c:v', 'libx264', '-crf', '23', '-c:a', 'aac', '-strict', '-2', 
        '-start_number', '0', '-hls_time', '10', '-hls_list_size', '0', '-f', 'hls', target
    ]

    # Run ffmpeg in the background (non-blocking)
    subprocess.Popen(cmd)