import pandas as pd
from difflib import SequenceMatcher
from math import radians, sin, cos, sqrt, atan2

# --------------------------------------------------
# Read datasets
# --------------------------------------------------

pyro = pd.read_csv('../data/pyrocb_conus.csv')
mtbs = pd.read_csv('../output/filtered_fires.csv')

# Extract year from dates
pyro['year'] = pd.to_datetime(pyro['datetime']).dt.year
mtbs['year'] = pd.to_datetime(mtbs['ignition_date']).dt.year

# Standardize fire names for comparison
pyro['name_clean'] = (
    pyro['fire_name']
    .fillna('')
    .str.upper()
    .str.strip()
)

mtbs['name_clean'] = (
    mtbs['fire_name']
    .fillna('')
    .str.upper()
    .str.strip()
)

# --------------------------------------------------
# Calculate distance between two coordinates
# --------------------------------------------------

def distance_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)

    a = (
        sin(dlat / 2)**2
        + cos(radians(lat1))
        * cos(radians(lat2))
        * sin(dlon / 2)**2
    )

    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# --------------------------------------------------
# Match each pyroCb event to MTBS
# --------------------------------------------------

results = []

for _, p in pyro.iterrows():

    # Only compare against MTBS fires from the same year
    candidates = mtbs[mtbs['year'] == p['year']].copy()

    # First try exact fire-name match
    exact = candidates[
        candidates['name_clean'] == p['name_clean']
    ]

    if len(exact) > 0 and p['name_clean'] != '':

        # If more than one exact-name record exists,
        # select the geographically closest one.
        exact = exact.copy()

        exact['distance_km'] = exact.apply(
            lambda m: distance_km(
                p['lat'],
                p['lon'],
                m['latitude'],
                m['longitude']
            ),
            axis=1
        )

        best = exact.loc[exact['distance_km'].idxmin()]

        method = 'exact_name_year'
        similarity = 1.0
        distance = best['distance_km']

    else:

        # No exact name match: evaluate nearby fires
        candidates['distance_km'] = candidates.apply(
            lambda m: distance_km(
                p['lat'],
                p['lon'],
                m['latitude'],
                m['longitude']
            ),
            axis=1
        )

        # Only consider fires within 100 km
        candidates = candidates[
            candidates['distance_km'] <= 100
        ].copy()

        if len(candidates) == 0:

            results.append({
                'pyrocb_datetime': p['datetime'],
                'pyrocb_fire': p['fire_name'],
                'year': p['year'],
                'mtbs_fire': '',
                'distance_km': '',
                'name_similarity': '',
                'match_method': 'unmatched'
            })

            continue

        candidates['name_similarity'] = candidates[
            'fire_name'
        ].apply(
            lambda name: SequenceMatcher(
                None,
                p['name_clean'],
                str(name).upper().strip()
            ).ratio()
        )

        # Prefer similar names and nearby fires
        candidates['score'] = (
            candidates['name_similarity']
            - candidates['distance_km'] / 500
        )

        best = candidates.sort_values(
            'score',
            ascending=False
        ).iloc[0]

        similarity = best['name_similarity']
        distance = best['distance_km']

        # Conservative automatic-match rule
        if similarity >= 0.65 and distance <= 50:
            method = 'probable_match'
        else:
            method = 'review'

    results.append({
        'pyrocb_datetime': p['datetime'],
        'pyrocb_fire': p['fire_name'],
        'year': p['year'],
        'mtbs_fire': best['fire_name'],
        'distance_km': round(distance, 1),
        'name_similarity': round(similarity, 2),
        'match_method': method
    })


# --------------------------------------------------
# Save results
# --------------------------------------------------

results = pd.DataFrame(results)

results.to_csv(
    '../output/pyrocb_mtbs_matches.csv',
    index=False
)

print()
print('Total pyroCb events:', len(results))
print()
print(results['match_method'].value_counts())
print()
print(
    'Results saved to '
    '../output/pyrocb_mtbs_matches.csv'
)

# --------------------------------------------------
# Create fire-level pyroCb dataset
# --------------------------------------------------

# Keep only accepted matches
accepted = results[
    results['match_method'].isin(
        ['exact_name_year', 'probable_match']
    )
].copy()

# For every accepted pyroCb event, locate the single
# MTBS record that is closest to the pyroCb coordinates.
fire_records = []

for _, r in accepted.iterrows():

    # Find the original pyroCb event
    p_event = pyro[
        (pyro['datetime'].astype(str) ==
         str(r['pyrocb_datetime'])) &
        (pyro['fire_name'].fillna('') ==
         str(r['pyrocb_fire']))
    ]

    if len(p_event) == 0:
        continue

    p_event = p_event.iloc[0]

    # Find MTBS records with the matched name and year
    candidates = mtbs[
        (mtbs['fire_name'] == r['mtbs_fire']) &
        (mtbs['year'] == r['year'])
    ].copy()

    if len(candidates) == 0:
        continue

    # Calculate distance to each possible MTBS record
    candidates['match_distance_km'] = candidates.apply(
        lambda m: distance_km(
            p_event['lat'],
            p_event['lon'],
            m['latitude'],
            m['longitude']
        ),
        axis=1
    )

    # Keep only the closest MTBS record
    best = candidates.loc[
        candidates['match_distance_km'].idxmin()
    ]

    fire_records.append({
        'mtbs_fire': best['fire_name'],
        'year': best['year'],
        'acres': best['acres'],
        'latitude': best['latitude'],
        'longitude': best['longitude'],
        'ignition_date': best['ignition_date'],
        'pyrocb_datetime': r['pyrocb_datetime'],
        'max_inject_alt': p_event['max_inject_alt']
    })


fire_records = pd.DataFrame(fire_records)

# Collapse multiple pyroCb events associated with
# the same physical MTBS fire into one record.
fire_level = fire_records.groupby(
    [
        'mtbs_fire',
        'year',
        'acres',
        'latitude',
        'longitude',
        'ignition_date'
    ],
    as_index=False
).agg(
    pyrocb_events=('pyrocb_datetime', 'count'),
    max_inject_alt=('max_inject_alt', 'max')
)

fire_level['pyrocb'] = 1

fire_level.to_csv(
    '../output/pyrocb_fires.csv',
    index=False
)

print()
print('Unique matched pyroCb fires:', len(fire_level))
print(
    'Fire-level dataset saved to '
    '../output/pyrocb_fires.csv'
)
