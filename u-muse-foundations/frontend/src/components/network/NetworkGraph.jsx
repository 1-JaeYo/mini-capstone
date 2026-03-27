import { useEffect, useMemo, useRef, useState } from "react";

/**
 * Lightweight SVG network renderer.
 *
 * Notes:
 * - Uses a deterministic circular layout (no physics engine dependency).
 * - Scales to container width for responsive display.
 */
export default function NetworkGraph({ network }) {
    const wrapperRef = useRef(null);
    const [width, setWidth] = useState(960);
    const height = Math.max(420, Math.min(700, Math.round(width * 0.62)));

    useEffect(() => {
        const element = wrapperRef.current;
        if (!element) return undefined;

        const updateSize = () => {
            setWidth(Math.max(320, element.clientWidth || 320));
        };

        updateSize();

        if (typeof ResizeObserver !== "undefined") {
            const observer = new ResizeObserver(updateSize);
            observer.observe(element);
            return () => observer.disconnect();
        }

        // ResizeObserver fallback for older browsers.
        window.addEventListener("resize", updateSize);
        return () => window.removeEventListener("resize", updateSize);
    }, []);

    const { positionedNodes, links } = useMemo(() => {
        const nodes = network?.nodes ?? [];
        const linksData = network?.links ?? [];

        if (nodes.length === 0) {
            return { positionedNodes: [], links: [] };
        }

        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.max(120, Math.min(width, height) * 0.34);
        const angleStep = (2 * Math.PI) / nodes.length;

        const laidOut = nodes.map((node, index) => {
            const angle = index * angleStep;
            return {
                ...node,
                x: centerX + radius * Math.cos(angle),
                y: centerY + radius * Math.sin(angle),
            };
        });

        const byId = new Map(laidOut.map((node) => [node.id, node]));
        const normalizedLinks = linksData
            .map((link) => {
                const source = byId.get(link.source);
                const target = byId.get(link.target);
                if (!source || !target) return null;

                return {
                    ...link,
                    sourceNode: source,
                    targetNode: target,
                };
            })
            .filter(Boolean);

        return { positionedNodes: laidOut, links: normalizedLinks };
    }, [network, width, height]);

    if (!positionedNodes.length) {
        return <div style={styles.empty}>No network data available yet.</div>;
    }

    return (
        <div ref={wrapperRef} style={styles.wrapper}>
            <svg
                width={width}
                height={height}
                viewBox={`0 0 ${width} ${height}`}
                role="img"
                aria-label="Song similarity network graph"
            >
                <rect width={width} height={height} fill="#ffffff" />

                {links.map((link, index) => (
                    <line
                        key={`${link.source}-${link.target}-${index}`}
                        x1={link.sourceNode.x}
                        y1={link.sourceNode.y}
                        x2={link.targetNode.x}
                        y2={link.targetNode.y}
                        stroke={link.mode === "descriptor" ? "#cbd5e1" : "#2563eb"}
                        strokeWidth={Math.max(1, (link.weight ?? 0.5) * 2)}
                        opacity={link.mode === "descriptor" ? "0.45" : "0.7"}
                        strokeDasharray={link.mode === "descriptor" ? "4 4" : undefined}
                    />
                ))}

                {positionedNodes.map((node) => (
                    <g key={node.id}>
                        <circle
                            cx={node.x}
                            cy={node.y}
                            r="7"
                            fill={nodeColor(node.dominant_mood)}
                            stroke={node.has_essentia_features ? "#0f172a" : "#ffffff"}
                            strokeWidth={node.has_essentia_features ? 1.5 : 1}
                        />
                        <title>
                            {`${node.label} • ${formatMood(node.dominant_mood)} • ${
                                node.has_essentia_features ? "Essentia ready" : "Descriptor-only"
                            }`}
                        </title>
                        <text
                            x={node.x + 10}
                            y={node.y + 4}
                            fontSize="12"
                            fill="#111827"
                        >
                            {node.label}
                        </text>
                    </g>
                ))}
            </svg>
        </div>
    );
}

function nodeColor(mood) {
    const palette = {
        happy: "#f59e0b",
        party: "#ef4444",
        relaxed: "#14b8a6",
        sad: "#3b82f6",
        unknown: "#64748b",
    };

    return palette[mood] || palette.unknown;
}

function formatMood(mood) {
    if (!mood || mood === "unknown") return "unknown mood";
    return `${mood} mood`;
}

const styles = {
    wrapper: {
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        overflow: "hidden",
        boxShadow: "0 2px 8px rgba(0,0,0,0.05)",
    },
    empty: {
        padding: "2rem",
        backgroundColor: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: "12px",
        color: "#6b7280",
    },
};
