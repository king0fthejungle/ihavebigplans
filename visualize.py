import streamlit as st
import pandas as pd
import altair as alt

# Load the data
@st.cache_data
def load_data():
    # Read the CSV file
    data = pd.read_csv('ihavebigplans.csv')  # Replace with the path to your CSV file
    return data

# Load the data
data = load_data()

# Streamlit App Layout
st.title('Fantasy Football Roster Metrics')

# Display the raw data
st.write("### Roster Overview")
st.dataframe(data)

# Add interactivity: Display a summary of the data
if st.checkbox('Show Data Summary'):
    st.write("### Data Summary")
    st.write(data.describe(include='all'))

st.write("### Roster Spots for All Players")

# Select only 'Roster Spot #' columns
roster_spots = [col for col in data.columns if col.startswith('Roster Spot') and col.endswith('_y')]
roster_data = data[['Username'] + roster_spots]  # Include 'User ID' for context

st.dataframe(roster_data)

# Add a plot for `setting_fpts_y` vs `setting_fpts_against_y` using Altair
if 'setting_fpts_y' in data.columns and 'setting_fpts_against_y' in data.columns:
    st.write("### Fantasy Points Visualization")
    
    # Prepare the data for plotting
    plot_data = data[['Username', 'setting_fpts_y', 'setting_fpts_against_y']].dropna()

    # Define a zoom area by setting axis limits
    x_min, x_max = plot_data['setting_fpts_y'].min(), plot_data['setting_fpts_y'].max()
    y_min, y_max = plot_data['setting_fpts_against_y'].min(), plot_data['setting_fpts_against_y'].max()
    
    zoom_x_min = x_min - 50
    zoom_x_max = x_max + 50
    zoom_y_min = y_min - 50
    zoom_y_max = y_max + 50

    # Create the scatter plot using Altair
    chart = alt.Chart(plot_data).mark_point().encode(
        x=alt.X('setting_fpts_y', scale=alt.Scale(domain=[zoom_x_min, zoom_x_max]), title='Fantasy Points For'),
        y=alt.Y('setting_fpts_against_y', scale=alt.Scale(domain=[zoom_y_min, zoom_y_max]), title='Fantasy Points Against'),
        tooltip=['Username','setting_fpts_y', 'setting_fpts_against_y']
    ).properties(
        title='Fantasy Points For vs. Fantasy Points Against'
    ).interactive()
    
    st.altair_chart(chart, use_container_width=True)
else:
    st.write("Required columns for plotting are missing.")

