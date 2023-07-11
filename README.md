# EasyAudioToTextWithWhisper

EasyAudioToTextWithWhisper is a Python script that uses OpenAI's Whisper ASR (Automatic Speech Recognition) system to transcribe audio files into text. It's designed to be straightforward to use, even for large files. The script splits the audio into manageable chunks, transcribes each chunk, and then combines them into a final transcription. The script can handle both local audio files and YouTube videos.

## Features

- Breaks down large audio files into manageable chunks for transcription.
- Supports downloading and transcribing audio from YouTube videos.
- Supports resuming transcription from the last completed chunk in case of interruptions.
- Outputs progress bars for both the chunking and transcription processes.
- Writes metadata and transcriptions to text files.
- Provides command-line arguments for customizing the transcription process.

## Usage

You can run the script with default parameters like this:

```bash
python3 transcribe.py
```

You can also specify parameters like this:

```bash
python3 transcribe.py --input_type file --input_path my_audio_file.mp3 --chunks_dir my_chunks_dir --transcripts_dir my_transcripts_dir --num_chunks 200
```

Or for YouTube videos:

```bash
python3 transcribe.py --input_type youtube --input_path https://www.youtube.com/watch?v=dQw4w9WgXcQ --num_chunks 200
```

## Parameters

- `input_type`: The type of the input (file or youtube). Default: 'file'
- `input_path`: The path to the audio file or the URL of the YouTube video to transcribe. Default for file: 'learn-in-podcast\_\_the-rise-of-the-ai-engine.mp3'
- `chunks_dir`: The directory to store the audio chunks. Default: 'chunks_dir'
- `transcripts_dir`: The directory to store the transcriptions. Default: 'transcripts_dir'
- `num_chunks`: The number of chunks to split the audio into. Default: 100

## Requirements

- Python 3
- OpenAI's Whisper model
- PyDub
- tqdm
- logging
- argparse
- mutagen
- pytube

## Getting Started as a Developer

### Contributing

Contributions to EasyAudioToTextWithWhisper are welcome! Here's how you can contribute:

1. Fork this repository.
2. Create a new branch for your changes.
3. Make your changes in your branch.
4. Submit a pull request.

Before contributing, please check the open issues in this repository to avoid duplicating work.

### Initial setup of project

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip freeze > requirements.txt
```

### Return Setup

```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Troubleshooting

If you encounter any problems during setup or use of this script, please check the following:

- Make sure you have the correct version of Python installed.
- Ensure that all required Python packages are installed and up-to-date.
- Make sure the audio file you're trying to transcribe is in the correct format and accessible.

If you're still having trouble, please open an issue in this repository with a description of the problem.

## License

EasyAudioToTextWithWhisper is released under the MIT License. See the LICENSE file for more details.
