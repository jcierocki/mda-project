from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="graph"),
    dcc.Dropdown(['Mississippi', 'Michigan', 'Iowa', 'Montana', 'Texas', 'Wyoming', 'Arkansas', 'Kansas', 'Wisconsin', 'Colorado', 'Indiana', 'Alabama', 'Utah', 'New Hampshire', 'Louisiana', 'Minnesota', 'North Carolina', 'Maryland', 'Virginia', 'Delaware', 'Maine', 'New Jersey', 'Massachusetts', 'Ohio', 'Illinois', 'Kentucky', 'Vermont', 'West Virginia', 'New York', 'Pennsylvania', 'Oregon', 'Rhode Island', 'North Dakota', 'Nevada', 'Connecticut', 'California', 'Washington', 'New Mexico', 'Hawaii', 'Nebraska'],
                 'Mississippi', id='dropdown'),
])


@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value"))
def update_line_chart_masks(state):
    model_masks_df = pd.read_csv('sample_model_results.csv')
    fig_selected_state_masks = px.line(model_masks_df.loc[model_masks_df['state_code'] == state].set_index(['state_code']),
                                       x="date", y=model_masks_df.columns[3], color='variable'
                                       )
    # Update figure layout
    fig_selected_state_masks.update_layout(
        title={
            'text': 'State: {}'.format(str((model_masks_df.loc[model_masks_df['state_code'] == state].set_index(['state_code']).index.values[0])))
        },
        xaxis_title="Date",
        yaxis_title="Value",
        legend_title="Variable"
    )
    # Slider for choosing date range
    fig_selected_state_masks.update_xaxes(rangeslider_visible=True)
    return fig_selected_state_masks


app.run_server(debug=True)
