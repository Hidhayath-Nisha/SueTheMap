# 🗺️ Sue the Map

**AI Litigation Intelligence Tool** — GeorgeHacksxAI 2026

An interactive 3D globe visualizing every AI lawsuit in the United States, powered by the [Database of AI Litigation (DAIL)](https://dail.gwlaw.edu) from GW Law.

![Sue the Map](https://img.shields.io/badge/cases-293-red) ![States](https://img.shields.io/badge/states-34-blue) ![Uncovered](https://img.shields.io/badge/uncovered-139-orange)

## Features

- **3D Interactive Globe** — US states colored by AI lawsuit volume (blue → red heat scale)
- **Law Mode / Public Mode** — toggle between legal terminology and plain language
- **Voice AI** — speak your question, get a Claude-powered legal briefing
- **Journalist Alerts** — 139 active AI lawsuits with zero press coverage
- **Timeline Chart** — annual case filing trends 2011–2026 with ChatGPT annotation
- **Sector Breakdown** — filter by Generative AI, Civil Rights, Copyright, Facial Recognition, and more
- **State Briefings** — click any state for full docket: stats, sectors, sparkline, case cards with sources

## Quick Start

1. Open `sue_the_map.html` in **Chrome or Edge**
2. (Optional) Add your Anthropic API key at the top of the `<script>` block to enable AI queries
3. Click any state on the globe

No build step. No server. No npm. Single HTML file.

## Data

Source: **Database of AI Litigation (DAIL)** — George Washington University Law School  
- 293 cases across 34 US states (2011–2026)
- 154 cases with media coverage
- 139 active cases with zero press coverage

## Files

| File | Purpose |
|---|---|
| `sue_the_map.html` | The complete app (single file, 451 KB) |
| `process_data.py` | Parses Excel datasets → `dail_data.json` |
| `generate_html.py` | Assembles the HTML from CSS/JS + embedded JSON |
| `dail_data.json` | Processed structured dataset |
| `us-states.json` | US states GeoJSON (embedded in HTML) |

## Regenerating the HTML

```bash
python process_data.py      # re-parse Excel → dail_data.json
python generate_html.py     # rebuild sue_the_map.html
```

## Tech Stack

- [Globe.gl](https://globe.gl) — 3D WebGL globe
- [D3.js](https://d3js.org) — charts
- [Claude API](https://anthropic.com) — AI legal briefings
- Web Speech API — voice input
- Vanilla JS, no framework

## Team

Built at **GeorgeHacksxAI 2026** hackathon.

## License

MIT — see [LICENSE](LICENSE)
