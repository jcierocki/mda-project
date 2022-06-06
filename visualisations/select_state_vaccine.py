from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots
import plotly.graph_objects as go

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id="graph"),
    dcc.Dropdown(['AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DC', 'DE', 'FL', 'GA', 'GU', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS', 'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM', 'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VI', 'VT', 'WA', 'WI', 'WV', 'WY'],
                 'AK', id='dropdown'),
])


@app.callback(
    Output("graph", "figure"),
    Input("dropdown", "value"))
def update_line_charts_vaccine(state):
    vaccinations_state_df = pd.read_csv('vaccinations_by_state.csv')
    print(vaccinations_state_df)
    column_date = 'date'
    column_pct_vaccinated = 'pct_vaccinated'
    column_fully_vaccinated = 'fully_vaccinated'
    column_total_pop = 'total_pop'

    fig_selected_state_vaccine = make_subplots(rows=1, cols=1,
                                               subplot_titles=('Number of vaccinated people',),
                                                               #Percentage of vaccinated people'),
                                               vertical_spacing=0.35)

    # First subplot
    fig_selected_state_vaccine.add_trace(go.Scatter(x=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_date],
                                                    y=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_fully_vaccinated],
                                                    mode='lines',
                                                    name=column_fully_vaccinated),
                                         row=1, col=1)

    fig_selected_state_vaccine['layout']['yaxis1'].update(title='Number',
                                                          range=[min(vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_fully_vaccinated]),
                                                                 max(vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_total_pop])],
                                                          autorange=False)
    fig_selected_state_vaccine['layout']['xaxis1'].update(title='Date')
    ''' # Hidden second subplot
        # Second subplot
        fig_selected_state_vaccine.add_trace(go.Scatter(x=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_date],
                                                        y=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_pct_vaccinated],
                                                        mode='lines',
                                                        name=column_pct_vaccinated),
                                             row=2, col=1)
        fig_selected_state_vaccine['layout']['yaxis2'].update(title='Per cent') '''
    # Update layout
    fig_selected_state_vaccine.update_layout(title_text="State: {}".format(state), showlegend=False)
    fig_selected_state_vaccine.update_xaxes(rangeslider_visible=True, rangeslider_thickness=0.075)
    return fig_selected_state_vaccine


app.run_server(debug=True)
