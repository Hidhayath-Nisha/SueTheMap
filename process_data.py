import pandas as pd
import json
import re
from collections import defaultdict

cases_df = pd.read_excel('Case_Table_2026-Feb-21_1952.xlsx')
media_df = pd.read_excel('Secondary_Source_Coverage_Table_2026-Feb-21_2058.xlsx')

def clean(val):
    if pd.isna(val): return ''
    return str(val).strip()

# Build media count per case (Record_Number)
media_counts = media_df.groupby('Case_Number').size().to_dict()
media_sources = {}
for _, row in media_df.iterrows():
    cn = row['Case_Number']
    if cn not in media_sources:
        media_sources[cn] = []
    media_sources[cn].append({
        'title': clean(row['Secondary_Source_Title']),
        'link': clean(row['Secondary_Source_Link'])
    })

state_map = {
    'California': 'CA', 'New York': 'NY', 'Illinois': 'IL', 'Texas': 'TX',
    'Florida': 'FL', 'Washington': 'WA', 'Massachusetts': 'MA', 'Michigan': 'MI',
    'Georgia': 'GA', 'Colorado': 'CO', 'Virginia': 'VA', 'Pennsylvania': 'PA',
    'Ohio': 'OH', 'New Jersey': 'NJ', 'Tennessee': 'TN', 'Missouri': 'MO',
    'Minnesota': 'MN', 'Arizona': 'AZ', 'Maryland': 'MD', 'North Carolina': 'NC',
    'Indiana': 'IN', 'Connecticut': 'CT', 'Wisconsin': 'WI', 'Nevada': 'NV',
    'Oregon': 'OR', 'Louisiana': 'LA', 'Alabama': 'AL', 'Iowa': 'IA',
    'Utah': 'UT', 'Kansas': 'KS', 'Arkansas': 'AR', 'Oklahoma': 'OK',
    'Nebraska': 'NE', 'Delaware': 'DE', 'Rhode Island': 'RI', 'Idaho': 'ID',
    'South Carolina': 'SC', 'Kentucky': 'KY', 'New Hampshire': 'NH',
    'New Mexico': 'NM', 'Montana': 'MT', 'Wyoming': 'WY', 'Vermont': 'VT',
    'West Virginia': 'WV', 'Maine': 'ME', 'Alaska': 'AK', 'Hawaii': 'HI',
    'North Dakota': 'ND', 'South Dakota': 'SD', 'Mississippi': 'MS',
    'District of Columbia': 'DC',
}

def get_state_abbr(jurisdiction_name):
    s = clean(jurisdiction_name)
    s2 = re.sub(r'\s*\(federal\)', '', s, flags=re.I).strip()
    s2 = re.sub(r'\s*\(state\)', '', s2, flags=re.I).strip()
    for name, abbr in state_map.items():
        if name.lower() == s2.lower() or name.lower() in s2.lower():
            return abbr, name
    return None, None

def parse_sector(area_text):
    if pd.isna(area_text): return 'Other'
    text = str(area_text)
    items = [x.strip().strip("'").strip('"') for x in text.split(',') if x.strip()]
    if items:
        first = items[0].strip("'").strip('"').strip()
        return first if first else 'Other'
    return 'Other'

def parse_year(date_val):
    if pd.isna(date_val): return None
    try:
        return int(pd.to_datetime(date_val).year)
    except:
        s = str(date_val)
        m = re.search(r'(\d{4})', s)
        return int(m.group(1)) if m else None

states_data = {}
year_trends = defaultdict(lambda: {'total': 0, 'sectors': defaultdict(int)})
sector_totals = defaultdict(int)
total_cases = 0
total_with_media = 0
total_uncovered_active = 0
skipped = 0

for _, row in cases_df.iterrows():
    abbr, state_name = get_state_abbr(row['Jurisdiction_Name'])
    if not abbr:
        skipped += 1
        continue

    record_num = row['Record_Number']
    status = clean(row['Status_Disposition'])
    is_active = 'active' in status.lower()
    year = parse_year(row['Date_Action_Filed'])
    sector = parse_sector(row['Area_of_Application_List'])
    media_count = int(media_counts.get(record_num, 0))
    sources = media_sources.get(record_num, [])
    class_action_raw = clean(row['Class_Action_list'])
    is_class = "'yes'" in class_action_raw.lower() or class_action_raw.lower() == 'yes'

    case_obj = {
        'id': int(record_num) if pd.notna(record_num) else 0,
        'caption': clean(row['Caption']),
        'description': clean(row['Brief_Description'])[:400],
        'status': status if status else 'Unknown',
        'year': year,
        'sector': sector,
        'issues': clean(row['Issue_Text'])[:200],
        'class_action': is_class,
        'significance': clean(row['Summary_of_Significance'])[:300],
        'media_count': media_count,
        'sources': sources[:5],
        'orgs': clean(row['Organizations_involved'])[:150],
        'state': abbr
    }

    if abbr not in states_data:
        states_data[abbr] = {
            'name': state_name,
            'total': 0,
            'active': 0,
            'total_media': 0,
            'uncovered_active': 0,
            'sectors': defaultdict(int),
            'years': defaultdict(int),
            'cases': []
        }

    s = states_data[abbr]
    s['total'] += 1
    if is_active:
        s['active'] += 1
        if media_count == 0:
            s['uncovered_active'] += 1
            total_uncovered_active += 1
    if media_count > 0:
        s['total_media'] += 1
        total_with_media += 1
    s['sectors'][sector] += 1
    if year:
        s['years'][str(year)] += 1
    s['cases'].append(case_obj)
    total_cases += 1

    if year:
        yr = str(year)
        year_trends[yr]['total'] += 1
        year_trends[yr]['sectors'][sector] += 1

    sector_totals[sector] += 1

# Convert defaultdicts
for abbr in states_data:
    s = states_data[abbr]
    s['sectors'] = dict(sorted(s['sectors'].items(), key=lambda x: -x[1]))
    s['years'] = dict(sorted(s['years'].items()))

final_year_trends = {}
for yr, v in sorted(year_trends.items()):
    final_year_trends[yr] = {'total': v['total'], 'sectors': dict(sorted(v['sectors'].items(), key=lambda x: -x[1]))}

print(f"Total cases processed: {total_cases}")
print(f"Skipped (no state match): {skipped}")
print(f"Total with media: {total_with_media}")
print(f"Total uncovered active: {total_uncovered_active}")
print(f"States count: {len(states_data)}")
print("Top states:", sorted([(k, v['total']) for k, v in states_data.items()], key=lambda x: -x[1])[:12])
print("Top sectors:", sorted(sector_totals.items(), key=lambda x: -x[1])[:12])
print("Years:", sorted(final_year_trends.keys()))

output = {
    'states': {k: {**{kk: vv for kk, vv in v.items() if kk != 'cases'}, 'cases': v['cases']} for k, v in states_data.items()},
    'year_trends': final_year_trends,
    'sector_totals': dict(sorted(sector_totals.items(), key=lambda x: -x[1])),
    'total_cases': total_cases,
    'total_with_media': total_with_media,
    'total_uncovered_active': total_uncovered_active
}

raw = json.dumps(output, default=str)
print(f"JSON size: {len(raw) // 1024} KB")

with open('dail_data.json', 'w') as f:
    json.dump(output, f, separators=(',', ':'), default=str)
print("Saved dail_data.json")
