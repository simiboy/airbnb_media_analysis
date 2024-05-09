import pandas as pd

# Function to split multiline strings at newline characters
def split_multiline(date_string):
    lines = date_string.split('\n')
    if len(lines) > 1:
        return lines[0]
    else:
        return date_string

# Apply the function to the "Date" column, skipping empty or 'Date not found' lines
#df['Date'] = df['Date'].apply(lambda x: split_multiline(x) if x and x != 'Date not found' else x)

# Custom mapping of Hungarian month names to English month names
hungarian_month_mapping = {
    'január': 'January',
    'február': 'February',
    'március': 'March',
    'április': 'April',
    'május': 'May',
    'június': 'June',
    'július': 'July',
    'augusztus': 'August',
    'szeptember': 'September',
    'október': 'October',
    'november': 'November',
    'december': 'December'
}

# Read the CSV file into a DataFrame
df = pd.read_csv('hvg.csv')

# Convert Hungarian month names to English month names
df['Date'] = df['Date'].replace(hungarian_month_mapping, regex=True)

# Convert the Date column to datetime format
df['Date'] = pd.to_datetime(df['Date'], format='%Y. %B. %d. %H:%M', errors='coerce')

# Extract date part only
df['Date'] = df['Date'].dt.date

# Save the DataFrame back to a new CSV file
df.to_csv('hvg_2.csv', index=False)