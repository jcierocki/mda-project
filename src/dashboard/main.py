
import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd
from pymongo import MongoClient
import requests

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
    fips_dict_df["full_area_name"] = fips_dict_df[["area", "state_name"]].apply(tuple, axis=1).str.join(', ')
    fips_dict_df = fips_dict_df.set_index("full_area_name")

app.layout = html.Div([
    dcc.Graph(id="graph"),
    dcc.Dropdown(fips_dict_df.index, fips_dict_df.index[0], id='dropdown'),
])

@app.callback(
    Output("graph", "figure"), 
    Input("dropdown", "value")
)
def update_line_chart(full_area_name):
    fips = fips_dict_df.loc[full_area_name, "fips"]

    data = db["daily_covid_cases"].find(
        {"fips": fips}, 
        {"data": {"date": 1, "cases": 1}, "_id": 0}
    )
    df = pd.DataFrame(data[0]["data"])
    
    fig_selected_county = px.line(df, x="date", y="cases")

    fig_selected_county.update_layout(
        title=full_area_name,
        xaxis_title="Date",
        yaxis_title="Value",
        legend_title="Variable"
    )

    fig_selected_county.update_xaxes(rangeslider_visible=True)

    return fig_selected_county

if __name__ == '__main__':
    app.run_server(debug=True, host="127.0.0.1", port=8000)