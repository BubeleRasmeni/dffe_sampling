import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import io
import streamlit as st

# Configuration for high-resolution plot export
config_figure = {
    "toImageButtonOptions": {
        "format": "png",  # one of png, svg, jpeg, webp
        "filename": "DFFE_Sampling_Stations_figure",
        "height": 800,
        "width": 1400,
        "scale": 3,  # Multiply title/legend/axis/canvas sizes by this factor
    }
}
