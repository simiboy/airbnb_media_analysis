import pandas as pd

# Read the CSV file into a DataFrame
df = pd.read_csv('seznam.csv')

# Convert the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y, %H:%M', errors='coerce')

# Extract date part only
df['Date'] = df['Date'].dt.date

# Save the DataFrame back to a new CSV file
df.to_csv('seznam_2.csv', index=False)