/**
 * Selected-song detail card with Essentia analysis results.
 */
export default function SongDetailPanel({
    song,
    onAnalyzeSong,
    analyzing,
    audioFeaturesRef,
}) {
    if (!song) {
        return (
            <div style={styles.card}>
                <h2 style={styles.heading}>Song Details</h2>
                <p style={styles.subtext}>Select a song from the table to inspect its metadata and audio features.</p>
            </div>
        );
    }

    const essentia = song.essentia || {};
    const mfcc = Array.isArray(essentia.mfcc_mean) ? essentia.mfcc_mean : [];

    return (
        <div style={styles.card}>
            <div style={styles.header}>
                <div>
                    <h2 style={styles.heading}>{song.title}</h2>
                    <p style={styles.subtext}>
                        {song.artist_name} {song.album_name ? `· ${song.album_name}` : ""}
                    </p>
                </div>
                <button
                    type="button"
                    onClick={() => onAnalyzeSong(song.id)}
                    disabled={analyzing}
                    style={styles.button}
                >
                    {analyzing ? "Analyzing..." : "Analyze"}
                </button>
            </div>

            <div style={styles.metaGrid}>
                <Metric label="Year" value={song.release_year || "N/A"} />
                <Metric label="Preview" value={song.preview_url ? "Available" : "Missing"} />
                <Metric label="Essentia" value={song.has_essentia_features ? "Ready" : "Missing"} />
                <Metric label="Dominant Mood" value={formatLabel(song.dominant_mood)} />
            </div>

            {song.has_essentia_features ? (
                <div ref={audioFeaturesRef} style={styles.section}>
                    <h3 style={styles.sectionHeading}>Audio Features</h3>
                    <div style={styles.metaGrid}>
                        <Metric label="Key" value={formatKey(essentia)} />
                        <Metric label="BPM" value={formatMetric(essentia.bpm, 1)} />
                        <Metric label="Energy" value={formatMetric(essentia.energy, 3)} />
                        <Metric label="Loudness" value={formatMetric(essentia.loudness, 3)} />
                        <Metric label="Brightness" value={formatMetric(essentia.spectral_centroid, 1)} />
                        <Metric label="Beat Confidence" value={formatMetric(essentia.beat_confidence, 3)} />
                    </div>

                    <div style={styles.mfccSection}>
                        <h4 style={styles.mfccHeading}>MFCC Mean Coefficients</h4>
                        <div style={styles.mfccBars}>
                            {mfcc.map((value, index) => (
                                <div key={`${song.id}-mfcc-${index}`} style={styles.mfccBarWrap}>
                                    <div
                                        style={{
                                            ...styles.mfccBar,
                                            height: `${Math.max(10, Math.min(100, Math.abs(value) * 2.5))}%`,
                                            backgroundColor: value >= 0 ? "#2563eb" : "#ef4444",
                                        }}
                                    />
                                    <span style={styles.mfccLabel}>{index + 1}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            ) : (
                <div ref={audioFeaturesRef} style={styles.section}>
                    <h3 style={styles.sectionHeading}>Audio Features</h3>
                    <p style={styles.subtext}>
                        Essentia features have not been computed for this song yet.
                    </p>
                </div>
            )}
        </div>
    );
}

function Metric({ label, value }) {
    return (
        <div style={styles.metric}>
            <span style={styles.metricLabel}>{label}</span>
            <strong style={styles.metricValue}>{value}</strong>
        </div>
    );
}

function formatMetric(value, digits = 2) {
    return typeof value === "number" ? value.toFixed(digits) : "N/A";
}

function formatKey(essentia) {
    if (!essentia?.key) return "N/A";
    return `${essentia.key} ${essentia.scale || ""}`.trim();
}

function formatLabel(value) {
    if (!value || value === "unknown") return "N/A";
    return value[0].toUpperCase() + value.slice(1);
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
    header: {
        display: "flex",
        justifyContent: "space-between",
        alignItems: "flex-start",
        gap: "1rem",
    },
    heading: {
        margin: 0,
        color: "#111827",
    },
    sectionHeading: {
        margin: "0 0 0.75rem 0",
        color: "#111827",
    },
    subtext: {
        color: "#6b7280",
        marginTop: "0.35rem",
        marginBottom: 0,
    },
    button: {
        padding: "0.65rem 0.95rem",
        borderRadius: "10px",
        border: "1px solid #d1d5db",
        backgroundColor: "#ffffff",
        cursor: "pointer",
        fontWeight: 600,
    },
    metaGrid: {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))",
        gap: "0.75rem",
        marginTop: "1rem",
    },
    metric: {
        border: "1px solid #e5e7eb",
        borderRadius: "10px",
        padding: "0.75rem",
        backgroundColor: "#f8fafc",
    },
    metricLabel: {
        display: "block",
        color: "#6b7280",
        fontSize: "0.85rem",
        marginBottom: "0.35rem",
    },
    metricValue: {
        color: "#111827",
    },
    section: {
        marginTop: "1.25rem",
    },
    mfccSection: {
        marginTop: "1rem",
    },
    mfccHeading: {
        margin: "0 0 0.75rem 0",
        fontSize: "0.95rem",
        color: "#374151",
    },
    mfccBars: {
        display: "grid",
        gridTemplateColumns: "repeat(13, minmax(0, 1fr))",
        gap: "0.4rem",
        alignItems: "end",
        minHeight: "140px",
        padding: "0.75rem",
        borderRadius: "10px",
        backgroundColor: "#f8fafc",
        border: "1px solid #e5e7eb",
    },
    mfccBarWrap: {
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "flex-end",
        gap: "0.35rem",
        height: "120px",
    },
    mfccBar: {
        width: "100%",
        borderRadius: "6px 6px 0 0",
    },
    mfccLabel: {
        fontSize: "0.75rem",
        color: "#6b7280",
    },
};
