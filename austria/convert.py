import pandas as pd

# Custom mapping of German month names to English month names
german_month_mapping = {
    'Jänner': 'January',
    'Februar': 'February',
    'März': 'March',
    'April': 'April',
    'Mai': 'May',
    'Juni': 'June',
    'Juli': 'July',
    'August': 'August',
    'September': 'September',
    'Oktober': 'October',
    'November': 'November',
    'Dezember': 'December'
}

# Read the CSV file into a DataFrame
#df = pd.read_csv('derstandard.csv')

# Convert German month names to English month names
#df['Date'] = df['Date'].replace(german_month_mapping, regex=True)

# Read the CSV file into a DataFrame
df = pd.read_csv('krone.csv')

# Convert the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%d.%m.%Y %H:%M', errors='coerce')

# Extract date part only
df['Date'] = df['Date'].dt.date

# Save the DataFrame back to a new CSV file
df.to_csv('krone_2.csv', index=False)
