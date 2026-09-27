import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# --------------------------------------------------
# Read datasets
# --------------------------------------------------

mtbs = pd.read_csv('../output/filtered_fires.csv')
pyro = pd.read_csv('../output/pyrocb_fires.csv')

# Limit MTBS data to the period covered by
# the pyroCb inventory
mtbs['year'] = pd.to_datetime(
    mtbs['ignition_date']
).dt.year

mtbs = mtbs[
    (mtbs['year'] >= 2013) &
    (mtbs['year'] <= 2023)
].copy()

# --------------------------------------------------
# Identify pyroCb-producing MTBS fires
# --------------------------------------------------

pyro_keys = set(
    zip(
        pyro['mtbs_fire'],
        pyro['year'],
        pyro['latitude'],
        pyro['longitude']
    )
)

mtbs['is_pyrocb'] = [
    (name, year, lat, lon) in pyro_keys
    for name, year, lat, lon in zip(
        mtbs['fire_name'],
        mtbs['year'],
        mtbs['latitude'],
        mtbs['longitude']
    )
]

non_pyro = mtbs[~mtbs['is_pyrocb']]

# --------------------------------------------------
# Create acreage comparison boxplot
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 6))

ax.boxplot(
    [
        non_pyro['acres'],
        pyro['acres']
    ],
    labels=[
        f'Non-pyroCb\n(n={len(non_pyro)})',
        f'PyroCb\n(n={len(pyro)})'
    ],
    showfliers=False
)

# Wildfire acreage is highly skewed, so use
# a logarithmic y-axis.
ax.set_yscale('log')

ax.yaxis.set_major_formatter(
    FuncFormatter(
        lambda x, pos: f'{x:,.0f}'
    )
)

ax.set_ylabel('Fire Size (acres)')
ax.set_title(
    'Wildfire Size: PyroCb vs. Non-pyroCb Fires\n'
    'CONUS MTBS, 2013-2023'
)

ax.grid(
    True,
    axis='y',
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    '../output/pyrocb_acreage_comparison.png',
    dpi=300
)

print('Plot saved to:')
print('../output/pyrocb_acreage_comparison.png')

print()
print('Median acreage:')
print(
    'Non-pyroCb:',
    round(non_pyro['acres'].median())
)
print(
    'PyroCb:',
    round(pyro['acres'].median())
)
