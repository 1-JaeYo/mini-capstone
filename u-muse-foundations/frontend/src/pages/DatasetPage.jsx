import { useState } from "react";
import { useSongs } from "../hooks/useSongs";
import { useSimilarity } from "../hooks/useSimilarity";
import SongSearch from "../components/dataset/SongSearch";
import SummaryCards from "../components/dataset/SummaryCards";
import DatasetTable from "../components/dataset/DatasetTable";
import SimilarSongsList from "../components/songs/SimilarSongsList";

/**
 * Dataset workspace:
 * - import songs
 * - inspect metrics
 * - view nearest neighbors for a selected row
 */
export default function DatasetPage() {
    const { songs, loading, error, refreshSongs } = useSongs();
    const [selectedSong, setSelectedSong] = useState(null);

    const {
        result: similarityResult,
        loading: similarityLoading,
        error: similarityError,
    } = useSimilarity(selectedSong?.id);

    if (loading) return <p style={{ padding: "2rem" }}>Loading songs...</p>;
    if (error) return <p style={{ padding: "2rem" }}>{error}</p>;

    return (
        <div style={styles.page}>
            <h1 style={styles.title}>U-Muse Dataset</h1>
            <p style={styles.subtitle}>
                Import songs from Spotify, explore the dataset, and compare musical similarity.
            </p>

            <SongSearch onImportSuccess={refreshSongs} />
            <SummaryCards songs={songs} />
            <DatasetTable
                songs={songs}
                onSelectSong={setSelectedSong}
                selectedSongId={selectedSong?.id}
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
        marginBottom: "2rem",
        color: "#6b7280",
    },
};
