/**
 * Shows nearest-neighbor songs for the selected dataset row.
 */
export default function SimilarSongsList({ result, loading, error }) {
    if (!result && !loading) {
        return (
            <div style={styles.card}>
                <h2 style={styles.heading}>Similar Songs</h2>
                <p style={styles.subtext}>Select a song from the table to view similarity results.</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div style={styles.card}>
                <h2 style={styles.heading}>Similar Songs</h2>
                <p style={styles.subtext}>Loading similarity results...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div style={styles.card}>
                <h2 style={styles.heading}>Similar Songs</h2>
                <p style={styles.error}>{error}</p>
            </div>
        );
    }

    const baseSong = result?.base_song;
    const similarSongs = result?.similar_songs || [];

    return (
        <div style={styles.card}>
            <h2 style={styles.heading}>Similar Songs</h2>

            {baseSong && (
                <p style={styles.subtext}>
                    Selected song: <strong>{baseSong.title}</strong> by {baseSong.artist_name}
                </p>
            )}

            {similarSongs.length === 0 ? (
                <p style={styles.subtext}>No similar songs found with the current available features.</p>
            ) : (
                <ul style={styles.list}>
                    {similarSongs.map((song) => (
                        <li key={song.song_id} style={styles.item}>
                            <div>
                                <strong>{song.title}</strong> by {song.artist_name}
                            </div>
                            <div style={styles.score}>Similarity: {song.similarity_score}</div>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

const styles = {
    card: {
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        padding: "1rem",
        marginTop: "1.5rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    },
    heading: {
        marginTop: 0,
        marginBottom: "0.5rem",
        color: "#111827",
    },
    subtext: {
        color: "#6b7280",
        marginBottom: "1rem",
    },
    error: {
        color: "#b91c1c",
    },
    list: {
        listStyle: "none",
        padding: 0,
        margin: 0,
    },
    item: {
        padding: "0.75rem 0",
        borderBottom: "1px solid #f3f4f6",
    },
    score: {
        color: "#4b5563",
        fontSize: "0.9rem",
        marginTop: "0.25rem",
    },
};
