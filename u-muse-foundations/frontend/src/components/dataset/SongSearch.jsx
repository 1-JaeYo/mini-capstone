import { useState } from "react";
import client from "../../api/client";

/**
 * Song import form that sends a query to the backend import endpoint.
 */
export default function SongSearch({ onImportSuccess }) {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [error, setError] = useState("");
    const [warning, setWarning] = useState("");

    async function handleSubmit(e) {
        e.preventDefault();

        if (!query.trim()) {
            setError("Enter a song title and artist.");
            return;
        }

        try {
            setLoading(true);
            setError("");
            setMessage("");
            setWarning("");

            const res = await client.post("/imports/spotify", {
                query: query.trim(),
            });

            setMessage(res.data.message || "Song imported");
            if (res.data.feature_error) {
                // Surface provider-side feature failures so users know why
                // downstream metrics might still show as "N/A".
                setWarning(`Imported, but audio features were not fetched: ${res.data.feature_error}`);
            }
            setQuery("");

            if (onImportSuccess) {
                onImportSuccess();
            }
        } catch (err) {
            console.error(err);

            if (err.response?.data?.error) {
                setError(err.response.data.error);
            } else {
                setError("Import failed");
            }
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={styles.container}>
            <h2>Import Song</h2>

            <form onSubmit={handleSubmit} style={styles.form}>
                <input
                    type="text"
                    placeholder="e.g. DRIVING - Eddie Benjamin"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    style={styles.input}
                />

                <button type="submit" disabled={loading} style={styles.button}>
                    {loading ? "Importing..." : "Import"}
                </button>
            </form>

            {message && <p style={styles.success}>{message}</p>}
            {warning && <p style={styles.warning}>{warning}</p>}
            {error && <p style={styles.error}>{error}</p>}
        </div>
    );
}

const styles = {
    container: {
        marginBottom: "2rem",
    },
    form: {
        display: "flex",
        gap: "0.5rem",
    },
    input: {
        flex: 1,
        padding: "0.7rem",
        borderRadius: "8px",
        border: "1px solid #ddd",
    },
    button: {
        padding: "0.7rem 1rem",
        borderRadius: "8px",
        border: "none",
        backgroundColor: "#111",
        color: "white",
        cursor: "pointer",
    },
    success: {
        color: "green",
    },
    error: {
        color: "red",
    },
    warning: {
        color: "#92400e",
        backgroundColor: "#fffbeb",
        border: "1px solid #fde68a",
        borderRadius: "8px",
        padding: "0.5rem 0.75rem",
    },
};
