import argparse
import json
import importlib
import os
import subprocess
import threading
import yaml
from tqdm import tqdm

pbar = None

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

def runModule(input_file, process, verbosity=0, progress_callback=None):
    importlib.invalidate_caches()
    module = importlib.import_module(f'.modules.{process["module"]}.main', 'mmisp')
    func = getattr(module, 'run')

    output_file = replacements(process['output'], input_file)

    kwargs = {"verbosity": verbosity}
    if 'options' in process:
        kwargs["options"] = process["options"]

    if progress_callback:
        kwargs["progress_callback"] = progress_callback

    thread = threading.Thread(
        target=func,
        args=[input_file, output_file],
        kwargs=kwargs
    )
    thread.daemon = True
    thread.start()

    return thread

def runCmd(input_file, process, verbosity=0):
    output_file = replacements(process['output'], input_file)
    args = [process['cmd'].format(input=input_file, output=output_file).split(' ')]

    if verbosity:
        print(' '.join(args[0]))

    thread = threading.Thread(
        target=subprocess.run,
        args=args,
    )
    thread.daemon = True
    thread.start()
    return thread

def run(input_file, processes, parallel=False, verbosity=0, progress_callback=None):
    threads = []
    for process in processes:
        if process['step'] == 'parallel':
            if verbosity >= 2:
                print('Running parallel processes')
            run(input_file, process['steps'], parallel=True, verbosity=verbosity, progress_callback=progress_callback)
            continue

        if process['step'] == 'module':
            if verbosity >= 2:
                print(f'Running module {process["module"]}')
            thread = runModule(input_file, process, verbosity=verbosity, progress_callback=progress_callback)
        elif process['step'] == 'cmd':
            if verbosity >= 2:
                print(f'Running cmd {process["cmd"]}')
            thread = runCmd(input_file, process, verbosity=verbosity)
        elif process['step'] == 'del':
            os.remove(input_file)
            return
        elif process['step'] == 'move':
            os.rename(input_file, process['output'])
            return

        if not parallel:
            thread.join()
        else:
            threads.append(thread)

    for thread in threads:
        thread.join()


def main():
    parser = argparse.ArgumentParser(description='Process multimedia via a pipeline.')
    parser.add_argument('input_file', metavar='filename',
                        help='A filename to the input file to be processed')
    parser.add_argument('--config', '-c', metavar='config_file',
                        help='Config file to use')
    parser.add_argument('--yaml', metavar='yaml',
                        help='YAML string (instead of using a config file)')
    parser.add_argument('--json', metavar='json',
                        help='JSON string (instead of using a config file)')
    parser.add_argument('--verbose', '-v', action='count', default=0,
                        help='Verbosity level (-v, -vv, etc)')

    args = parser.parse_args()

    if args.config:
        file = open(args.config, 'r')
        items = yaml.safe_load(file)
    elif args.yaml:
        yaml_string = open(args.yaml, 'r')
        items = yaml.safe_load(yaml_string)
    elif args.json:
        print(args.json)
        items = json.loads(args.json)

    input_file = args.input_file
    input_file = os.path.abspath(input_file)

    # TODO: Handle progress bar in a thread
    if args.verbose:
        pbar = tqdm(total=100)

    run(input_file, items['process'], verbosity=args.verbose, progress_callback=update_progress)

    # run('vid.mp4',
    #   [{'step': 'module', 'module': 'ffmpeg', 'output': 'output.mp4', 'options': {'vcodec': 'libx265'}}],
    #   verbosity=args.verbose)

    if args.verbose:
        pbar.close()


if __name__ == '__main__':
    main()
