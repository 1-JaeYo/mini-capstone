/**
 * Quick KPI cards derived from numeric song fields.
 */
export default function SummaryCards({ songs }) {
    const totalSongs = songs.length;

    const getAverage = (key) => {
        const validValues = songs
            .map((song) => song[key])
            .filter((value) => typeof value === "number");

        if (validValues.length === 0) return "N/A";

        const sum = validValues.reduce((acc, curr) => acc + curr, 0);
        return (sum / validValues.length).toFixed(2);
    };

    const previewCount = songs.filter((song) => Boolean(song.preview_url)).length;
    const acousticProfileCount = songs.filter(
        (song) => typeof song.tempo === "number" || typeof song.danceability === "number"
    ).length;

    const cards = [
        { label: "Total Songs", value: totalSongs },
        { label: "Songs With Preview", value: previewCount },
        { label: "Songs With Acoustic Profile", value: acousticProfileCount },
        { label: "Average Tempo", value: getAverage("tempo") },
        { label: "Average Gain", value: getAverage("gain") },
        { label: "Average Energy Proxy", value: getAverage("energy") },
    ];

    return (
        <div style={styles.grid}>
            {cards.map((card) => (
                <div key={card.label} style={styles.card}>
                    <p style={styles.label}>{card.label}</p>
                    <h2 style={styles.value}>{card.value}</h2>
                </div>
            ))}
        </div>
    );
}

const styles = {
    grid: {
        display: "grid",
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
        gap: "1rem",
        marginBottom: "2rem",
    },
    card: {
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        padding: "1rem",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    },
    label: {
        margin: 0,
        fontSize: "0.9rem",
        color: "#6b7280",
    },
    value: {
        margin: "0.5rem 0 0 0",
        fontSize: "1.8rem",
        color: "#111827",
    },
};
