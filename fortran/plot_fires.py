import csv
import matplotlib.pyplot as plt

years = []
acres = []

with open('../output/annual_fire_totals.csv', 'r') as f:
    reader = csv.DictReader(f)

    for row in reader:
        years.append(int(row['year']))
        acres.append(float(row['total_acres']))

plt.figure(figsize=(10,6))

plt.plot(years, acres, marker='o', markersize=3)

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
