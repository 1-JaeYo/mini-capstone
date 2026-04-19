import axios from "axios";

// Centralized Axios client so hooks/components share one API base URL.
export const API_BASE_URL = import.meta.env.DEV
    ? "http://127.0.0.1:5000/api"
    : "/_/backend/api";

const client = axios.create({
    baseURL: API_BASE_URL,
});

export default client;
