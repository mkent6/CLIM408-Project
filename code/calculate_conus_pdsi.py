import pandas as pd

pdsi_file = '../output/pdsi_monthly.csv'
areas_file = '../output/climate_division_areas.csv'
output_file = '../output/conus_pdsi_monthly.csv'

# load cleaned PDSI data and climate-division area weights
pdsi = pd.read_csv(
    pdsi_file,
    dtype={
        'state_code': str,
        'division_code': str,
        'element_code': str
    }
)

areas = pd.read_csv(
    areas_file,
    dtype={
        'STATE_CODE': str,
        'CD_2DIG': str
    }
)

# make NOAA state codes two digits to match the PDSI file
areas['STATE_CODE'] = areas['STATE_CODE'].str.zfill(2)

print(f'PDSI rows: {len(pdsi):,}')
print(f'Climate divisions: {len(areas):,}')

# match each PDSI observation with its climate-division area weight
merged = pdsi.merge(
    areas,
    left_on=['state_code', 'division_code'],
    right_on=['STATE_CODE', 'CD_2DIG'],
    how='left'
)

# check that every PDSI row received an area weight
missing_weights = merged['area_weight'].isna().sum()

print(f'Merged rows: {len(merged):,}')
print(f'Rows missing area weights: {missing_weights:,}')

# Show unique climate divisions that failed to match
unmatched = merged.loc[
    merged['area_weight'].isna(),
    ['state_code', 'division_code']
].drop_duplicates()

print(f'Unmatched climate divisions: {len(unmatched)}')
print(unmatched.to_string(index=False))

# Calculate weighted PDSI contribution for each climate division
merged['weighted_pdsi'] = merged['pdsi'] * merged['area_weight']

# Sum the weighted values for each year and month
conus_pdsi = (
    merged.groupby(['year', 'month'], as_index=False)['weighted_pdsi']
    .sum()
    .rename(columns={'weighted_pdsi': 'conus_pdsi'})
)

# Put months in calendar order
month_order = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

conus_pdsi['month'] = pd.Categorical(
    conus_pdsi['month'],
    categories=month_order,
    ordered=True
)

conus_pdsi = conus_pdsi.sort_values(['year', 'month'])

print(conus_pdsi.head(12).to_string(index=False))

# save monthly area-weighted CONUS PDSI
conus_pdsi.to_csv(output_file, index=False)

print(f'CONUS monthly PDSI saved to {output_file}')
print(f'Total monthly observations: {len(conus_pdsi):,}')

# Calculate annual mean CONUS PDSI
annual_pdsi = (
    conus_pdsi.groupby('year', as_index=False)['conus_pdsi']
    .mean()
    .rename(columns={'conus_pdsi': 'annual_pdsi'})
)

annual_output_file = '../output/conus_pdsi_annual.csv'
annual_pdsi.to_csv(annual_output_file, index=False)

print(f'Annual CONUS PDSI saved to {annual_output_file}')
print(f'Total annual observations: {len(annual_pdsi)}')
print(annual_pdsi.head().to_string(index=False))
