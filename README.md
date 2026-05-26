# F1 Race Replay 🏎️

A Streamlit dashboard for exploring Formula 1 sessions (2018–2025) with interactive visualizations powered by the FastF1 API.

## Features ✨

- **Animated Position Replays** – Watch drivers' positions change lap-by-lap with smooth animations
- **Circuit Speed Maps** – Visualize driver speeds around the track at each corner
- **Lap Time Analysis** – Compare lap times with real-time tyre compound data
- **Gap-to-Leader Charts** – Track how drivers' gaps evolved throughout the session
- **Head-to-Head Driver Duels** – Analyze direct driver-vs-driver matchups
- **Dark-Themed UI** – Modern, polished interface for optimal viewing
- **Instant Caching** – First load downloads data; subsequent loads are instant
- **Sessions 2018–2025** – Access 8+ years of F1 telemetry data

## Tech Stack 🛠️

- **Frontend:** [Streamlit](https://streamlit.io/) – Interactive web app framework
- **Data API:** [FastF1](https://theoehrly.github.io/Fast-F1/) – F1 session and telemetry data
- **Visualization:** [Plotly](https://plotly.com/) – Interactive charts and animations
- **Data Processing:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
- **Language:** Python 3.11+

## Quick Start 🚀

### Installation

```bash
git clone https://github.com/jhingaa/F1-mini-project.git
cd F1-mini-project
pip install -r requirements.txt
```

### Run the App

```bash
streamlit run src/app.py
```

The dashboard will open at `http://localhost:8501`. 

1. Select a **year**, **Grand Prix**, and **session type** (Practice, Qualifying, Race) from the sidebar
2. Click **Load Session** to fetch and cache the data
3. Explore the interactive visualizations

## Project Structure 📁

```
F1-mini-project/
├── cache/                # FastF1 data cache (auto-generated, git-ignored)
├── data/                 # Raw and processed session data
├── src/
│   ├── data/            # Session loading, processing, cache initialization
│   ├── viz/             # Animated Plotly charts, team colors, visualization utilities
│   └── app.py           # Streamlit app entry point
├── notebooks/           # Exploratory Jupyter notebooks for analysis
├── assets/              # Static files (logos, images, etc.)
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## How It Works 🔧

1. **Data Fetching:** FastF1 downloads session data from the Ergast API and F1 telemetry sources
2. **Caching:** Data is cached locally in the `cache/` directory for faster subsequent loads
3. **Processing:** Lap and telemetry data is processed, aligned, and formatted for visualization
4. **Visualization:** Plotly renders interactive, animated charts with real-time interactivity

**First load:** May take 30–60 seconds to download and cache data  
**Subsequent loads:** Instant from cache ⚡

## Requirements

- **Python:** 3.11+
- **FastF1:** ≥ 3.3
- **Dependencies:** See `requirements.txt`

## Usage Examples 📊

### Explore Race Progression
Load a race session to see animated position changes, pit stop strategies, and lap-by-lap performance.

### Analyze Qualifying Performance
Compare qualifying laps with sector times and check optimal tyre strategies.

### Study Practice Sessions
Review FP1, FP2, FP3 data to understand car setup changes and driver performance trends.

### Driver Comparisons
Use head-to-head mode to analyze specific driver matchups and competitive battles.

## Development 💡

### Running Tests
```bash
pytest tests/
```

### Exploring Data
Jupyter notebooks in `notebooks/` contain exploratory analysis and data inspection examples.

## Performance Notes ⚡

- **Initial Session Load:** 30–60 seconds (downloads 500MB–2GB of telemetry data)
- **Cached Sessions:** <1 second
- **Animations:** Smooth 60 FPS on modern hardware
- **Memory:** ~500MB for a full race weekend cache

## Troubleshooting 🐛

### Data Won't Load
- Check your internet connection (FastF1 requires API access)
- Ensure FastF1 ≥ 3.3 is installed: `pip install --upgrade fastf1`
- Clear the cache: `rm -rf cache/`

### Slow Performance
- The first load for any session downloads large telemetry files
- Clear old cache files to free disk space: `rm -rf cache/`

### Missing Sessions
- F1 historical data (pre-2018) is limited in FastF1. Only 2018–2025 sessions are reliable.

## Contributing 🤝

Contributions are welcome! Please feel free to:
- Report issues
- Suggest features
- Submit pull requests

## License 📜

This project is open-source. See the LICENSE file for details.

## Credits 🏁

- **FastF1:** [theoehrly/Fast-F1](https://github.com/theoehrly/Fast-F1) – F1 data library
- **Streamlit:** Interactive web framework
- **Formula 1:** Official race data via Ergast API

## Resources 📚

- [FastF1 Documentation](https://theoehrly.github.io/Fast-F1/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [F1 Data Sources](https://ergast.com/mrd/)

---

**Enjoy exploring F1 data! 🏁**
