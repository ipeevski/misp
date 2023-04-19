import os
import subprocess
import threading
import yaml
from tqdm import tqdm

def update_progress(percent_complete):
    if pbar:
        pbar.n = percent_complete
        pbar.refresh()

def replacements(string, input_file):
    return string.format(
        path=os.path.dirname(input_file),
        base_name=os.path.splitext(os.path.basename(input_file))[0],
        ext=os.path.splitext(input_file)[1]
    )

def runModule(input_file, process):
    module = __import__(process["module"])
    func = getattr(module, 'run')

    output_file = replacements(process['output'], input_file)
    thread = threading.Thread(
        target=func,
        args=[input_file, output_file],
        kwargs={
            'ffmpeg_options': process['ffmpeg_options'],
            'progress_callback': update_progress
        }
    )
    thread.daemon = True
    thread.start()

    return thread

def runCmd(input_file, process):
    output_file = replacements(process['output'], input_file)
    thread = threading.Thread(
        target=subprocess.run,
        args=[process['cmd'].format(input=input_file, output=output_file).split(' ')],
    )
    thread.daemon = True
    thread.start()
    return thread

def run(input_file, processes, parallel=False):
    threads = []
    for process in processes:
        if process['step'] == 'parallel':
            run(input_file, process['steps'], True)
            continue

        if process['step'] == 'module':
            thread = runModule(input_file, process)
        elif process['step'] == 'cmd':
            thread = runCmd(input_file, process)

        if not parallel:
            thread.join()
        else:
            threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == '__main__':
    file = open('test-recipe.yaml', 'r')
    items = yaml.safe_load(file)

    input_file = 'vid.mp4'
    input_file = os.path.abspath(input_file)

    # TODO: Handle progress bar in a thread
    pbar = tqdm(total=100)

    run(input_file, items['process'])

    # thread = threading.Thread(target=ffmpeg.run, args=['vid.mp4', 'output.mp4'], kwargs={'ffmpeg_options': {'vcodec': 'libx265'}, 'progress_callback': update_progress})
    # thread.daemon = True
    # thread.start()
    # thread.join()

    pbar.close()
