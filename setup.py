from setuptools import setup, find_packages

setup(
    name='EasyAudioToTextWithWhisper',
    version='0.0.42',
    description='A Python script to transcribe audio files using OpenAI Whisper',
    author='Hunter Gerlach',
    author_email='hunter@huntergerlach.com',
    packages=find_packages(),  # automatically find all packages and subpackages
    install_requires=[
        'pydub',
        'tqdm',
        'mutagen',
        'pytube',
        'argparse',
        'openai-whisper',
    ],
)
