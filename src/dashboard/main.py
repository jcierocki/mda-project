from typing import Literal
import dash
from dash import dcc, html
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.figure_factory as ff
import pandas as pd
from pymongo import MongoClient
import requests
from datetime import datetime, date
# import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate
from dash.dependencies import Output, Input
from datetime import datetime, timedelta

db = MongoClient()["MDAProjectDatabase"]

app = dash.Dash(
    __name__,
    # external_stylesheets=external_stylesheets,
    url_base_pathname="/"
)

with app.server.app_context():
    fips_dict_df = pd.DataFrame.from_records(db["fips_codes"].find({}, {"_id": 0}))
    fips_dict_df.loc[fips_dict_df.state_name.notna(), "full_area_name"] = [area + ", " + state_name for (area, state_name) in zip(fips_dict_df.area, fips_dict_df.state_name) if pd.isna(state_name) is not True]
    fips_dict_df.loc[fips_dict_df.state_name.isna(), "full_area_name"] = fips_dict_df.area
    fips_dict_df = fips_dict_df.set_index("full_area_name")

    date_max = datetime.strptime(
        db["daily_covid_cases"] \
            .find({}, {"date": 1, "_id": 0}) \
            .sort("date", -1) \
            .limit(1)[0]["date"],
        "%Y-%m-%d"
    ).date()

    date_min = datetime.strptime(
        db["daily_covid_cases"] \
            .find({}, {"date": 1, "_id": 0}) \
            .sort("date", 1) \
            .limit(1)[0]["date"],
        "%Y-%m-%d"
    ).date()

    states_counterfactual_model = db["counterfactual_model_results"].distinct("state_name")

    states_vaccinations = db["vaccinations"].distinct("state_name")

    ## static plots below

    data_fcst = pd.DataFrame(db["country_level_cases_with_forecasts"].find({}, {"_id": 0}))
    fig_fcst = px.line(
        data_fcst,
        x="date",
        y=["cases", "Forecast 1", "Forecast 2"],
        width=1500
    )

    fig_fcst.update_xaxes(rangeslider_visible=True)


app.layout = html.Div([
    html.Div([
        html.H1("COVID dynamic through time"),
        dcc.Graph(id="cases-deaths-lineplot"),
        html.Div(children=[
            dcc.Dropdown(
                fips_dict_df.index, 
                fips_dict_df.index[0], 
                id='dropdown-cases-deaths-lineplot', 
                style={'display': 'inline-block', 'width': "50%"}),
            dcc.RadioItems(
                id='radio-cases-deaths-lineplot',
                options=['One Y axis', 'Two Y axes'],
                value='Two Y axes',
                style={'display': 'inline-block'}
            ),
        ])
    ], style={'display': 'block', 'width': "1500px", "margin": "0 auto"}),
    html.Br(),
    html.Div([
        html.H1("Infections and deaths by geografical location"),
        html.Div(children=[
            html.Div([
                dcc.Graph(id="map-cases"),
                dcc.DatePickerSingle(
                    id="date-picker-cases",
                    min_date_allowed=date_min,
                    max_date_allowed=date_max,
                    initial_visible_month=date_max,
                    date=date_max
                ),
            ], style={'display': 'inline-block', 'width': "750px"}),
            html.Div([
                dcc.Graph(id="map-deaths"),
                dcc.DatePickerSingle(
                    id="date-picker-deaths",
                    min_date_allowed=date_min,
                    max_date_allowed=date_max,
                    initial_visible_month=date_max,
                    date=date_max
                )
            ], style={'display': 'inline-block', 'width': "750px"}),
        ]),
    ], style={'display': 'block', 'width': "1500px", "margin": "0 auto"}),
    html.Div(children=[
        html.H1("Forecasting cases for next 30 days using Exponential Smoothing"),
        html.P("Exponential Smoothing model was tuned using grid search and rolled validation set. Best MAPE was obtained for the model with both trend and seasonality additive, damped trend and Box-Cox transformation. Seasonal period was assumed to be equal 7, as there is observed weekly cycle in collecting COVID-19-related data."),
        dcc.Graph(id="ts-fcst", figure=fig_fcst)
    ], style={'display': 'block', 'width': "1500px", "margin": "0 auto"}),
    html.Div(children=[
        html.H1("Counterfactual model"),
        html.P("Some description..."),
        dcc.Graph(id="counterfactual-model-results-lineplot"),
        dcc.Dropdown(
            states_counterfactual_model,
            states_counterfactual_model[0],
            id="counterfactual-model-state-dropdown",
            style={'display': 'inline-block', 'width': "500px"}
        )
    ], style={'display': 'block', 'width': "1500px", "margin": "0 auto"}),
    html.Div(children=[
        html.H1("Vaccinations by state"),
        dcc.Graph("vaccinations-lineplot"),
        dcc.Dropdown(
            states_vaccinations,
            states_vaccinations[0],
            id="vaccinations-states",
            style={'display': 'inline-block', 'width': "500px"}
        )
    ], style={"display": "block", "width": "1500px", "margin": "0 auto"})
], style={"display": "block"})

@app.callback(
    Output("cases-deaths-lineplot", "figure"), 
    [
        Input("radio-cases-deaths-lineplot", "value"),
        Input("dropdown-cases-deaths-lineplot", "value")
    ]
)
def update_line_chart(radio_value, full_area_name):
    fips = fips_dict_df.loc[full_area_name, "fips"]

    data = db["daily_covid_cases"].find(
        {"fips": fips}, 
        {"date": 1, "cases": 1, "deaths": 1, "_id": 0}
    )
    df = pd.DataFrame(data)

    fig_selected_county = make_subplots(specs=[[{"secondary_y": True}]])

    fig_selected_county.add_trace(
        go.Scatter(x=df.date,
                   y=df.cases,
                   name="Cases"),
        secondary_y=False,
    )

    fig_selected_county.add_trace(
        go.Scatter(x=df.date,
                   y=df.deaths,
                   name="Deaths"),
        secondary_y=radio_value == 'Two Y axes',
    )

    fig_selected_county.update_layout(
        title=full_area_name,
        xaxis_title="Date",
        yaxis_title="Value",
        legend_title="Variable",
        width=1500
    )

    fig_selected_county.update_yaxes(
        title_text="Cases",
        secondary_y=False)

    fig_selected_county.update_yaxes(
        title_text="Deaths",
        secondary_y=True)

    fig_selected_county.update_xaxes(rangeslider_visible=True)

    return fig_selected_county


def update_map(date_value: str, variable: Literal["cases", "deaths"]):
    selected_date = date.fromisoformat(date_value).strftime("%Y-%m-%d")

    data = db["daily_covid_cases"].find(
        {"date": selected_date}, 
        {"fips": 1, variable: 1, "_id": 0}
    )
    df = pd.DataFrame(data)

    fig_selected_date = ff.create_choropleth(fips=df.fips, values=df[variable])
    
    fig_selected_date.layout.template = None
    fig_selected_date.update_layout(
        title=f'Map of daily COVID-19 {variable} - {selected_date}',
        font=dict(
            size=15,
            color="Black"
        ),
        width=750
    )

    return fig_selected_date

@app.callback(
    Output("map-cases", "figure"), 
    Input("date-picker-cases", "date")
)
def update_map_cases(date_value):
    return update_map(date_value, "cases")


@app.callback(
    Output("map-deaths", "figure"), 
    Input("date-picker-deaths", "date")
)
def update_map_deaths(date_value):
    return update_map(date_value, "deaths")


@app.callback(
    Output("counterfactual-model-results-lineplot", "figure"),
    Input("counterfactual-model-state-dropdown", "value")
)
def update_line_chart_masks(state_name):
    model_masks_df = pd.DataFrame(db["counterfactual_model_results"].find({"state_name": state_name}, {"_id": 0}))

    fig_selected_state_masks = px.line(
        model_masks_df,
        x="date",
        y="value",
        color="variable"
    )

    fig_selected_state_masks.update_layout(
        title=state_name,
        xaxis_title="Date",
        yaxis_title="Value",
        legend_title="Variable"
    )

    fig_selected_state_masks.update_xaxes(rangeslider_visible=True)

    return fig_selected_state_masks


@app.callback(
    Output("vaccinations-lineplot", "figure"),
    Input("vaccinations-states", "value")
)
def update_line_chart_vaccinations(state_name):
    vaccinations_state_df = pd.DataFrame(db["vaccinations"].find({"state_name": state_name}, {"_id": 0}))

    fig_selected_state_vaccine = make_subplots(
        rows=1, 
        cols=1,
        subplot_titles=('Number of vaccinated people'),#Percentage of vaccinated people'),
        vertical_spacing=0.35
    )

    fig_selected_state_vaccine.add_trace(
        go.Scatter(
            x=vaccinations_state_df.date,
            y=vaccinations_state_df.fully_vaccinated,
            mode='lines',
            name="fully_vaccinated"
        ),
        row=1, 
        col=1
    )

    fig_selected_state_vaccine['layout']['yaxis1'].update(
        title='Number',
        range=[vaccinations_state_df.fully_vaccinated.min(), vaccinations_state_df.total_pop.max()],
        autorange=False
    )
    fig_selected_state_vaccine['layout']['xaxis1'].update(title='Date')
    # ''' # Hidden second subplot
    #     # Second subplot
    #     fig_selected_state_vaccine.add_trace(go.Scatter(x=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_date],
    #                                                     y=vaccinations_state_df.loc[vaccinations_state_df['state_code'] == state][column_pct_vaccinated],
    #                                                     mode='lines',
    #                                                     name=column_pct_vaccinated),
    #                                          row=2, col=1)
    #     fig_selected_state_vaccine['layout']['yaxis2'].update(title='Per cent') '''

    fig_selected_state_vaccine.update_layout(title_text=state_name, showlegend=False, width=1500)
    fig_selected_state_vaccine.update_xaxes(rangeslider_visible=True, rangeslider_thickness=0.075)

    return fig_selected_state_vaccine


if __name__ == '__main__':
    app.run_server(debug=True, host="127.0.0.1", port=8000)