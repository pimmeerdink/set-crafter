import asyncio
import concurrent.futures
import html
import io
import os
import re

import librosa
import numpy as np
from pydub import AudioSegment

# The mp3-128 URL is token-stamped and timestamped, so we have to fetch *some*
# bandcamp page per track to get a fresh one. Use the embed-player URL — it's
# ~30 KB (vs ~200 KB for the artist page) and still contains the preview URL.
PREVIEW_URL_PATTERN = re.compile(
    r'https://t4\.bcbits\.com/stream/[a-f0-9]+/mp3-128/\d+\?[^"\']+token=\d+_[a-f0-9]+'
)

# Beat tracking does not need full fidelity — 11.025 kHz keeps the kick band and
# halves the work vs librosa's default 22.05 kHz. 15 s is enough for a stable
# estimate on dance music and halves the mp3 download.
TARGET_SR = 11025
MAX_DURATION_MS = 15_000


async def _fetch_preview_url(session, track_id):
    embed_url = f"https://bandcamp.com/EmbeddedPlayer/track={track_id}"
    async with session.get(embed_url) as response:
        text = await response.text()
    match = PREVIEW_URL_PATTERN.search(text)
    if not match:
        return None
    return html.unescape(match.group(0))


async def _download_audio(session, preview_url):
    async with session.get(preview_url) as response:
        return await response.read()


def _analyze_bpm_from_bytes(audio_data):
    audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
    audio = audio.set_channels(1).set_frame_rate(TARGET_SR)[:MAX_DURATION_MS]
    samples = np.array(audio.get_array_of_samples(), dtype=np.float32)
    samples /= float(1 << (audio.sample_width * 8 - 1))
    onset_env = librosa.onset.onset_strength(y=samples, sr=audio.frame_rate)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=audio.frame_rate)
    return float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)


# A persistent process pool so librosa/pydub imports are amortised across batches.
# librosa.beat_track is mostly Python and holds the GIL, so threads don't give us
# real CPU parallelism — processes do.
_executor = None


def _get_executor():
    global _executor
    if _executor is None:
        _executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=min(8, (os.cpu_count() or 4))
        )
    return _executor


async def _bpm_for_track(session, track_id, track_url, executor):
    try:
        preview_url = await _fetch_preview_url(session, track_id)
        if not preview_url:
            return track_url, None
        audio_data = await _download_audio(session, preview_url)
        loop = asyncio.get_running_loop()
        bpm = await loop.run_in_executor(
            executor, _analyze_bpm_from_bytes, audio_data
        )
        return track_url, bpm
    except Exception as exc:
        print(f"{track_url} BPM extraction failed: {exc}")
        return track_url, None


async def process_bpm_urls(tracks, session):
    """`tracks` is an iterable of (track_id, track_url). Return {url: bpm}."""
    executor = _get_executor()
    results = await asyncio.gather(
        *[_bpm_for_track(session, tid, turl, executor) for tid, turl in tracks]
    )
    return {url: bpm for url, bpm in results if bpm is not None}
