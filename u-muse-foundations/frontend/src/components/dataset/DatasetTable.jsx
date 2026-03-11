/**
 * Tabular dataset browser with selectable rows.
 */
export default function DatasetTable({ songs, onSelectSong, selectedSongId }) {
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
                        <th style={styles.th}>Energy</th>
                        <th style={styles.th}>Danceability</th>
                        {/*
                          Additional audio-feature columns are kept ready for when
                          feature APIs are available (current Spotify restrictions
                          often return 403 for all these metrics).
                        */}
                        {/* <th style={styles.th}>Valence</th>
                        <th style={styles.th}>Acousticness</th>
                        <th style={styles.th}>Instrumentalness</th>
                        <th style={styles.th}>Loudness</th>
                        <th style={styles.th}>Speechiness</th>
                        <th style={styles.th}>Liveness</th> */}
                    </tr>
                </thead>
                <tbody>
                    {songs.map((song) => {
                        const isSelected = selectedSongId === song.id;

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
                                    {formatMetric(song.energy)}
                                </td>
                                <td style={styles.td}>
                                    {formatMetric(song.danceability)}
                                </td>
                                {/* <td style={styles.td}>{formatMetric(song.valence)}</td>
                                <td style={styles.td}>{formatMetric(song.acousticness)}</td>
                                <td style={styles.td}>{formatMetric(song.instrumentalness)}</td>
                                <td style={styles.td}>{formatMetric(song.loudness, 1)}</td>
                                <td style={styles.td}>{formatMetric(song.speechiness)}</td>
                                <td style={styles.td}>{formatMetric(song.liveness)}</td> */}
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
};
