# plex-scripts

Collection of automation scripts for Plex Media Server.

## Overview

This repository provides tools to automate common tasks with Plex. Most notably, it includes scripts to export your Plex library and interact with your server via the [plexapi](https://github.com/pkkid/python-plexapi) Python library.

---

## Script: `plex_export.py`

**`plex_export.py`** exports all items from all your Plex libraries into a single CSV file. Each media item (movie, show, etc) is exported with detailed metadata for easy archival, reporting, or data migration.

### Features

- Automatically connects to your Plex server using environment variables.
- Exports all libraries (Movies, TV Shows, etc) at once.
- Outputs a CSV file named like `plex_library_export_<timestamp>.csv` in the current directory.
- Exports media attributes such as title, year, type, genres, rating, studio, file size, summary, and more.

---

## Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone git@github.com:franklinfreitas/plex-scripts.git
   cd plex-scripts
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   - Create either a `.env` file in the project directory (see `.env.example` or below) or set the environment variables in your session:
   - Populate it with:
     ```
     PLEX_URL=https://your-plex-server.url
     PLEX_TOKEN=your_plex_token
     ```

---

## Usage

To export your entire Plex library to CSV:

```bash
python plex_export.py
```

**The script will:**
- Connect to your server using the values from `PLEX_URL` and `PLEX_TOKEN` environment variables
- List your available libraries (Movies, TV Shows, etc)
- Export all media items to a CSV file named `plex_library_export_<timestamp>.csv`
- Save the CSV in the current directory

You will see progress in the terminal as libraries and items are processed.

---

### Example .env file

```
PLEX_URL=http://localhost:32400
PLEX_TOKEN=xxxxxxxxxxxxxxxxxxxx
```

---

## Troubleshooting

- **No libraries found?** Make sure `PLEX_URL` and `PLEX_TOKEN` are set correctly either in a `.env` file or as environment variables and your Plex server is accessible from your machine.
- **Plex token:** Learn how to find your Plex token [here](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).
- **Dependencies:** Install all required Python packages using `pip install -r requirements.txt`.

---
