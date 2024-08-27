import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

# Load CSV data into Pandas DataFrames
df_gdp = pd.read_csv('GDP(US)diff_for.csv')
df_gdp_per_capita = pd.read_csv('GDP(Percapita)Diff_for.csv')
df_gdp_deflator = pd.read_csv('GDP_Deflator.csv')

# Reshape and rename columns in the GDP deflator DataFrame
melted_df = df_gdp_deflator.melt(id_vars=['Country Name'], var_name='Year', value_name='GDP deflator')
melted_df = melted_df.rename(columns={'Country Name': 'Entity'})
melted_df['Year'] = melted_df['Year'].astype(int)

# Merge the DataFrames by country and year
merged_df = pd.merge(df_gdp, df_gdp_per_capita, on=['Entity', 'Year'])
merged_df = pd.merge(merged_df, melted_df, on=['Entity', 'Year'])

# Convert GDP values to billions and apply logarithmic scale
merged_df.dropna(subset=['GDP (constant 2015 US$)_x'], inplace=True)
merged_df['GDP (constant 2015 US$)_x'] = np.log(merged_df['GDP (constant 2015 US$)_x'] / 1e9)  # GDP in billions
merged_df['GDP (constant 2015 US$)_y'] = merged_df['GDP (constant 2015 US$)_y'] / 1000  # GDP per capita in thousands

# Read continent data and merge with existing DataFrame
merged_df = pd.read_csv('continent.csv') 
merged_df.dropna(subset=['Continent'], inplace=True)

# Initialize colors for continents
colors = {'Asia': 'red', 'Europe': 'blue', 'Africa': 'green', 'America': 'orange', 'Oceania': 'purple'}

# Create a scatter plot for each continent
fig, ax = plt.subplots()
scatters = {}

for continent, color in colors.items():
    scatters[continent] = ax.scatter([], [], s=[], alpha=0.5, color=color, label=continent)

# Set plot limits, labels, and legends
ax.set_xlim(0, merged_df['GDP (constant 2015 US$)_y'].max() / 1.5)
ax.set_ylim(0, merged_df['GDP (constant 2015 US$)_x'].max())
ax.set_xlabel('GDP per Capita (constant 2015 US$)', fontsize=12)
ax.set_ylabel('Log of GDP (constant 2015 US$)', fontsize=12)

# Legend for GDP deflator size
size_legend = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='gray', markersize=10, label='Circle size ~ GDP deflator')
ax.add_artist(ax.legend(handles=[size_legend], loc='upper left', title='GDP Deflator'))

# Set legend for continents
handles, labels = [], []
for scatter in scatters.values():
    handle = plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=scatter.get_facecolor()[0], markersize=10)
    handles.append(handle)
    labels.append(scatter.get_label())
ax.legend(handles=handles, labels=labels, loc='upper right')

# Function to update scatter plots for each continent
def update(year):
    year_data = merged_df[merged_df['Year'] == year]
    for continent, scatter in scatters.items():
        continent_data = year_data[year_data['Continent'] == continent]
        scatter.set_offsets(continent_data[['GDP (constant 2015 US$)_y', 'GDP (constant 2015 US$)_x']])
        scatter.set_sizes(continent_data['GDP deflator'] * 3)  # Adjust the scaling factor as needed
    ax.set_title(f'Year: {year}')

# Define the years for the animation
years = sorted(merged_df['Year'].unique())

# Create and show the animation
ani = FuncAnimation(fig, update, frames=years, interval=100)
plt.show()

