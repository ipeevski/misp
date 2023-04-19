# MMISP

A framework for processing multimedia files (mainly video, audio and text) and generating new outputs.

It's designed to be modular and supports adding your own custom modules.

It is also intended for creating a processsing pipeline, where steps can use the
outputs of previous steps as their own inputs.

## Example Usage

To process a file, based on a set of steps:
```sh
python process.py "<input_file>" --config config.yaml
```

The expected configuration (`config.yaml` in the above example) should look like this:

```yaml
process:
  - step: "module|cmd|parallel"
    output: "{path}//{base_name}_out.mp4"   # The pattern for the output file
                                            # The {path} and {base_name} variables are automatically generated based on the input name
    steps:                                  # An optional list of sub-steps to execute
      - step: ...                           # Only applicable when step is "parallel"
    cmd: "<cmd> {input} {output}"           # Only applicable when the step is "cmd"
                                            # {input} and {output} automatically replaced
    module: "<module_name>"                 # The module name to use
                                            # Only applicable when the step is "module"
    options:                                # A keyed list of any options to pass in to the module
                                            # Only applicable when the step is "module"
```

For example:
```yaml
process:
  - step: "module"
    module: "ffmpeg"
    output: "{path}//{base_name}_out.mp4"
    options:
      vcodec: "libx265"
  - step: "parallel"
    steps:
      - step: "module"
        module: "ffmpeg"
        output: "{path}//{base_name}_out2.mp4"
        options:
          vcodec: "libx265"
      - step: "cmd"
        cmd: "ffmpeg -y -hide_banner -nostats -loglevel quiet -x265-params log-level=quiet -i {input} -vcodec libx265 {output}"
        output: "{path}//{base_name}_out3.mp4"
```

Alternatively, you can specify JSON (via the `--json` flag) or YAML (via the `--yaml` flag) directly from the command line:
```sh
python process.py "<input_file>" --json '{ \"process\": [{ \"step\": \"module\", \"module\": \"ffprobe\", \"output\": \"test.json\" }] }'
```

## Available Modules
- [ffmpeg](#ffmpeg)
- [ffprobe](#ffprobe)

### ffmpeg

Leveraging on the `ffmpeg` library.
Supported options are anything the `ffmpeg` command line tool supports

It can be used for re-encoding a video
```yaml
  - step: "module"
    module: "ffmpeg"
    output: "{path}//{base_name}_out.mp4"
    options:
      vcodec: "libx265"
```

Requires `ffmpeg-python`

```
pip install ffmpeg-python
```

### ffprobe

Leveraging on the `ffmpeg` library to get information about a stream.

It can be used for get data about a media file
```yaml
  - step: "module"
    module: "ffprobe"
    output: "{path}//{base_name}.json"
```

Sample output:
```
{
  "streams": [
    {
      "index": 0,
      "codec_name": "timed_id3",
      "codec_long_name": "timed ID3 metadata",
      "codec_type": "data",
      "codec_tag_string": "ID3 ",
      "codec_tag": "0x20334449",
      "id": "0x102",
      "r_frame_rate": "0/0",
      "avg_frame_rate": "0/0",
      "time_base": "1/90000",
      "start_pts": 270002070,
      "start_time": "3000.023000",
      "duration_ts": 16464810,
      "duration": "182.942333",
      "disposition": {
        "default": 0,
        "dub": 0,
        "original": 0,
        "comment": 0,
        "lyrics": 0,
        "karaoke": 0,
        "forced": 0,
        "hearing_impaired": 0,
        "visual_impaired": 0,
        "clean_effects": 0,
        "attached_pic": 0,
        "timed_thumbnails": 0,
        "captions": 0,
        "descriptions": 0,
        "metadata": 0,
        "dependent": 0,
        "still_image": 0
      }
    },
    {
      "index": 1,
      "codec_name": "h264",
      "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
      "profile": "High",
      "codec_type": "video",
      "codec_tag_string": "[27][0][0][0]",
      "codec_tag": "0x001b",
      "width": 1920,
      "height": 1080,
      "coded_width": 1920,
      "coded_height": 1080,
      "closed_captions": 0,
      "film_grain": 0,
      "has_b_frames": 0,
      "sample_aspect_ratio": "1:1",
      "display_aspect_ratio": "16:9",
      "pix_fmt": "yuv420p",
      "level": 40,
      "chroma_location": "left",
      "field_order": "progressive",
      "refs": 1,
      "is_avc": "false",
      "nal_length_size": "0",
      "id": "0x100",
      "r_frame_rate": "30/1",
      "avg_frame_rate": "30/1",
      "time_base": "1/90000",
      "start_pts": 270002880,
      "start_time": "3000.032000",
      "duration_ts": 16464000,
      "duration": "123.123456",
      "bits_per_raw_sample": "8",
      "extradata_size": 34,
      "disposition": {
        "default": 0,
        "dub": 0,
        "original": 0,
        "comment": 0,
        "lyrics": 0,
        "karaoke": 0,
        "forced": 0,
        "hearing_impaired": 0,
        "visual_impaired": 0,
        "clean_effects": 0,
        "attached_pic": 0,
        "timed_thumbnails": 0,
        "captions": 0,
        "descriptions": 0,
        "metadata": 0,
        "dependent": 0,
        "still_image": 0
      }
    },
    {
      "index": 2,
      "codec_name": "aac",
      "codec_long_name": "AAC (Advanced Audio Coding)",
      "profile": "LC",
      "codec_type": "audio",
      "codec_tag_string": "[15][0][0][0]",
      "codec_tag": "0x000f",
      "sample_fmt": "fltp",
      "sample_rate": "48000",
      "channels": 2,
      "channel_layout": "stereo",
      "bits_per_sample": 0,
      "id": "0x101",
      "r_frame_rate": "0/0",
      "avg_frame_rate": "0/0",
      "time_base": "1/90000",
      "start_pts": 270002070,
      "start_time": "3000.023000",
      "duration_ts": 16458240,
      "duration": "123.123456",
      "bit_rate": "128089",
      "disposition": {
        "default": 0,
        "dub": 0,
        "original": 0,
        "comment": 0,
        "lyrics": 0,
        "karaoke": 0,
        "forced": 0,
        "hearing_impaired": 0,
        "visual_impaired": 0,
        "clean_effects": 0,
        "attached_pic": 0,
        "timed_thumbnails": 0,
        "captions": 0,
        "descriptions": 0,
        "metadata": 0,
        "dependent": 0,
        "still_image": 0
      }
    }
  ],
  "format": {
    "filename": "<input_file>",
    "nb_streams": 3,
    "nb_programs": 1,
    "format_name": "mpegts",
    "format_long_name": "MPEG-TS (MPEG-2 Transport Stream)",
    "start_time": "3000.023000",
    "duration": "123.123456",
    "size": "118433172",
    "bit_rate": "5179038",
    "probe_score": 50
  }
}
```

Requires `ffmpeg-python`

```
pip install ffmpeg-python
```
