import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Load CSV data into Pandas DataFrames
Gross_Capital_Formation = pd.read_csv('GDP_Deflator.csv')
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
top_10_countries = top_10_gdp_2021['Entity'].unique()
top_10_countries = [country for country in top_10_countries if country != 'World']

# Calculate world GDP and top 10 countries' GDP for each year
world_gdp = GDP[GDP['Entity'] == 'World'].groupby('Year')['GDP (constant 2015 US$)'].sum()
top_10_gdp = GDP[GDP['Entity'].isin(top_10_countries)].groupby('Year')['GDP (constant 2015 US$)'].sum()

# Calculate rest of the world's GDP
rest_of_world_gdp = world_gdp - top_10_gdp
print(rest_of_world_gdp)

# Remove world data from GDP DataFrame
GDP = GDP[GDP['Entity'] != 'World']

# Create subplots for the animation
fig, ax = plt.subplots(figsize=(10, 6))
lines = [ax.plot([], [], label=country)[0] for country in top_10_countries]
ax.legend()

# Initialize the plot
def init():
    ax.set_xlim(filtered_df['Year'].min(), filtered_df['Year'].max())
    ax.set_ylim(filtered_df['GDP (constant 2015 US$)'].min(), filtered_df['GDP (constant 2015 US$)'].max() / 2.5)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('GDP (constant 2015 US$)', fontsize=12)
    return lines

# Update the plot for each frame
def animate(i):
    data = filtered_df[filtered_df['Year'] <= filtered_df['Year'].min() + i]
    for j, line in enumerate(lines):
        country_data = data[data['Entity'] == top_10_countries[j]]
        if not country_data.empty:
            line.set_data(country_data['Year'], country_data['GDP (constant 2015 US$)'])
    return lines

# Create and save the animation
ani = FuncAnimation(fig, animate, frames=filtered_df['Year'].nunique(), init_func=init, interval=100, blit=True)
ani.save("GDP-by-year.gif", dpi=250, writer=PillowWriter(fps=25))
plt.show()

