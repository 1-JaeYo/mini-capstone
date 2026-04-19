# Mini-Capstone

This repository contains the final mini-capstone project workspace. The main project in this repo is:

- [`u-muse-foundations`](./u-muse-foundations)

## Project Summary

**U-Muse Foundations** is a full-stack music analysis and exploration app. It lets a user:

- import songs into a local dataset
- enrich songs with metadata from multiple providers
- analyze 30-second preview clips with Essentia
- compare songs by similarity
- explore connections through a network graph

The app uses:

- **Flask** + **SQLAlchemy** + **SQLite** for the backend
- **React** + **Vite** for the frontend
- **Spotify** for exact track identity/search
- **MusicBrainz** for recording identity
- **AcousticBrainz** for open descriptor-style features
- **Deezer** for preview clips and additional metadata
- **Essentia** for audio feature extraction

## Repository Layout

```text
mini-capstone/
├── README.md
└── u-muse-foundations/
    ├── backend/
    ├── frontend/
    └── run-dev.sh
```

## Main Features

- Spotify-first song import
- Multi-provider metadata enrichment
- Local dataset stored in SQLite
- Essentia-based audio analysis
- Similar-song recommendations
- Network graph visualization
- Batch analysis workflow

## Quick Start

The main app lives in [`u-muse-foundations`](./u-muse-foundations).

### Option 1: Start both frontend and backend together

From the project folder:

```bash
cd u-muse-foundations
./run-dev.sh
```

This starts:

- the Flask backend from `backend/venv/bin/python run.py`
- the React frontend with Vite

Press `Ctrl+C` to stop both.

### Option 2: Run them separately

Backend:

```bash
cd u-muse-foundations/backend
source venv/bin/activate
python run.py
```

Frontend:

```bash
cd u-muse-foundations/frontend
npm run dev
```

## Environment Notes

The backend reads configuration from:

- [`u-muse-foundations/backend/.env`](./u-muse-foundations/backend/.env)

Important variables include:

- `SPOTIFY_CLIENT_ID`
- `SPOTIFY_CLIENT_SECRET`
- `MUSIC_METADATA_USER_AGENT`
- `MUSIC_METADATA_CONTACT` (optional)

The backend database defaults to a local SQLite file in:

- `u-muse-foundations/backend/instance/u_muse.db`

## Fresh Setup

If you need to recreate the environment instead of using the existing project setup:

### Backend

```bash
cd u-muse-foundations/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

### Frontend

```bash
cd u-muse-foundations/frontend
npm install
npm run dev
```

## Backend API Areas

The Flask app exposes these main route groups:

- `/api/songs`
- `/api/imports`
- `/api/analytics`
- `/api/network`
- `/api/analyze`

## Current State

This is the final version of the project prepared for presentation/demo. The system is designed as a working research prototype rather than a production deployment.

## Notes

- Deezer preview links can expire, so the backend refreshes them on demand.
- AcousticBrainz coverage is incomplete, so some songs will not have all descriptor fields.
- Similarity prefers Essentia-based vectors when available and falls back to descriptor matching otherwise.
