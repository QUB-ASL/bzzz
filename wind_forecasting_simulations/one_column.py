import csv

# Read the original CSV and remove the first column
filename = 'raspberry/data/wind_data/25-09-23--17-23/25-09-23--17-23_N_10_error_ph_40_baseline.csv'
with open(filename, 'r', newline='') as infile, open(filename.replace('.csv', '_one_column.csv'), 'w', newline='') as outfile:
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    for row in reader:
        # Skip the first column
        writer.writerow(row[1:])
