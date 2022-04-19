from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from statsmodels.tsa.exponential_smoothing.ets import ETSModel
# from statsmodels.tsa.forecasting.theta import ThetaModel

df = pd.read_csv('https://raw.githubusercontent.com/banditkings/datasets/main/TimeSeries/AirPassengers.csv')

app = Dash(__name__)

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
    return result

forecast = forecast(df)

app.layout = html.Div([
    dcc.Graph(id='table-editing-simple-output'),
    dash_table.DataTable(
        id='table-editing-simple',
        columns=(
            [{"name": i, "id": i} for i in forecast.columns]
        ),
        data=forecast.to_dict('records'),
        editable=True,
        fixed_rows={'headers': True},  # Freeze Header
        page_size=100,
        style_table={'height': '300px', 'overflowY': 'auto'}, # Vertical Scrollbar
    ),
])

@app.callback(
    Output('table-editing-simple-output', 'figure'),
    Input('table-editing-simple', 'data'),
    Input('table-editing-simple', 'columns'))
def display_output(rows, columns):
    fcst_df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.tail(50).Month, y=df.tail(50)['#Passengers'], name="Actuals"))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df.Forecast, name='Forecast', mode='lines'))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df['pi_upper'], 
                             name='Upper PI', mode='lines',
                             line={'color':'grey', 'dash':'dot'}))
    fig.add_trace(go.Scatter(x=fcst_df.Month, y=fcst_df['pi_lower'], 
                             name='Lower PI', mode='lines',
                             line={'color':'grey', 'dash':'dot'}))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True, host='localhost')