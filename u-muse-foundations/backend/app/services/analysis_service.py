"""Essentia-based analysis helpers for Deezer preview clips."""

from __future__ import annotations

import math
import os
import tempfile
from contextlib import suppress

import numpy as np
import requests

from app.extensions import db
from app.models.song import Song
from app.services.deezer_service import get_track_by_id

ESSENTIA_SAMPLE_RATE = 44100
MFCC_FRAME_SIZE = 2048
MFCC_HOP_SIZE = 1024


class AnalysisUnavailableError(RuntimeError):
    """Raised when the Essentia runtime is not available."""


def ensure_analysis_runtime_available():
    """Raise a clear error if Essentia is unavailable."""
    _load_essentia_modules()


def _load_essentia_modules():
    """Import Essentia lazily so the app still boots without it installed."""
    try:
        import essentia  # type: ignore
        import essentia.standard as estd  # type: ignore
    except ImportError as exc:
        raise AnalysisUnavailableError(
            "Essentia is not installed. This backend needs a supported Essentia setup before "
            "analysis can run. On macOS, the official install path is Homebrew/source build "
            "rather than a plain pip install in this virtualenv."
        ) from exc

    return essentia, estd


def _to_python_scalar(value):
    """Convert Essentia/numpy scalars into plain Python values."""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, "item"):
        with suppress(Exception):
            return value.item()
    return value


def _to_float(value):
    """Convert one numeric-ish value into a Python float."""
    value = _to_python_scalar(value)
    if value is None:
        return None
    return float(value)


def _to_list(values):
    """Convert numpy/Eessentia vectors into JSON-safe Python lists."""
    if values is None:
        return None
    if hasattr(values, "tolist"):
        values = values.tolist()
    return list(values)


def _mean_vector(matrix):
    """Average a list of equal-length vectors into one vector."""
    if matrix is None:
        return None

    array = np.asarray(matrix, dtype=float)
    if array.size == 0:
        return None
    if array.ndim == 1:
        return array.tolist()

    return array.mean(axis=0).tolist()


def _prepare_mfcc_mean(audio, estd):
    """Compute 13 mean MFCC coefficients across frames."""
    window = estd.Windowing(type="hann")
    spectrum = estd.Spectrum()
    mfcc = estd.MFCC(numberCoefficients=13)

    coeff_rows = []
    for frame in estd.FrameGenerator(
        audio,
        frameSize=MFCC_FRAME_SIZE,
        hopSize=MFCC_HOP_SIZE,
        startFromZero=True,
    ):
        _, coeffs = mfcc(spectrum(window(frame)))
        coeff_rows.append(np.array(coeffs[:13], dtype=float))

    return _mean_vector(coeff_rows)


def _prepare_tonal_features(audio, estd):
    """Extract tonal features, including chords and an averaged HPCP vector."""
    (
        _chords_changes_rate,
        _chords_histogram,
        _chords_key,
        _chords_number_rate,
        chords_progression,
        _chords_scale,
        _chords_strength,
        hpcp_frames,
        _hpcp_highres,
        _key_key,
        _key_scale,
        _key_strength,
    ) = estd.TonalExtractor()(audio)

    hpcp_mean = _mean_vector(hpcp_frames)

    return {
        "chords": _to_list(chords_progression),
        "hpcp": hpcp_mean,
    }


def extract_audio_features_from_file(filename):
    """Run Essentia extractors against one local audio file."""
    essentia_module, estd = _load_essentia_modules()

    audio = estd.MonoLoader(filename=filename, sampleRate=ESSENTIA_SAMPLE_RATE)()
    if len(audio) == 0:
        raise ValueError("Downloaded preview clip was empty.")

    bpm, beats, beat_confidence, _estimates, _intervals = estd.RhythmExtractor2013(
        method="multifeature"
    )(audio)
    key, scale, strength = estd.KeyExtractor()(audio)
    loudness = estd.Loudness()(audio)
    energy = estd.Energy()(audio)
    spectral_centroid = estd.SpectralCentroidTime()(audio)
    mfcc_mean = _prepare_mfcc_mean(audio, estd)
    tonal_features = _prepare_tonal_features(audio, estd)
    beats_list = _to_list(beats) or []
    mfcc_values = mfcc_mean if mfcc_mean is not None else []
    hpcp_values = tonal_features["hpcp"] if tonal_features["hpcp"] is not None else []

    return {
        "essentia_bpm": _to_float(bpm),
        "essentia_beats": [float(value) for value in beats_list],
        "essentia_beat_confidence": _to_float(beat_confidence),
        "essentia_key": _to_python_scalar(key),
        "essentia_scale": _to_python_scalar(scale),
        "essentia_key_strength": _to_float(strength),
        "essentia_loudness": _to_float(loudness),
        "essentia_energy": _to_float(energy),
        "essentia_spectral_centroid": _to_float(spectral_centroid),
        "essentia_mfcc_mean": [float(value) for value in mfcc_values],
        "essentia_chords": tonal_features["chords"],
        "essentia_hpcp": [float(value) for value in hpcp_values],
    }


def refresh_song_preview(song):
    """Refresh a Deezer preview URL before downloading audio."""
    if not song.deezer_id:
        raise ValueError("Song does not have a Deezer ID.")

    deezer_track = get_track_by_id(song.deezer_id)
    if not deezer_track or not deezer_track.get("preview_url"):
        raise ValueError("Song does not have a Deezer preview clip.")

    song.preview_url = deezer_track["preview_url"]
    if deezer_track.get("gain") is not None:
        song.gain = deezer_track["gain"]
    if song.tempo is None and deezer_track.get("tempo") is not None:
        song.tempo = deezer_track["tempo"]

    db.session.commit()
    return song.preview_url


def download_preview_to_tempfile(preview_url):
    """Download a preview clip to a temporary file and return its path."""
    response = requests.get(preview_url, timeout=30)
    response.raise_for_status()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    try:
        temp_file.write(response.content)
        return temp_file.name
    finally:
        temp_file.close()


def apply_analysis_to_song(song, analysis_payload):
    """Persist analysis results onto a song model."""
    for key, value in analysis_payload.items():
        setattr(song, key, value)


def analyze_song(song):
    """Refresh, download, analyze, and persist Essentia features for one song."""
    preview_url = refresh_song_preview(song)
    temp_filename = download_preview_to_tempfile(preview_url)

    try:
        analysis_payload = extract_audio_features_from_file(temp_filename)
    finally:
        with suppress(FileNotFoundError):
            os.remove(temp_filename)

    apply_analysis_to_song(song, analysis_payload)
    db.session.commit()
    return analysis_payload


def has_complete_essentia_vector(song):
    """Return True when the Essentia cosine-similarity vector is present."""
    return bool(getattr(song, "has_essentia_features", False))


def normalized_essentia_similarity_vector(song):
    """Build a cosine-similarity vector from stored Essentia features."""
    if not has_complete_essentia_vector(song):
        return None

    mfcc_mean = getattr(song, "essentia_mfcc_mean", None) or []
    if len(mfcc_mean) < 13:
        return None

    vector = [
        (getattr(song, "essentia_bpm", None) or 0.0) / 240.0,
        math.log1p(max(getattr(song, "essentia_energy", None) or 0.0, 0.0)),
        math.log1p(max(getattr(song, "essentia_loudness", None) or 0.0, 0.0)),
        (getattr(song, "essentia_spectral_centroid", None) or 0.0) / (ESSENTIA_SAMPLE_RATE / 2),
    ]
    vector.extend(float(np.tanh(value / 100.0)) for value in mfcc_mean[:13])

    array = np.array(vector, dtype=float)
    norm = float(np.linalg.norm(array))
    if norm == 0:
        return None

    return array / norm
