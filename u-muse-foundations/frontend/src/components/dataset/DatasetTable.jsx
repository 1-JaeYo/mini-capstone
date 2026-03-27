import { API_BASE_URL } from "../../api/client";

/**
 * Tabular dataset browser with selectable rows.
 */
export default function DatasetTable({
    songs,
    onSelectSong,
    selectedSongId,
    onAnalyzeSong,
    analyzingSongId,
    onDeleteSong,
    deletingSongId,
}) {
    return (
        <div style={styles.wrapper}>
            <table style={styles.table}>
                <thead>
                    <tr>
                        <th style={styles.th}>Title</th>
                        <th style={styles.th}>Artist</th>
                        <th style={styles.th}>Album</th>
                        <th style={styles.th}>Year</th>
                        <th style={styles.th}>Tempo</th>
                        <th style={styles.th}>Danceability</th>
                        <th style={styles.th}>Gain</th>
                        <th style={styles.th}>Energy Proxy</th>
                        <th style={styles.th}>Dominant Mood</th>
                        <th style={styles.th}>Essentia</th>
                        <th style={styles.th}>Preview</th>
                        <th style={styles.th}>Analyze</th>
                        <th style={styles.iconTh}></th>
                    </tr>
                </thead>
                <tbody>
                    {songs.map((song) => {
                        const isSelected = selectedSongId === song.id;
                        const isAnalyzing = analyzingSongId === song.id;
                        const isDeleting = deletingSongId === song.id;

                        return (
                            <tr
                                key={song.id}
                                onClick={() => onSelectSong(song)}
                                style={{
                                    ...styles.row,
                                    ...(isSelected ? styles.selectedRow : {}),
                                }}
                            >
                                <td style={styles.td}>{song.title}</td>
                                <td style={styles.td}>{song.artist_name}</td>
                                <td style={styles.td}>{song.album_name || "N/A"}</td>
                                <td style={styles.td}>{song.release_year || "N/A"}</td>
                                <td style={styles.td}>
                                    {formatMetric(song.tempo, 1)}
                                </td>
                                <td style={styles.td}>
                                    {formatMetric(song.danceability)}
                                </td>
                                <td style={styles.td}>
                                    {formatMetric(song.gain, 1)}
                                </td>
                                <td style={styles.td}>
                                    {formatMetric(song.energy)}
                                </td>
                                <td style={styles.td}>
                                    {formatMood(song.dominant_mood)}
                                </td>
                                <td style={styles.td}>
                                    <span
                                        style={{
                                            ...styles.statusBadge,
                                            ...(song.has_essentia_features
                                                ? styles.statusReady
                                                : styles.statusMissing),
                                        }}
                                    >
                                        <span
                                            style={{
                                                ...styles.statusDot,
                                                backgroundColor: song.has_essentia_features
                                                    ? "#16a34a"
                                                    : "#94a3b8",
                                            }}
                                        />
                                        {song.has_essentia_features ? "Ready" : "Missing"}
                                    </span>
                                </td>
                                <td style={styles.td}>
                                    {song.deezer_id ? (
                                        <a
                                            href={`${API_BASE_URL}/songs/${song.id}/preview`}
                                            target="_blank"
                                            rel="noreferrer"
                                            onClick={(event) => event.stopPropagation()}
                                            style={styles.previewLink}
                                        >
                                            Clip
                                        </a>
                                    ) : (
                                        "N/A"
                                    )}
                                </td>
                                <td style={styles.td}>
                                    <button
                                        type="button"
                                        onClick={(event) => {
                                            event.stopPropagation();
                                            onAnalyzeSong(song.id);
                                        }}
                                        disabled={isAnalyzing}
                                        style={styles.analyzeButton}
                                    >
                                        {isAnalyzing ? "Analyzing..." : "Analyze"}
                                    </button>
                                </td>
                                <td style={{ ...styles.td, ...styles.iconCell }}>
                                    <button
                                        type="button"
                                        onClick={(event) => {
                                            event.stopPropagation();
                                            onDeleteSong(song.id);
                                        }}
                                        disabled={isDeleting || isAnalyzing}
                                        aria-label={`Remove ${song.title}`}
                                        title={`Remove ${song.title}`}
                                        style={styles.deleteButton}
                                    >
                                        &times;
                                    </button>
                                </td>
                            </tr>
                        );
                    })}
                </tbody>
            </table>
        </div>
    );
}

function formatMetric(value, digits = 2) {
    // Keep formatting consistent while handling missing/null data.
    return typeof value === "number" ? value.toFixed(digits) : "N/A";
}

function formatMood(value) {
    if (!value || value === "unknown") return "N/A";
    return value[0].toUpperCase() + value.slice(1);
}

const styles = {
    wrapper: {
        overflowX: "auto",
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    },
    table: {
        width: "100%",
        borderCollapse: "collapse",
    },
    th: {
        textAlign: "left",
        padding: "0.9rem",
        borderBottom: "1px solid #e5e7eb",
        backgroundColor: "#f9fafb",
        color: "#374151",
        fontSize: "0.95rem",
    },
    iconTh: {
        width: "1%",
        whiteSpace: "nowrap",
        padding: "0.9rem",
        borderBottom: "1px solid #e5e7eb",
        backgroundColor: "#f9fafb",
    },
    td: {
        padding: "0.9rem",
        borderBottom: "1px solid #f3f4f6",
        fontSize: "0.95rem",
        color: "#111827",
    },
    row: {
        cursor: "pointer",
    },
    selectedRow: {
        backgroundColor: "#eef2ff",
    },
    previewLink: {
        color: "#2563eb",
        textDecoration: "none",
        fontWeight: 600,
    },
    iconCell: {
        textAlign: "center",
    },
    analyzeButton: {
        padding: "0.5rem 0.8rem",
        borderRadius: "8px",
        border: "1px solid #d1d5db",
        backgroundColor: "#ffffff",
        cursor: "pointer",
        fontWeight: 600,
    },
    deleteButton: {
        width: "2rem",
        height: "2rem",
        borderRadius: "999px",
        border: "1px solid #fecaca",
        backgroundColor: "#fff1f2",
        color: "#b91c1c",
        cursor: "pointer",
        fontSize: "1.2rem",
        lineHeight: 1,
        fontWeight: 700,
    },
    statusBadge: {
        display: "inline-flex",
        alignItems: "center",
        gap: "0.4rem",
        borderRadius: "999px",
        padding: "0.3rem 0.6rem",
        fontSize: "0.8rem",
        fontWeight: 600,
    },
    statusReady: {
        backgroundColor: "#dcfce7",
        color: "#166534",
    },
    statusMissing: {
        backgroundColor: "#e5e7eb",
        color: "#475569",
    },
    statusDot: {
        width: "0.5rem",
        height: "0.5rem",
        borderRadius: "999px",
        display: "inline-block",
    },
};
