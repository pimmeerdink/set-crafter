import requests
import io
import librosa
import numpy as np
from bs4 import BeautifulSoup
from pydub import AudioSegment
import re
from functools import lru_cache
from multiprocessing import Pool
import concurrent.futures
import pandas as pd

# Compile the regex pattern once
PREVIEW_URL_PATTERN = re.compile(
    r"(https://t4\.bcbits\.com/stream/[a-f0-9]+/mp3-128/\d+\?p=0&amp;ts=\d+&amp;t=[a-f0-9]+&amp;token=\d+_[a-f0-9]+)"
)


def get_preview_url(bandcamp_url):
    response = requests.get(bandcamp_url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the audio element
    scripts = (
        soup.find_all("script", {"type": "text/javascript"})
        + soup.find_all("script", {"type": None})
        + soup.find_all("script", {"type": "javascript"})
    )

    preview_url = None
    # print(len(scripts))
    for script in scripts:
        script_content = str(script)
        if script_content:
            # Look for the specific pattern of the audio URL
            match = re.search(
                r"(https://t4\.bcbits\.com/stream/[a-f0-9]+/mp3-128/\d+\?p=0&amp;ts=\d+&amp;t=[a-f0-9]+&amp;token=\d+_[a-f0-9]+)",
                script_content,
            )
            if match is not None:
                preview_url = match.group(1)
                break
    return preview_url


def download_audio(url):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    return response.content


def analyze_bpm(audio_data):
    # Convert to AudioSegment
    audio = AudioSegment.from_mp3(io.BytesIO(audio_data))

    # Export as wav (librosa works better with wav)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)

    # Load audio file with librosa
    y, sr = librosa.load(buffer)  # Only load first 30 seconds

    # Detect the BPM
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)

    return tempo


def get_bc_bpm(url):
    preview_url = get_preview_url(url)
    audio_data = download_audio(preview_url)
    return analyze_bpm(audio_data)


import asyncio
import concurrent.futures
import pandas as pd


async def process_bpm_urls(urls):
    async def process_url(url):
        try:
            bpm = await asyncio.to_thread(get_bc_bpm, url)
            return url, bpm
        except Exception as exc:
            print(f"{url} generated an exception: {exc}")
            return url, None

    results = await asyncio.gather(*[process_url(url) for url in urls])
    return pd.Series({url: bpm[0] for url, bpm in results if bpm is not None})


if __name__ == "__main__":
    urls = [
        # "https://wajang.bandcamp.com/track/lost-delirious",
        # "https://wajang.bandcamp.com/track/amor-satyr-conduit"
        # Add more URLs here
    ]
    results = process_bpm_urls(urls)
    for url, bpm in results.items():
        print(f"URL: {url}, BPM: {bpm}")
