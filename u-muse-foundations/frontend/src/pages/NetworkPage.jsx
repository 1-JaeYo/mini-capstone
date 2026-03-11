import { useNetwork } from "../hooks/useNetwork";
import NetworkGraph from "../components/network/NetworkGraph";

/**
 * Network visualization page for song-to-song similarity links.
 */
export default function NetworkPage() {
    const { network, loading, error } = useNetwork();

    if (loading) return <p style={{ padding: "2rem" }}>Loading network...</p>;
    if (error) return <p style={{ padding: "2rem" }}>{error}</p>;

    return (
        <div style={styles.page}>
            <h1 style={styles.title}>Song Similarity Network</h1>
            <p style={styles.subtitle}>
                Explore relationships between songs based on similarity scores.
            </p>

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
        marginBottom: "2rem",
        color: "#6b7280",
    },
};
