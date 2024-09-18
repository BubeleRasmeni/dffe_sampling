import streamlit as st
import pandas as pd
import plotly.express as px
from functions import config_figure

# Set the page configuration to wide mode
st.set_page_config(layout="wide")


# Function to load and cache the dataset
@st.cache_data
def load_data(file_path, sheet_name):
    return pd.read_excel(file_path, sheet_name=sheet_name)


# Load the dataset (Assuming it's an Excel file)
data = load_data(
    "data/dffe_sampling_Stations.xlsx", sheet_name="all_stations"
)  # Your original file path

# Add a column for project abbreviations
abbreviations = {
    "Integrated Ecosystem Programme: Southern Benguela": "IEP Cruise🌊🐚🔬",
    "Long-term monitoring of nearshore temperatures around Southern Africa": "Long-term Temp 🌡️",
    "West Coast Cetacean Distribution and Abundance Survey": "Cetacean Cruise 🐋🐬🧫",
    "South Atlantic Meridional Overturning Circulation Basin-wide Array": "SAMBA Cruise🌊🐚🔬",
}

data["Project_Abbr"] = data["Project_Name"].map(abbreviations)

# Custom CSS to increase the font size of the expander titles
st.markdown(
    """
    <style>
    .streamlit-expanderHeader {
        font-size: 1.5rem !important;  /* Adjust the size as needed */
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 0.8rem;
                    padding-bottom: 2rem;
                    padding-left: 2rem;
                    padding-right: 3rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

# App title and description
st.title("Oceans and Coastal Research Directorate")
st.markdown(
    """
    <div style='text-align: justify;'>
    Welcome to the interactive dashboard of the Department of Forestry, Fisheries, and the Environment (DFFE) Oceans and Coastal Research Directorate.
    Explore various research projects conducted across South African ocean waters. 
    Some of the data collected from these projects is available on the <a href='https://data.ocean.gov.za/' target='_blank'>Marine Information Management System (MIMS)</a>.
    Select a project to view the sampling stations on the map and learn more about the research initiatives.
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar for project selection and resources
with st.sidebar:
    st.header("Instrument Type Selection")
    selected_instruments = st.multiselect(
        "Choose the instruments to filter by:",
        options=["CTD", "TSG", "ADCP", "Niskin Bottle", "Bongo", "UTR"],
        default=[],
    )

    # Get the default project options based on the selected instruments
    def get_project_options(selected_instruments):
        if not selected_instruments:
            return [
                "Integrated Ecosystem Programme: Southern Benguela",
                "Long-term monitoring of nearshore temperatures around Southern Africa",
                "West Coast Cetacean Distribution and Abundance Survey",
                "South Atlantic Meridional Overturning Circulation Basin-wide Array",
            ]
        relevant_projects = data[
            data["Instrument_Type"].apply(
                lambda x: any(inst in x for inst in selected_instruments)
            )
        ]["Project_Name"].unique()
        return relevant_projects.tolist()

    project_options = get_project_options(selected_instruments)

    st.header("Project Selection")
    selected_projects = st.multiselect(
        "Choose the projects to display on the map:",
        options=project_options,
        default=project_options if selected_instruments else project_options,
    )

    st.header("Resources")
    st.markdown(
        """
        <div style='text-align: justify;'>
        -<a href='https://data.ocean.gov.za/' target='_blank'>Marine Information Management System</a><br>
        -<a href='https://www.dffe.gov.za/OceansandCoasts' target='_blank'>DFFE Oceans and Coasts</a><br>
        -<a href='https://docs.streamlit.io/' target='_blank'>Streamlit Documentation</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


# Function to filter data based on selected projects and instruments
def filter_data_for_projects_and_instruments(selected_projects, selected_instruments):
    if not selected_projects and not selected_instruments:
        return pd.DataFrame(
            columns=data.columns
        )  # Return an empty DataFrame with the same structure

    if selected_projects:
        combined_data = pd.DataFrame()
        for project in selected_projects:
            project_data = data[data["Project_Name"] == project]
            if selected_instruments:
                # Filter by instruments within the selected project
                instrument_filter = project_data["Instrument_Type"].apply(
                    lambda x: any(inst in x for inst in selected_instruments)
                )
                project_data = project_data[instrument_filter]
            combined_data = pd.concat([combined_data, project_data])
        return combined_data
    else:
        # No project selected, filter all data by the selected instruments
        instrument_filter = data["Instrument_Type"].apply(
            lambda x: any(inst in x for inst in selected_instruments)
        )
        return data[instrument_filter]


# Function to generate map based on selected projects and instruments
# Set your Mapbox access token
mapbox_access_token = "pk.eyJ1IjoiYnViZWxlcmFzbWVuaSIsImEiOiJjbHU0ODBwajIxOHpoMmtwZG1tcGNzeWZ2In0.mcRExtaG9PtQ1UVuoGRehg"
px.set_mapbox_access_token(mapbox_access_token)


def generate_map(selected_projects, selected_instruments):
    filtered_data = filter_data_for_projects_and_instruments(
        selected_projects, selected_instruments
    )

    # Determine the appropriate zoom level
    zoom_level = 4.8  # Default zoom level
    if (
        "South Atlantic Meridional Overturning Circulation Basin-wide Array"
        in selected_projects
    ):
        zoom_level = 3.7

    if filtered_data.empty:
        # If there is no data, create an empty map with only the chosen Mapbox style
        fig = px.scatter_mapbox(
            lat=[],
            lon=[],
            zoom=zoom_level,
            height=700,
            labels={"Project_Abbr": "Project"},
            title="No Data Available",
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": -31.0, "lon": 23.0},
            legend_title_text="Project Name",  # Legend title
        )
    else:
        # If data is available, create the map with the filtered data
        fig = px.scatter_mapbox(
            filtered_data,
            lat="Lat (°S)",
            lon="Lon (°E)",
            hover_name="Station",
            hover_data={
                "Project_Abbr": False,
                "Platform": True,
                "Instrument_Type": True,
            },  # Add Platform and Type to hover data
            color="Project_Abbr",  # Use Project_Abbr for legend
            color_discrete_sequence=["red", "navy", "forestgreen", "black"],
            zoom=zoom_level,
            height=600,
            width=3000,
            labels={"Project_Abbr": "Project"},
            title="Sampling Stations for Selected Projects",
        )
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox_center={"lat": -29.0, "lon": 23.0},
            legend_title_text="Project Name",  # Legend title
            legend_title=dict(
                font=dict(size=14, color="black", family="Helvetica")
            ),  # Customize font size, color, and style
            margin=dict(
                l=0, r=0, t=30, b=0
            ),  # Remove margins (left, right, top, bottom)
        )
        fig.update_traces(marker=dict(size=8, symbol="circle", opacity=0.7))

    return fig


# Main layout: map followed by project details
st.header("Sampling Stations Map")
map_fig = generate_map(selected_projects, selected_instruments)
st.plotly_chart(map_fig, config=config_figure)

# Custom CSS to reduce the font size for the "Project Details" header
st.markdown(
    """
    <style>
    h2 {
        font-size: 1.2rem !important;  /* Adjust the size as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Project details below the map
st.markdown("<h2>PROJECT DETAILS</h2>", unsafe_allow_html=True)


# Inject custom CSS to increase the font size of expander labels
st.markdown(
    """
    <style>
    div[data-testid="stExpander"] details summary p {
        font-size: 1.1rem;  /* You can adjust this size as needed */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if selected_projects:
    for project in selected_projects:
        # Add emojis next to the project headings
        emoji_map = {
            "Integrated Ecosystem Programme: Southern Benguela": "🌊🐚🔬",
            "Long-term monitoring of nearshore temperatures around Southern Africa": "🌡️",
            "West Coast Cetacean Distribution and Abundance Survey": "🐋🐬🧫",
            "South Atlantic Meridional Overturning Circulation Basin-wide Array": "🌊🐚🔬",
        }
        with st.expander(f"{emoji_map.get(project, '')} {project}"):
            project_description = {
                "Integrated Ecosystem Programme: Southern Benguela": """
                    The Integrated Ecosystem Programme (IEP) in the Southern Benguela region focuses on understanding the complex interactions
                    between physical, chemical, and biological components of the marine ecosystem. This project aims to develop ecosystem indicators
                    that aid in monitoring and managing the region's rich biodiversity and resources.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=Integrated+Ecosystem+Programme:+Southern+Benguela+(IEP:+SB)' target='_blank'>data source</a>.
                """,
                "Long-term monitoring of nearshore temperatures around Southern Africa": """
                    The Long-term monitoring of nearshore temperatures around Southern Africa monitors underwater temperature fluctuations in South African waters.
                    The data collected helps in understanding ocean dynamics and their impact on marine life and ecosystems.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=Long-term+monitoring+of+nearshore+temperatures+around+Southern+Africa' target='_blank'>data source</a>.
                """,
                "West Coast Cetacean Distribution and Abundance Survey": """
                    The West Coast Cetacean Distribution and Abundance Survey, conducted on the Algoa Voyage 254, focused on collecting data on humpback whales along the west coast of South Africa.
                    The research included genetic relatedness, stock identification, abundance, feeding, and migratory behaviors of large whales.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=West+Coast+Cetacean+Distribution+and+Abundance+Survey' target='_blank'>data source</a>.
                """,
                "South Atlantic Meridional Overturning Circulation Basin-wide Array": """
                    The South Atlantic Meridional Overturning Circulation Basin-wide Array (SAMBA) monitors oceanographic conditions in the South Atlantic,
                    focusing on the meridional overturning circulation and its role in climate regulation and nutrient distribution.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=South+Atlantic+Meridional+Overturning+Circulation+Basin-wide+Array+(SAMBA)' target='_blank'>data source</a>.
                """,
            }
            st.markdown(
                project_description.get(project, "Project description not available."),
                unsafe_allow_html=True,
            )
elif selected_instruments:
    # If only instruments are selected, show details for all relevant projects
    relevant_projects = data[
        data["Instrument_Type"].apply(
            lambda x: any(inst in x for inst in selected_instruments)
        )
    ]["Project_Name"].unique()
    for project in relevant_projects:
        emoji_map = {
            "Integrated Ecosystem Programme: Southern Benguela": "🐟",
            "Long-term monitoring of nearshore temperatures around Southern Africa": "🌡️",
            "West Coast Cetacean Distribution and Abundance Survey": "🐋",
            "South Atlantic Meridional Overturning Circulation Basin-wide Array": "🌊",
        }
        with st.expander(f"{emoji_map.get(project, '')} {project}"):
            project_description = {
                "Integrated Ecosystem Programme: Southern Benguela": """
                    The Integrated Ecosystem Programme (IEP) in the Southern Benguela region focuses on understanding the complex interactions
                    between physical, chemical, and biological components of the marine ecosystem. This project aims to develop ecosystem indicators
                    that aid in monitoring and managing the region's rich biodiversity and resources.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=Integrated+Ecosystem+Programme:+Southern+Benguela+(IEP:+SB)' target='_blank'>data source</a>.
                """,
                "Long-term monitoring of nearshore temperatures around Southern Africa": """
                    The Long-term monitoring of nearshore temperatures around Southern Africa monitors underwater temperature fluctuations in South African waters.
                    The data collected helps in understanding ocean dynamics and their impact on marine life and ecosystems.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=Long-term+monitoring+of+nearshore+temperatures+around+Southern+Africa' target='_blank'>data source</a>.
                """,
                "West Coast Cetacean Distribution and Abundance Survey": """
                    The West Coast Cetacean Distribution and Abundance Survey, conducted on the Algoa Voyage 254, focused on collecting data on humpback whales along the west coast of South Africa.
                    The research included genetic relatedness, stock identification, abundance, feeding, and migratory behaviors of large whales.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=West+Coast+Cetacean+Distribution+and+Abundance+Survey' target='_blank'>data source</a>.
                """,
                "South Atlantic Meridional Overturning Circulation Basin-wide Array": """
                    The South Atlantic Meridional Overturning Circulation Basin-wide Array (SAMBA) monitors oceanographic conditions in the South Atlantic,
                    focusing on the meridional overturning circulation and its role in climate regulation and nutrient distribution.
                    <br><br>For more details, you can visit the <a href='https://data.ocean.gov.za/mims/catalog/?facet_project=South+Atlantic+Meridional+Overturning+Circulation+Basin-wide+Array+(SAMBA)' target='_blank'>data source</a>.
                """,
            }
            st.markdown(
                project_description.get(project, "Project description not available."),
                unsafe_allow_html=True,
            )
else:
    st.write(
        "No project selected. Please select a project or instrument to view details."
    )
