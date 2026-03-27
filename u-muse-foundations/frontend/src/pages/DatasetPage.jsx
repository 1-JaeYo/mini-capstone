import { useEffect, useMemo, useRef, useState } from "react";
import client from "../api/client";
import { useSongs } from "../hooks/useSongs";
import { useSimilarity } from "../hooks/useSimilarity";
import SongSearch from "../components/dataset/SongSearch";
import SummaryCards from "../components/dataset/SummaryCards";
import DatasetTable from "../components/dataset/DatasetTable";
import SimilarSongsList from "../components/songs/SimilarSongsList";
import SongDetailPanel from "../components/songs/SongDetailPanel";

/**
 * Dataset workspace:
 * - import songs
 * - inspect metrics
 * - view nearest neighbors for a selected row
 */
export default function DatasetPage() {
    const { songs, loading, error, refreshSongs } = useSongs();
    const [selectedSongId, setSelectedSongId] = useState(null);
    const [analyzingSongId, setAnalyzingSongId] = useState(null);
    const [deletingSongId, setDeletingSongId] = useState(null);
    const [batchAnalyzing, setBatchAnalyzing] = useState(false);
    const [analysisMessage, setAnalysisMessage] = useState("");
    const [analysisError, setAnalysisError] = useState("");
    const [similarityRefreshKey, setSimilarityRefreshKey] = useState(0);
    const audioFeaturesRef = useRef(null);
    const pendingScrollSongIdRef = useRef(null);

    const selectedSong = useMemo(
        () => songs.find((song) => song.id === selectedSongId) || null,
        [songs, selectedSongId]
    );

    const {
        result: similarityResult,
        loading: similarityLoading,
        error: similarityError,
    } = useSimilarity(selectedSongId, similarityRefreshKey);

    useEffect(() => {
        if (
            pendingScrollSongIdRef.current !== null &&
            selectedSong?.id === pendingScrollSongIdRef.current &&
            selectedSong.has_essentia_features &&
            audioFeaturesRef.current
        ) {
            audioFeaturesRef.current.scrollIntoView({
                behavior: "smooth",
                block: "start",
            });
            pendingScrollSongIdRef.current = null;
        }
    }, [selectedSong]);

    async function handleAnalyzeSong(songId) {
        try {
            setSelectedSongId(songId);
            setAnalyzingSongId(songId);
            setAnalysisError("");
            setAnalysisMessage("");
            pendingScrollSongIdRef.current = songId;

            const response = await client.post(`/analyze/${songId}`);
            setAnalysisMessage(response.data.message || "Song analyzed successfully");
            await refreshSongs();
            setSimilarityRefreshKey((value) => value + 1);
        } catch (err) {
            console.error(err);
            pendingScrollSongIdRef.current = null;
            setAnalysisError(err.response?.data?.error || "Failed to analyze song");
        } finally {
            setAnalyzingSongId(null);
        }
    }

    async function handleAnalyzeAll() {
        try {
            setBatchAnalyzing(true);
            setAnalysisError("");
            setAnalysisMessage("");

            const response = await client.post("/analyze/batch");
            const summary = response.data.summary || {};
            setAnalysisMessage(
                `Analyze All finished: ${summary.analyzed ?? 0} analyzed, ${summary.skipped ?? 0} skipped, ${summary.failed ?? 0} failed.`
            );
            await refreshSongs();
            setSimilarityRefreshKey((value) => value + 1);
        } catch (err) {
            console.error(err);
            setAnalysisError(err.response?.data?.error || "Failed to analyze dataset");
        } finally {
            setBatchAnalyzing(false);
        }
    }

    async function handleDeleteSong(songId) {
        try {
            setDeletingSongId(songId);
            setAnalysisError("");
            setAnalysisMessage("");
            pendingScrollSongIdRef.current = null;

            if (selectedSongId === songId) {
                setSelectedSongId(null);
            }

            await client.delete(`/songs/${songId}`);
            setAnalysisMessage("Song removed from dataset");
            await refreshSongs();
            setSimilarityRefreshKey((value) => value + 1);
        } catch (err) {
            console.error(err);
            setAnalysisError(err.response?.data?.error || "Failed to remove song");
        } finally {
            setDeletingSongId(null);
        }
    }

    if (loading) return <p style={{ padding: "2rem" }}>Loading songs...</p>;
    if (error) return <p style={{ padding: "2rem" }}>{error}</p>;

    return (
        <div style={styles.page}>
            <h1 style={styles.title}>U-Muse Dataset</h1>
            <p style={styles.subtitle}>
                Import songs through MusicBrainz, AcousticBrainz, and Deezer to explore tempo,
                danceability, mood, gain, and similarity.
            </p>
            <p style={styles.note}>
                Tempo, danceability, and mood descriptors only appear when AcousticBrainz has data for
                that exact recording. Deezer preview clips and gain coverage are broader.
            </p>

            <SongSearch onImportSuccess={refreshSongs} />
            <div style={styles.toolbar}>
                <button
                    type="button"
                    onClick={handleAnalyzeAll}
                    disabled={batchAnalyzing || songs.length === 0}
                    style={styles.toolbarButton}
                >
                    {batchAnalyzing ? "Analyzing All..." : "Analyze All"}
                </button>
                {analysisMessage ? <span style={styles.success}>{analysisMessage}</span> : null}
                {analysisError ? <span style={styles.error}>{analysisError}</span> : null}
            </div>
            <SummaryCards songs={songs} />
            <DatasetTable
                songs={songs}
                onSelectSong={(song) => setSelectedSongId(song.id)}
                selectedSongId={selectedSongId}
                onAnalyzeSong={handleAnalyzeSong}
                analyzingSongId={analyzingSongId}
                onDeleteSong={handleDeleteSong}
                deletingSongId={deletingSongId}
            />
            <SongDetailPanel
                song={selectedSong}
                onAnalyzeSong={handleAnalyzeSong}
                analyzing={analyzingSongId === selectedSongId}
                audioFeaturesRef={audioFeaturesRef}
            />
            <SimilarSongsList
                result={similarityResult}
                loading={similarityLoading}
                error={similarityError}
            />
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
        marginBottom: "0.5rem",
        color: "#6b7280",
    },
    note: {
        marginTop: 0,
        marginBottom: "2rem",
        color: "#6b7280",
        fontSize: "0.95rem",
    },
    toolbar: {
        display: "flex",
        alignItems: "center",
        gap: "0.75rem",
        marginBottom: "1.25rem",
        flexWrap: "wrap",
    },
    toolbarButton: {
        padding: "0.7rem 1rem",
        borderRadius: "10px",
        border: "none",
        backgroundColor: "#111827",
        color: "#ffffff",
        cursor: "pointer",
        fontWeight: 600,
    },
    success: {
        color: "#166534",
        fontSize: "0.95rem",
    },
    error: {
        color: "#b91c1c",
        fontSize: "0.95rem",
    },
};
