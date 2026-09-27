import csv

input_file = '../data/climdiv-pdsidv-v1.0.0-20260904.txt'
output_file = '../output/pdsi_monthly.csv'

months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
]

rows = []

with open(input_file, 'r') as f:
    for line in f:
        parts = line.split()

        identifier = parts[0]
        year = int(identifier[-4:])

# keep only years matching the wildfire dataset

        if 1985 <= year <= 2025:
            monthly_values = parts[1:]

            for month, value in zip(months, monthly_values):
                state_code = identifier[:2]
                division_code = identifier[2:4]
                element_code = identifier[4:6]

                rows.append([
                    state_code,
                    division_code,
                    element_code,
                    year,
                    month,
                    float(value)
                ])

with open(output_file, 'w', newline='') as f:
    writer = csv.writer(f)

    writer.writerow([
    'state_code',
    'division_code',
    'element_code',
    'year',
    'month',
    'pdsi'
])
    writer.writerows(rows)

print(f'Cleaned PDSI data saved to {output_file}')
print(f'Total rows: {len(rows):,}')
