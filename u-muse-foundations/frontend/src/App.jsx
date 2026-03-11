import './App.css'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/layout/Navbar";
import DatasetPage from "./pages/DatasetPage";
import NetworkPage from "./pages/NetworkPage";

/**
 * Root application layout and route mapping.
 */
function App() {
  return (
    <BrowserRouter>
      <Navbar />
      <Routes>
        <Route path="/" element={<DatasetPage />} />
        <Route path="/network" element={<NetworkPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
