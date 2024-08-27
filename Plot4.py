import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter

# Load CSV data into Pandas DataFrames
Gross_Capital_Formation = pd.read_csv('Gross_Capital_Formation(CurrentUS).csv')
CO2_emission = pd.read_csv('owid-co2-data.csv')
Exports = pd.read_csv('Exports(CurrentUS).csv')
GDP = pd.read_csv('GDP(US)diff_for.csv')

# Reshape and rename columns in the Gross Capital Formation and Exports DataFrames
melted_df = Gross_Capital_Formation.melt(id_vars=['Country Name'], var_name='Year', value_name='Gross capital formation (current US$)')
melted_df = melted_df.rename(columns={'Country Name': 'Entity'})
Exports2 = Exports.melt(id_vars=['Country Name'], var_name='Year', value_name='Exports(current US$)')
Exports2 = Exports2.rename(columns={'Country Name': 'Entity'})
Exports2['Year'] = Exports2['Year'].astype(int)

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

# Calculate world exports and top 10 countries' exports for each year
world_exp = Exports2[Exports2['Entity'] == 'World'].groupby('Year')['Exports(current US$)'].sum()
top_10_exp = Exports2[Exports2['Entity'].isin(top_10_countries)].groupby('Year')['Exports(current US$)'].sum()

# Calculate rest of the world's exports
rest_of_world_exp = world_exp - top_10_exp
print(rest_of_world_exp)

# Include 'Rest-World' for visualization purposes
top_10_countries.append('Rest-World')

# Create subplots for the animation
fig, ax = plt.subplots(figsize=(10, 6))
lines = [ax.plot([], [], label=country)[0] for country in top_10_countries]
ax.legend()

# Initialize the plot
def init():
    ax.set_xlim(Exports2['Year'].min(), Exports2['Year'].max())
    ax.set_ylim(Exports2['Exports(current US$)'].min(), Exports2['Exports(current US$)'].max() / 2.5)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Exports (current US$)', fontsize=12)
    return lines

# Update the plot for each frame
def animate(i):
    data = Exports2[Exports2['Year'] <= Exports2['Year'].min() + i]
    for j, line in enumerate(lines):
        country_data = data[data['Entity'] == top_10_countries[j]]
        if not country_data.empty:
            line.set_data(country_data['Year'], country_data['Exports(current US$)'])
    return lines

# Create and save the animation
ani = FuncAnimation(fig, animate, frames=Exports2['Year'].nunique(), init_func=init, interval=100, blit=True)
ani.save("World-Export-by-year.gif", dpi=100, writer=PillowWriter(fps=25))
plt.show()

