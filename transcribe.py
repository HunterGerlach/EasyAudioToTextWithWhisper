import warnings
from numba import NumbaDeprecationWarning

# Suppress specific warnings
warnings.filterwarnings("ignore", category=UserWarning, module="whisper.transcribe")
warnings.filterwarnings("ignore", category=NumbaDeprecationWarning)

import os
from pydub import AudioSegment
import whisper
from tqdm import tqdm
import logging
import argparse
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.id3 import ID3
from pytube import YouTube

def download_youtube_audio(url, output_dir='youtube_downloads'):
    # Create a YouTube object
    yt = YouTube(url)

    # Get the title of the video and create a safe filename
    title = yt.title
    safe_filename = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
    safe_filename += '.m4a'  # YouTube downloads are in M4A format

    # Get the highest quality audio stream
    audio_stream = yt.streams.get_audio_only()

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download the audio stream
    audio_stream.download(output_path=output_dir, filename=safe_filename)

    # Check if the file was downloaded successfully
    audio_file_path = os.path.join(output_dir, safe_filename)
    if not os.path.isfile(audio_file_path):
        raise Exception(f"Failed to download audio from YouTube video: {url}")
    else:
        print(f"Successfully downloaded audio to: {audio_file_path}")
        return audio_file_path, safe_filename

# Set up logging
logging.basicConfig(filename='transcription.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Default parameters
defaults = {
    'input_type': 'file',
    'input_path': 'learn-in-podcast__the-rise-of-the-ai-engine.mp3',
    'chunks_dir': 'chunks_dir',
    'transcripts_dir': 'transcripts_dir',
    'num_chunks': 100
}

# Set up argument parser
parser = argparse.ArgumentParser(description='Transcribe an audio file with Whisper.')
parser.add_argument('--input_type', type=str, choices=['file', 'youtube'], default=defaults['input_type'],
                    help='The type of the input (file or youtube). Default: %(default)s')
parser.add_argument('--input_path', type=str, default=defaults['input_path'],
                    help='The path to the audio file or YouTube video to transcribe. Default: %(default)s')
parser.add_argument('--chunks_dir', type=str, default=defaults['chunks_dir'],
                    help='The directory to store the audio chunks. Default: %(default)s')
parser.add_argument('--transcripts_dir', type=str, default=defaults['transcripts_dir'],
                    help='The directory to store the transcriptions. Default: %(default)s')
parser.add_argument('--num_chunks', type=int, default=defaults['num_chunks'],
                    help='The number of chunks to split the audio into. Default: %(default)s')
args = parser.parse_args()

# Determine the audio file path based on the input type
if args.input_type == 'youtube':
    # Download the audio from the YouTube video
    args.audio_file_path, base_name = download_youtube_audio(args.input_path)
    args.is_mp3 = False
elif args.input_type == 'file':
    # Verify if audio file exists
    if not os.path.isfile(args.input_path):
        raise FileNotFoundError(f"The specified audio file {args.input_path} does not exist!")
    args.audio_file_path = args.input_path
    args.is_mp3 = args.input_path.lower().endswith('.mp3')
    # Get the base name of the input (without extension)
    base_name = os.path.splitext(os.path.basename(args.input_path))[0]
else:
    raise ValueError(f"Invalid input type: {args.input_type}. Expected 'file' or 'youtube'.")

# Load the audio file with pydub
try:
    audio = AudioSegment.from_file(args.audio_file_path)
except Exception as e:
    logging.error(f"Error loading audio file: {e}")
    raise

# Calculate the length of each chunk
chunk_length = len(audio) // args.num_chunks

# Create a subdirectory for this input
audio_chunks_dir = os.path.join(args.chunks_dir, base_name)
os.makedirs(audio_chunks_dir, exist_ok=True)

# Create a subdirectory for this transcription
audio_transcripts_dir = os.path.join(args.transcripts_dir, base_name)
os.makedirs(audio_transcripts_dir, exist_ok=True)

# Load the Whisper model
try:
    model = whisper.load_model("base")
except Exception as e:
    logging.error(f"Error loading Whisper model: {e}")
    raise

# Initialize the progress bars
chunking_progress_bar = tqdm(total=args.num_chunks, desc="Chunking", ncols=70)
transcription_progress_bar = tqdm(total=args.num_chunks, desc="Transcription", ncols=70)

# Loop over the chunks
for i in range(args.num_chunks):
    try:
        # Calculate the start and end times for this chunk
        start_time = i * chunk_length
        end_time = start_time + chunk_length if i < args.num_chunks - 1 else len(audio)

        # Extract this chunk from the audio file
        chunk = audio[start_time:end_time]

        # Save the chunk to a file if it doesn't already exist
        chunk_file_path = os.path.join(audio_chunks_dir, f"chunk{i}.wav")
        if not os.path.exists(chunk_file_path):
            chunk.export(chunk_file_path, format="wav")
            logging.info(f"Created chunk file: {chunk_file_path}")

        # Update the chunking progress bar
        chunking_progress_bar.update(1)

        # Transcribe the chunk if the transcription doesn't already exist
        transcription_file_path = os.path.join(audio_transcripts_dir, f"transcription{i}.txt")
        if not os.path.exists(transcription_file_path):
            result = model.transcribe(chunk_file_path)
            # Save the transcription to a file
            with open(transcription_file_path, 'w') as f:
                f.write(result["text"])
            logging.info(f"Created transcription file: {transcription_file_path}")

        # Update the transcription progress bar
        transcription_progress_bar.update(1)
    except Exception as e:
        logging.error(f"Error during chunking or transcription: {e}")
        raise

# Close the progress bars
chunking_progress_bar.close()
transcription_progress_bar.close()

# Combine all transcriptions into one file
full_transcription = ""
for i in range(args.num_chunks):
    transcription_file_path = os.path.join(audio_transcripts_dir, f"transcription{i}.txt")
    with open(transcription_file_path, 'r') as f:
        full_transcription += f.read() + " "

# Define the directory to save the final transcription file
if args.input_type == 'youtube':
    # For YouTube videos, save next to the original video
    final_transcript_dir = 'youtube_downloads'
else:
    # For local files, save in the same directory as the original file
    final_transcript_dir = os.path.dirname(args.input_path)

# Write the full transcription to a file in the final transcription directory
final_transcription_file_path = os.path.join(final_transcript_dir, base_name + ".txt")


if args.is_mp3:
    audio_file = MP3(args.audio_file_path, ID3=ID3)
    metadata = {
        'title': audio_file.get('TIT2', 'Unknown title'),
        'artist': audio_file.get('TPE1', 'Unknown artist'),
        'album': audio_file.get('TALB', 'Unknown album'),
        'track number': audio_file.get('TRCK', 'Unknown track number'),
        'genre': audio_file.get('TCON', 'Unknown genre'),
        'recording date': audio_file.get('TDRC', 'Unknown recording date'),
    }
else:
    audio_file = MP4(args.audio_file_path)
    metadata = {
        'title': audio_file.get('\xa9nam', ['Unknown title'])[0],
        'artist': audio_file.get('\xa9ART', ['Unknown artist'])[0],
        'album': audio_file.get('\xa9alb', ['Unknown album'])[0],
        'track number': audio_file.get('trkn', [(0, 0)])[0][0],
        'genre': audio_file.get('\xa9gen', ['Unknown genre'])[0],
        'recording date': audio_file.get('\xa9day', ['Unknown recording date'])[0],
    }

# When writing the full transcription to a file, include the metadata at the top
with open(final_transcription_file_path, 'w') as f:
    for key, value in metadata.items():
        f.write(f"{key}: {value}\n")
    f.write("\n")
    f.write(full_transcription)

logging.info(f"Created final transcription file: {final_transcription_file_path}")
