# SueTheMap

**SueTheMap** is an interactive, self-contained AI Litigation data visualization tool. It provides a dynamic globe interface that maps out tracking data from the Database of AI Litigation (DAIL). 

## Overview

The project processes raw litigation and media coverage data (from Excel spreadsheets) to generate a deeply interactive single HTML file (`sue_the_map.html`). The visualization features:
- **Interactive 3D Globe**: Built with Globe.gl and D3.js for geographic data representation.
- **AI-Powered Queries**: Integrated with the Anthropic API to allow natural language queries about the litigation data.
- **Rich Filtering**: Filter cases by state, sector, and timeline. 
- **Detailed Insights**: View total cases, active cases, and media coverage breakdowns by state.

## Project Structure

- `process_data.py`: Reads the raw `.xlsx` data files and compiles them into a structured `dail_data.json` format used by the frontend.
- `generate_html.py`: The build script that takes the processed data, geographical shapes (`us-states.json`), CSS, and JavaScript, and bundles them into the final `sue_the_map.html` file.
- `sue_the_map.html`: The fully self-contained output visualization. No web server required—just open it in any modern browser!

## Data Sources

The project requires the following DAIL datasets to build the visualization:
1. **Case Table** (`Case_Table_*.xlsx`)
2. **Secondary Source Coverage Table** (`Secondary_Source_Coverage_Table_*.xlsx`)
3. **Geographical Data** (`us-states.json` for mapping coordinates)

## How to Build

If you update the source Excel files, you can regenerate the map by running the Python scripts in order:

1. Process the raw data:
   ```bash
   python3 process_data.py
   ```
2. Generate the new HTML file:
   ```bash
   python3 generate_html.py
   ```
3. Open `sue_the_map.html` in your web browser to view the updated visualization.
