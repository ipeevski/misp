import ffmpeg as ffmpeg
import re
import math
from datetime import datetime

percent_complete = 0
current_time = 0
total_time = 0

def run(input_filename, output_filename,
    options={},
    progress_callback=None,
    verbosity=0):
    # percent_complete = 0
    # current_time = 0

    total_time = float(ffmpeg.probe(input_filename)["format"]["duration"])
    # input = ffmpeg.input(input_filename, v=1, a=1)
    # ffmpeg_cmd = ffmpeg.output(input.node[0], input.node[1], f"{output_filename}", **options)
    # audio = input.audio # .filter("aecho", 0.8, 0.9, 1000, 0.3)
    # video = input.video # .hflip()
    # ffmpeg_cmd = ffmpeg.output(audio, video, f"{output_filename}", **options)

    input = ffmpeg.input(input_filename)
    # .filter('fps', fps=25, round='up')
    ffmpeg_cmd = input.output(f"{output_filename}", **options)

    if verbosity:
        print(' '.join(ffmpeg_cmd.compile()))

    process = (
        ffmpeg_cmd.run_async(quiet=True, overwrite_output=True)
    )

    regex = re.compile(".*frame= +([0-9]+) +fps= *([0-9.]+?) .+ time=([0-9.:]+?) .+ speed= *([0-9.]+)x")

    buffer = process.stderr.readline()
    while buffer:
        if verbosity >= 2:
            print(buffer)

        matches = regex.search(str(buffer))
        if matches:
            current_time = parse_time(matches.group(3))
            percent_complete = math.floor(current_time * 100 / total_time)
            speed = matches.group(4)
            if progress_callback:
                progress_callback(percent_complete)

            if verbosity >= 2:
                print(f'Sec: {current_time} of {total_time}, perc: {percent_complete}, speed: {float(speed)}')

        buffer = process.stderr.read(160)

    if progress_callback:
        progress_callback(100)
    process.wait()

def parse_time(time_string):
    time_format = "%H:%M:%S.%f"
    section_time = datetime.strptime(time_string, time_format) - datetime.strptime("00:00:00.00000", time_format)

    return section_time.total_seconds()
