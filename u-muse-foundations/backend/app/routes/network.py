"""Network graph endpoints for song similarity visualization."""

from flask import Blueprint, jsonify, request
from app.models.song import Song
from app.services.feature_service import dominant_mood
from app.services.similarity_service import compute_similarity_details

network_bp = Blueprint("network", __name__)


@network_bp.get("/")
def get_network():
    """Build a graph payload with mutual nearest-neighbor similarity links."""
    songs = Song.query.all()
    include_descriptor_fallback = request.args.get("include_descriptor_fallback", "").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    top_k = request.args.get("top_k", default=3, type=int) or 3
    top_k = max(1, min(top_k, 5))
    min_similarity = request.args.get(
        "min_similarity",
        default=(0.68 if include_descriptor_fallback else 0.82),
        type=float,
    )

    nodes = [
        {
            "id": song.id,
            "label": song.title,
            "artist_name": song.artist_name,
            "dominant_mood": dominant_mood(song),
            "has_essentia_features": song.has_essentia_features,
        }
        for song in songs
    ]

    if len(songs) < 2:
        return jsonify({
            "nodes": nodes,
            "links": [],
            "meta": {
                "top_k": top_k,
                "min_similarity": min_similarity,
                "include_descriptor_fallback": include_descriptor_fallback,
            },
        })

    neighbor_lookup = {}
    for source_song in songs:
        ranked_neighbors = []
        for target_song in songs:
            if source_song.id == target_song.id:
                continue

            similarity, mode = compute_similarity_details(
                source_song,
                target_song,
                allow_descriptor_fallback=include_descriptor_fallback,
            )
            if similarity is None or similarity < min_similarity:
                continue

            ranked_neighbors.append({
                "target": target_song.id,
                "weight": similarity,
                "mode": mode,
            })

        ranked_neighbors.sort(key=lambda item: item["weight"], reverse=True)
        neighbor_lookup[source_song.id] = {
            neighbor["target"]: neighbor
            for neighbor in ranked_neighbors[:top_k]
        }

    links = []
    seen_pairs = set()
    for source_id, neighbors in neighbor_lookup.items():
        for target_id, edge in neighbors.items():
            reverse_edge = neighbor_lookup.get(target_id, {}).get(source_id)
            if not reverse_edge:
                continue

            pair_key = tuple(sorted((source_id, target_id)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            links.append({
                "source": pair_key[0],
                "target": pair_key[1],
                "weight": round((edge["weight"] + reverse_edge["weight"]) / 2, 4),
                "mode": edge["mode"],
            })

    return jsonify({
        "nodes": nodes,
        "links": links,
        "meta": {
            "top_k": top_k,
            "min_similarity": min_similarity,
            "include_descriptor_fallback": include_descriptor_fallback,
        },
    })
