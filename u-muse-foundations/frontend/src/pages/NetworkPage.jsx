import { useState } from "react";
import { useNetwork } from "../hooks/useNetwork";
import NetworkGraph from "../components/network/NetworkGraph";

/**
 * Network visualization page for song-to-song similarity links.
 */
export default function NetworkPage() {
    const [includeDescriptorFallback, setIncludeDescriptorFallback] = useState(false);
    const { network, loading, error } = useNetwork({
        includeDescriptorFallback,
        topK: 3,
    });

    if (loading) return <p style={{ padding: "2rem" }}>Loading network...</p>;
    if (error) return <p style={{ padding: "2rem" }}>{error}</p>;

    return (
        <div style={styles.page}>
            <h1 style={styles.title}>Song Similarity Network</h1>
            <p style={styles.subtitle}>
                The graph now shows mutual top-3 neighbors. By default it only links songs when both
                have Essentia audio features, which keeps the network more specific and less cluttered.
            </p>
            <label style={styles.toggle}>
                <input
                    type="checkbox"
                    checked={includeDescriptorFallback}
                    onChange={(event) => setIncludeDescriptorFallback(event.target.checked)}
                />
                Include descriptor fallback for songs that do not have Essentia features
            </label>

            <NetworkGraph network={network} />
        </div>
    );
}

const styles = {
    page: {
        padding: "2rem",
        maxWidth: "1200px",
        margin: "0 auto",
        backgroundColor: "#f8fafc",
        minHeight: "100vh",
    },
    title: {
        marginBottom: "0.25rem",
        color: "#111827",
    },
    subtitle: {
        marginTop: 0,
        marginBottom: "1rem",
        color: "#6b7280",
    },
    toggle: {
        display: "inline-flex",
        alignItems: "center",
        gap: "0.6rem",
        marginBottom: "1.5rem",
        color: "#374151",
        fontWeight: 500,
    },
};
