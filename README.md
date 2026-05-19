# F1-mini-project (F1 Race Replay)

F1 Race Replay is a Streamlit dashboard for exploring F1 sessions (2018–2025) using the FastF1 API. It features animated position replays, circuit speed maps, lap time analysis with tyre data, gap-to-leader charts, and head-to-head driver duels. Built with Python, Plotly, Pandas, and NumPy in a polished dark-themed UI.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run src/app.py
```

Open http://localhost:8501, pick a year/GP/session in the sidebar, and hit **Load Session**.

## Project layout

```
f1-race-replay/
├── cache/          FastF1 data cache (git-ignored)
├── data/           Raw and processed session data
├── src/
│   ├── data/       Session loading, processing, cache setup
│   ├── viz/        Animated Plotly chart, team colors, helpers
│   └── app.py      Streamlit entry point
├── notebooks/      Exploratory Jupyter notebooks
└── assets/         Static files
```

## Notes

- First load for a session downloads data from the Ergast/FastF1 API and caches it locally.
- Subsequent loads are instant from cache.
- Tested with FastF1 ≥ 3.3 and Python 3.11.
