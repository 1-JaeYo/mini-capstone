import { useEffect, useState } from "react";
import client from "../api/client";

/**
 * Fetch similar-song analytics for the currently selected song.
 */
export function useSimilarity(songId) {
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        // Clear state when no selection is active.
        if (!songId) {
            setResult(null);
            return;
        }

        async function fetchSimilarity() {
            try {
                setLoading(true);
                setError("");

                const response = await client.get(`/analytics/similarity/${songId}`);
                setResult(response.data);
            } catch (err) {
                console.error(err);
                setError("Failed to load similar songs");
            } finally {
                setLoading(false);
            }
        }

        fetchSimilarity();
    }, [songId]);

    return { result, loading, error };
}
