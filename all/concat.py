import pandas as pd
import os

# List of CSV files
files = ['idnes_2.csv', 'seznam_2.csv', '24_2.csv', 'hvg_2.csv', 'index_2.csv', 'derstandard_2.csv', 'krone_2.csv']

# Initialize an empty list to hold the dataframes
dfs = []

# Read each CSV file and append its dataframe to the list
for file in files:
    df = pd.read_csv(file)
    dfs.append(df)

# Concatenate all dataframes into a single dataframe
concatenated_df = pd.concat(dfs)

print("Number of articles:", len(concatenated_df))

# Remove duplicates based on URL
concatenated_df.drop_duplicates(subset='URL', keep='first', inplace=True)

# Sort the concatenated dataframe by date in descending order
concatenated_df.sort_values(by='Date', ascending=False, inplace=True)

# Save the sorted and deduplicated concatenated dataframe to a CSV file named "articles.csv"
output_file = 'articles.csv'
concatenated_df.to_csv(output_file, index=False)

print("Concatenated, sorted, and deduplicated CSV file saved successfully as articles.csv.")

# Print the number of articles
print("Number of articles after removing duplicates:", len(concatenated_df))

# Print the number of articles per country
articles_per_country = concatenated_df['Country'].value_counts()
print("Number of articles per country:")
print(articles_per_country)
