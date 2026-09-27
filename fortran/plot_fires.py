import csv
import matplotlib.pyplot as plt
from scipy.stats import theilslopes

years = []
acres = []

with open('../output/annual_fire_totals.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        years.append(int(row['year']))
        acres.append(float(row['total_acres']))

plt.figure(figsize=(10,6))

# calculate theil-sen trend
slope, intercept, low_slope, high_slope = theilslopes(acres, years)
trend = [intercept + slope * year for year in years]

print(f"Thiel-Sen slope: {slope:,.0f} acres per year")

# compare average annual burned acerage between two periods
early_acres = [acre for year, acre in zip(years, acres) if 1985 <= year <= 1999]
recent_acres = [acre for year, acre in zip(years, acres) if 2000 <= year <= 2025]

early_avg = sum(early_acres) / len(early_acres)
recent_avg = sum(recent_acres) / len(recent_acres)

percent_increase = ((recent_avg - early_avg) / early_avg) * 100
print(f"1985-1999 average: {early_avg:,.0f} acres/year")
print(f"2000-2025 average: {recent_avg:,.0f} acres/year")
print(f"Percentage increase: {percent_increase:.1f}%")

plt.plot(years, acres, marker='o', markersize=3)
plt.plot(years, trend, linestyle='--', linewidth=2, label=f'Theil-Sen trend (+{slope/1e6:.3f} million acres/year)')

plt.legend()

plt.gca().yaxis.set_major_formatter(
    plt.FuncFormatter(lambda x, pos: f'{x/1e6:.0f}')
)

plt.xlabel('Year')
plt.ylabel('Total Acres Burned (millions)')
plt.title('Annual Wildfire Acreage Burned, 1985-2025')

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('../output/annual_acres_burned.png', dpi=300)

print('Plot saved to ../output/annual_acres_burned.png')
