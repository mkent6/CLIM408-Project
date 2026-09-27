import geopandas as gpd

input_file = '../data/climate_divisions/GIS.OFFICIAL_CLIM_DIVISIONS.shp'
output_file = '../output/climate_division_areas.csv'

# read NOAA climate division boundaries
gdf = gpd.read_file(input_file)

print(f'Climate divisions loaded: {len(gdf)}')
print(f'Original CRS: {gdf.crs}')

# project to an equal-area CRS for accurate area calculations
gdf_equal_area = gdf.to_crs('EPSG:5070')

# calculate area in square kilometers
gdf_equal_area['area_km2'] = gdf_equal_area.geometry.area / 1_000_000

print(f'Total CONUS area: {gdf_equal_area["area_km2"].sum():,.0f} km?')

# calculate each climate division's fraction of total CONUS area
total_area = gdf_equal_area['area_km2'].sum()
gdf_equal_area['area_weight'] = gdf_equal_area['area_km2'] / total_area

# keep the fields needed to match with the PDSI data
areas = gdf_equal_area[
    ['STATE_CODE', 'STATE_FIPS', 'CD_2DIG', 'STATE', 'NAME',
     'area_km2', 'area_weight']
].copy()

areas.to_csv(output_file, index=False)

print(f'Area weights saved to {output_file}')
print(f'Sum of weights: {areas["area_weight"].sum():.6f}')
