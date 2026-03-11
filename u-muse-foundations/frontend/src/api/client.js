import axios from "axios";

// Centralized Axios client so hooks/components share one API base URL.
const client = axios.create({
    baseURL: "http://127.0.0.1:5000/api",
});

export default client;
