"""Feature definitions and helper utilities for the catalog pipeline."""

CATALOG_METADATA_FIELDS = [
    "musicbrainz_recording_id",
    "deezer_id",
    "album_name",
    "release_year",
    "duration_ms",
    "preview_url",
]

CATALOG_FEATURE_FIELDS = [
    "tempo",
    "danceability",
    "gain",
    "mood_happy",
    "mood_sad",
    "mood_relaxed",
    "mood_party",
    "energy",
    "valence",
]

SIMILARITY_FEATURE_KEYS = [
    "tempo",
    "danceability",
    "gain",
    "mood_happy",
    "mood_sad",
    "mood_relaxed",
    "mood_party",
]

FEATURE_LABELS = {
    "tempo": "tempo",
    "danceability": "danceability",
    "gain": "gain",
    "mood_happy": "happy mood",
    "mood_sad": "sad mood",
    "mood_relaxed": "relaxed mood",
    "mood_party": "party mood",
    "energy": "energy proxy",
    "valence": "valence proxy",
}

FEATURE_RANGES = {
    "tempo": (60.0, 200.0),
    "danceability": (0.0, 1.0),
    "gain": (-18.0, 0.0),
    "mood_happy": (0.0, 1.0),
    "mood_sad": (0.0, 1.0),
    "mood_relaxed": (0.0, 1.0),
    "mood_party": (0.0, 1.0),
}

DOMINANT_MOOD_FIELDS = {
    "happy": "mood_happy",
    "party": "mood_party",
    "relaxed": "mood_relaxed",
    "sad": "mood_sad",
}


def _clamp(value, lower, upper):
    """Clamp one numeric value into the provided range."""
    return max(lower, min(upper, value))


def normalize_feature_value(key, value):
    """Normalize one numeric feature for similarity calculations."""
    if value is None:
        return None

    if key not in FEATURE_RANGES:
        return float(value)

    lower, upper = FEATURE_RANGES[key]
    if upper == lower:
        return 0.0

    normalized = (float(value) - lower) / (upper - lower)
    return _clamp(normalized, 0.0, 1.0)


def derive_energy_proxy(payload):
    """Approximate an energy score from gain, danceability, and party mood."""
    components = []

    gain = payload.get("gain")
    if gain is not None:
        components.append((normalize_feature_value("gain", gain), 0.45))

    danceability = payload.get("danceability")
    if danceability is not None:
        components.append((normalize_feature_value("danceability", danceability), 0.25))

    mood_party = payload.get("mood_party")
    if mood_party is not None:
        components.append((normalize_feature_value("mood_party", mood_party), 0.30))

    if not components:
        return None

    weighted_total = sum(value * weight for value, weight in components)
    total_weight = sum(weight for _, weight in components)
    return round(weighted_total / total_weight, 4)


def derive_valence_proxy(payload):
    """Approximate a valence score from happy and sad mood probabilities."""
    happy = payload.get("mood_happy")
    sad = payload.get("mood_sad")

    if happy is None and sad is None:
        return None

    values = []
    if happy is not None:
        values.append(normalize_feature_value("mood_happy", happy))
    if sad is not None:
        values.append(1 - normalize_feature_value("mood_sad", sad))

    return round(sum(values) / len(values), 4)


def build_catalog_payload(musicbrainz_match=None, acousticbrainz_features=None, deezer_match=None):
    """Merge provider payloads into one set of Song model fields."""
    payload = {}

    if musicbrainz_match:
        payload["musicbrainz_recording_id"] = musicbrainz_match.get("musicbrainz_recording_id")
        payload["title"] = musicbrainz_match.get("title")
        payload["artist_name"] = musicbrainz_match.get("artist_name")
        payload["release_year"] = musicbrainz_match.get("release_year")
        payload["duration_ms"] = musicbrainz_match.get("duration_ms")

    if acousticbrainz_features:
        payload["tempo"] = acousticbrainz_features.get("tempo")
        payload["danceability"] = acousticbrainz_features.get("danceability")
        payload["mood_happy"] = acousticbrainz_features.get("mood_happy")
        payload["mood_sad"] = acousticbrainz_features.get("mood_sad")
        payload["mood_relaxed"] = acousticbrainz_features.get("mood_relaxed")
        payload["mood_party"] = acousticbrainz_features.get("mood_party")

    if deezer_match:
        payload["deezer_id"] = deezer_match.get("deezer_id")
        payload["album_name"] = deezer_match.get("album_name") or payload.get("album_name")
        payload["release_year"] = payload.get("release_year") or deezer_match.get("release_year")
        payload["duration_ms"] = payload.get("duration_ms") or deezer_match.get("duration_ms")
        payload["preview_url"] = deezer_match.get("preview_url")
        payload["gain"] = deezer_match.get("gain")
        if payload.get("tempo") is None:
            payload["tempo"] = deezer_match.get("tempo")

    payload["energy"] = derive_energy_proxy(payload)
    payload["valence"] = derive_valence_proxy(payload)
    return payload


def apply_catalog_payload(song, payload):
    """Copy non-null catalog fields onto a Song model."""
    changed = False
    writable_fields = [
        "title",
        "artist_name",
        "spotify_id",
        *CATALOG_METADATA_FIELDS,
        *CATALOG_FEATURE_FIELDS,
    ]

    for key in writable_fields:
        value = payload.get(key)
        if value is None:
            continue

        if getattr(song, key, None) != value:
            setattr(song, key, value)
            changed = True

    return changed


def dominant_mood(song):
    """Return the strongest mood label available for one song."""
    scores = {
        label: getattr(song, field, None)
        for label, field in DOMINANT_MOOD_FIELDS.items()
        if getattr(song, field, None) is not None
    }

    if not scores:
        return "unknown"

    return max(scores.items(), key=lambda item: item[1])[0]


def get_shared_feature_keys(song_a, song_b):
    """List comparable raw features available for both songs."""
    return [
        key for key in SIMILARITY_FEATURE_KEYS
        if getattr(song_a, key, None) is not None and getattr(song_b, key, None) is not None
    ]


def format_feature_labels(keys):
    """Convert internal feature keys into short UI labels."""
    return [FEATURE_LABELS.get(key, key.replace("_", " ")) for key in keys]


def summarize_provider_status(provider_matches, provider_errors):
    """Build short warning messages suitable for the API response."""
    warnings = []

    if not provider_matches.get("musicbrainz"):
        warnings.append("No MusicBrainz recording match found for this query.")
    if provider_matches.get("musicbrainz") and not provider_matches.get("acousticbrainz"):
        warnings.append("MusicBrainz matched, but AcousticBrainz had no feature document for that recording.")
    if not provider_matches.get("deezer"):
        warnings.append("No Deezer metadata match found for this query.")

    for provider, message in provider_errors.items():
        warnings.append(f"{provider} lookup failed: {message}")

    return warnings
