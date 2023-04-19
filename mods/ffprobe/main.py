import ffmpeg
import json

def run(input_filename, output_filename=None, progress_callback=None, options={}, verbosity=0):
    probe = ffmpeg.probe(input_filename, **options)

    if verbosity >= 2:
        print(json.dumps(probe, indent=2))
    if progress_callback:
        progress_callback(100)

    if not output_filename:
        return

    with open(output_filename, 'w') as f:
        f.write(json.dumps(probe, indent=2))
