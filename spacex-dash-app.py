# Import required libraries
import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# TASK 1: Add a dropdown list to enable Launch Site selection
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in launch_sites]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Launch Site dropdown
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),

    # TASK 2: Pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Payload range slider
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload]
    ),
    html.Br(),

    # TASK 4: Scatter chart for payload vs launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # All sites: total success counts
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches by Site'
        )
    else:
        # Filter for selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = filtered_df['class'].value_counts().reset_index()
        success_count.columns = ['class', 'count']
        fig = px.pie(
            success_count,
            names='class',
            values='count',
            title=f'Total Success vs Failure for site {selected_site}'
        )
    return fig

# TASK 4: Callback for scatter chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    low, high = payload_range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]

    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Payload vs. Outcome for Selected Site(s)'
    )
    return fig

# Run the app
if __name__ == '__main__':
    import socket
    import os

    # Get the host IP (0.0.0.0 is needed for cloud IDEs)
    host = '0.0.0.0'
    port = 8050

    # Construct a URL for browser access if in a cloud IDE
    workspace_url = os.getenv("WORKSPACE_URL")
    if workspace_url:
        print(f"Open this URL in your browser to access the Dash app: {workspace_url}:{port}")
    else:
        # fallback message if not in a cloud IDE
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"Running on http://{ip}:{port}")

    app.run(host=host, port=port, debug=True)


