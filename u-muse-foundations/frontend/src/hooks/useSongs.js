import { useEffect, useState, useCallback } from "react";
import client from "../api/client";

/**
 * Fetch and cache song rows for the dataset view.
 */
export function useSongs() {
    const [songs, setSongs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const fetchSongs = useCallback(async () => {
        try {
            setLoading(true);
            setError("");
            const response = await client.get("/songs/");
            setSongs(response.data);
        } catch (err) {
            console.error(err);
            setError("Failed to load songs");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchSongs();
    }, [fetchSongs]);

    // Expose `refreshSongs` so import actions can force a re-fetch.
    return { songs, loading, error, refreshSongs: fetchSongs };
}
