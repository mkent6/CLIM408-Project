import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

fire_file = '../output/annual_fire_totals.csv'
pdsi_file = '../output/conus_pdsi_annual.csv'

# Load annual wildfire acreage and annual PDSI
fires = pd.read_csv(fire_file)
pdsi = pd.read_csv(pdsi_file)

print("Fire data:")
print(fires.head())

print("\nPDSI data:")
print(pdsi.head())

# Merge wildfire and drought data by year
combined = fires.merge(pdsi, on='year', how='inner')

print(f"\nMatched years: {len(combined)}")
print(combined.head().to_string(index=False))

from scipy.stats import pearsonr, spearmanr

# Calculate correlations between drought and annual burned acreage
pearson_r, pearson_p = pearsonr(
    combined['annual_pdsi'],
    combined['total_acres']
)

spearman_r, spearman_p = spearmanr(
    combined['annual_pdsi'],
    combined['total_acres']
)

print(f"\nPearson correlation: r = {pearson_r:.3f}, p = {pearson_p:.4f}")
print(f"Spearman correlation: rho = {spearman_r:.3f}, p = {spearman_p:.4f}")

# Calculate correlations between drought and number of fires
pearson_fires_r, pearson_fires_p = pearsonr(
    combined['annual_pdsi'],
    combined['number_of_fires']
)

spearman_fires_r, spearman_fires_p = spearmanr(
    combined['annual_pdsi'],
    combined['number_of_fires']
)

print(f"\nPDSI vs number of fires:")
print(f"Pearson correlation: r = {pearson_fires_r:.3f}, p = {pearson_fires_p:.4f}")
print(f"Spearman correlation: rho = {spearman_fires_r:.3f}, p = {spearman_fires_p:.4f}")

# Scatterplot: annual PDSI vs annual burned acreage
x = combined['annual_pdsi']
y = combined['total_acres'] / 1_000_000

plt.figure(figsize=(8, 6))

plt.scatter(x, y, alpha=0.8)

# Linear best-fit line
slope, intercept = np.polyfit(x, y, 1)
trend_x = np.linspace(x.min(), x.max(), 100)
trend_y = slope * trend_x + intercept

plt.plot(trend_x, trend_y, linestyle='--')

# Mark the PDSI zero line
plt.axvline(0, linestyle=':', linewidth=1, alpha=0.6)

# Add correlation statistics
plt.text(
    0.97, 0.95,
    f'Pearson r = {pearson_r:.2f}\np = {pearson_p:.3f}',
    transform=plt.gca().transAxes,
    ha='right',
    va='top',
    fontsize=10
)

plt.xlabel('Annual CONUS PDSI')
plt.ylabel('Annual Acres Burned (millions)')
plt.title('Drought and Annual Wildfire Acreage, 1985-2025')

plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig('../output/pdsi_vs_burned_acres.png', dpi=300)

print('\nScatterplot saved to ../output/pdsi_vs_burned_acres.png')
