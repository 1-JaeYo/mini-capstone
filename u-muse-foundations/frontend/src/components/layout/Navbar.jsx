import { NavLink } from "react-router-dom";

/**
 * Top-level navigation across the current pages.
 */
export default function Navbar() {
    return (
        <nav style={styles.nav}>
            <div style={styles.brand}>U-Muse Foundations</div>

            <div style={styles.links}>
                <NavLink
                    to="/"
                    style={({ isActive }) => ({
                        ...styles.link,
                        ...(isActive ? styles.activeLink : {}),
                    })}
                >
                    Dataset
                </NavLink>

                <NavLink
                    to="/network"
                    style={({ isActive }) => ({
                        ...styles.link,
                        ...(isActive ? styles.activeLink : {}),
                    })}
                >
                    Network
                </NavLink>
            </div>
        </nav>
    );
}

const styles = {
    nav: {
        width: "100%",
        boxSizing: "border-box",
        position: "sticky",
        top: 0,
        zIndex: 10,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        padding: "1rem 2rem",
        backgroundColor: "#111827",
        color: "#ffffff",
        borderBottom: "1px solid #1f2937",
    },
    brand: {
        fontWeight: "bold",
        fontSize: "1.1rem",
    },
    links: {
        display: "flex",
        gap: "1rem",
    },
    link: {
        color: "#d1d5db",
        textDecoration: "none",
        fontWeight: 500,
    },
    activeLink: {
        color: "#ffffff",
        borderBottom: "2px solid #ffffff",
        paddingBottom: "0.2rem",
    },
};
