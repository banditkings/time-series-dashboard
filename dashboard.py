from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from statsmodels.tsa.exponential_smoothing.ets import ETSModel

df = pd.read_csv('https://raw.githubusercontent.com/banditkings/datasets/main/TimeSeries/AirPassengers.csv')

external_stylesheets = [
     "https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap"
]

app = Dash(__name__, external_stylesheets=external_stylesheets)
app.css.config.serve_locally = True

def forecast(df):
    model = ETSModel(df["#Passengers"],
                     error="add",
                     trend="add",
                     seasonal="add",
                     damped_trend=True,
                     seasonal_periods=12)
    fit = model.fit(maxiter=1000)
    pred = fit.get_prediction(start=len(df), end=len(df)+5)
    result = pred.summary_frame(alpha=0.05)
    result['Month'] = ['1961-01', '1961-02', '1961-03', '1961-04', '1961-05', '1961-06']
    result.rename({'mean':'Forecast'}, axis=1, inplace=True)
    result = result[['Month', 'Forecast', 'pi_lower', 'pi_upper']].round(2)
    return result

fcst = forecast(df)

app.layout = html.Div([
    # Title
    html.H1(children="Dashboard Title", id="db-name"),
    dcc.Markdown("""
        This interactive report shows how you might construct a helper dashboard that does time series forecasting. 

        The data table below provides the forecast and prediction intervals, and allows the user to override the forecast and export the forecast to CSV.
    """),
    # Line Chart with Historicals and Forecast
    dcc.Graph(id='editable-table-output'),
    # Editable DataTable where user can override the forecast
    dash_table.DataTable(
        id='editable-table',
        columns=(
            [{"name": i, "id": i} for i in fcst.columns]
        ),
        data=fcst.to_dict('records'),
        editable=True,
        fixed_rows={'headers': True},  # Freeze Header
        page_size=100,
        export_format='csv', # Add Export Button
        style_cell={'textAlign': 'center', 'font_family':"'Press Start 2P'"},
        style_table={'height': '300px', 'overflowY': 'auto'}, # Vertical Scrollbar
    ),
], id="main_page")

# Create a callback to update the figure based on what's in the datatable
@app.callback(
    Output('editable-table-output', 'figure'),
    Input('editable-table', 'data'),
    Input('editable-table', 'columns'))
def display_output(rows, columns):
    """Update the figure based on the datatable contents"""
    fcst_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    fig = go.Figure()
    x = fcst_df.Month
    fig.add_trace(go.Scatter(x=df.tail(50).Month, y=df.tail(50)['#Passengers'], name="Actuals", 
                             line_width=4, line_color="gray"))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df.Forecast, name='Forecast', 
                             mode='lines', line_width=3))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df['pi_upper'], 
                             name='Upper PI', mode='lines',
                             line={'color':'grey', 'dash':'dot'}))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df['pi_lower'], 
                             name='Lower PI', mode='lines',
                             line={'color':'grey', 'dash':'dot'}))
    fig.update_layout(title="AutoETS (A, A, A) Forecast", font_family="'Press Start 2P', Arial", template="plotly_white")
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost', port=1234)