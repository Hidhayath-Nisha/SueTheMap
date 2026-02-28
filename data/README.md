# Data Dictionary

## Source

**Database of AI Litigation (DAIL)**  
George Washington University Law School  
https://dail.gwlaw.edu

## Files

### `Case_Table_2026-Feb-21_1952.xlsx`
Raw case table from DAIL. Key columns:

| Column | Description |
|---|---|
| `Record_Number` | Unique case ID (links to secondary sources) |
| `Caption` | Case name (e.g. *Doe v. OpenAI*) |
| `Brief_Description` | Short case summary |
| `Area_of_Application_List` | Sector (Generative AI, Facial Recognition, etc.) |
| `Issue_Text` | Legal issues raised |
| `Class_Action_list` | Whether it's a class action |
| `Organizations_involved` | Parties involved |
| `Jurisdiction_Name` | US state or federal district |
| `Date_Action_Filed` | Filing date |
| `Status_Disposition` | Active / settled / dismissed |
| `Summary_of_Significance` | Analyst note on why this case matters |

### `Secondary_Source_Coverage_Table_2026-Feb-21_2058.xlsx`
Media and secondary source coverage per case.

| Column | Description |
|---|---|
| `id` | Row ID |
| `Case_Number` | Links to `Record_Number` in case table |
| `Secondary_Source_Link` | URL to article or filing |
| `Secondary_Source_Title` | Title of the coverage |

### `dail_data.json`
Processed output used by the app. Structure:

```json
{
  "states": {
    "CA": {
      "name": "California",
      "total": 103,
      "active": 68,
      "total_media": 42,
      "uncovered_active": 26,
      "sectors": { "Generative AI": 57 },
      "years": { "2020": 8 },
      "cases": [...]
    }
  },
  "year_trends": { "2023": { "total": 94, "sectors": {} } },
  "sector_totals": { "Generative AI": 77 },
  "total_cases": 293,
  "total_with_media": 154,
  "total_uncovered_active": 139
}
```

## Processing

Run `process_data.py` to regenerate `dail_data.json` from the Excel files:

```bash
python process_data.py
```

Stats: 293 cases · 34 states · 2011–2026
