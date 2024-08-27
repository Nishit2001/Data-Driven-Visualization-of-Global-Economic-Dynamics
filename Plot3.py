import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Load CSV data into Pandas DataFrames
Gross_Capital_Formation = pd.read_csv('Gross_Capital_Formation(CurrentUS).csv')
CO2_emission = pd.read_csv('owid-co2-data.csv')
Exports = pd.read_csv('exports-of-goods-and-services-constant-2015-us.csv')
GDP = pd.read_csv('GDP(US)diff_for.csv')

# Reshape and rename columns in the Gross Capital Formation DataFrame
melted_df = Gross_Capital_Formation.melt(id_vars=['Country Name'], var_name='Year', value_name='Gross capital formation (current US$)')
melted_df = melted_df.rename(columns={'Country Name': 'Entity'})
melted_df['Year'] = melted_df['Year'].astype(int)

# Merge the DataFrames by country and year
merged_df = pd.merge(Exports, CO2_emission, on=['Entity', 'Year'])
merged_df = pd.merge(merged_df, melted_df, on=['Entity', 'Year'])
merged_df = pd.merge(merged_df, GDP, on=['Entity', 'Year'])

# List of income categories to filter out
country_group = [
    'High-income countries', 'Middle-income countries', 'East Asia and Pacific (WB)', 'Upper-middle-income countries',
    'Europe and Central Asia (WB)', 'North America (WB)', 'European Union (27)', 'Lower-middle-income countries',
    'Latin America and Caribbean (WB)', 'South Asia (WB)', 'Middle East and North Africa (WB)', 'Sub-Saharan Africa (WB)'
]

# Filter the DataFrame to remove high-income and middle-income countries
filtered_df = GDP[~GDP['Entity'].isin(country_group)]

# Get top 10 GDP countries for the year 2021
top_10_gdp_2021 = filtered_df[filtered_df['Year'] == 2021].nlargest(10, 'GDP (constant 2015 US$)')
top_10_countries = [country for country in top_10_gdp_2021['Entity'].unique() if country not in ['World', 'Rest-World']]

# Calculate world Gross Capital Formation (GCF) and top 10 countries' GCF for each year
world_gcf = melted_df[melted_df['Entity'] == 'World'].groupby('Year')['Gross capital formation (current US$)'].sum()
top_10_gcf = melted_df[melted_df['Entity'].isin(top_10_countries)].groupby('Year')['Gross capital formation (current US$)'].sum()

# Calculate rest of the world's Gross Capital Formation (GCF)
rest_of_world_gcf = world_gcf - top_10_gcf
print(rest_of_world_gcf)

# Include 'Rest-World' for visualization purposes
top_10_countries.append('Rest-World')

# Create subplots for the animation
fig, ax = plt.subplots(figsize=(10, 6))
lines = [ax.plot([], [], label=country)[0] for country in top_10_countries]
ax.legend()

# Initialize the plot
def init():
    ax.set_xlim(melted_df['Year'].min(), melted_df['Year'].max())
    ax.set_ylim(melted_df['Gross capital formation (current US$)'].min(), melted_df['Gross capital formation (current US$)'].max() / 2.5)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Gross Capital Formation (current US$)', fontsize=12)
    return lines

# Update the plot for each frame
def animate(i):
    data = melted_df[melted_df['Year'] <= melted_df['Year'].min() + i]
    for j, line in enumerate(lines):
        country_data = data[data['Entity'] == top_10_countries[j]]
        if not country_data.empty:
            line.set_data(country_data['Year'], country_data['Gross capital formation (current US$)'])
    return lines

# Create and save the animation
ani = FuncAnimation(fig, animate, frames=melted_df['Year'].nunique(), init_func=init, interval=100, blit=True)
ani.save("Gross-Capital-Formation.gif", dpi=250, writer=PillowWriter(fps=25))
plt.show()

