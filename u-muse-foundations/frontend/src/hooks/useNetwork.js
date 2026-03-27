import { useEffect, useState } from "react";
import client from "../api/client";

/**
 * Load the node/link graph payload for the network page.
 */
export function useNetwork({ includeDescriptorFallback = false, topK = 3 } = {}) {
    const [network, setNetwork] = useState({ nodes: [], links: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        async function fetchNetwork() {
            try {
                setLoading(true);
                setError("");

                const response = await client.get("/network/", {
                    params: {
                        include_descriptor_fallback: includeDescriptorFallback,
                        top_k: topK,
                    },
                });
                setNetwork(response.data);
            } catch (err) {
                console.error(err);
                setError("Failed to load network");
            } finally {
                setLoading(false);
            }
        }

        fetchNetwork();
    }, [includeDescriptorFallback, topK]);

    return { network, loading, error };
}
