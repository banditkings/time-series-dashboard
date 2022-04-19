from dash import Dash, dash_table, dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px

df = pd.read_csv('https://raw.githubusercontent.com/banditkings/datasets/main/TimeSeries/AirPassengers.csv')

app = Dash(__name__)

app.layout = html.Div([
    dcc.Graph(id='table-editing-simple-output'),
    dash_table.DataTable(
        id='table-editing-simple',
        columns=(
            [{"name": i, "id": i} for i in df.columns]
        ),
        data=df.to_dict('records'),
        editable=True,
        fixed_rows={'headers': True},  # Freeze Header
        page_size=100,
        style_table={'height': '300px', 'overflowY': 'auto'}, # Vertical Scrollbar
    )
])

@app.callback(
    Output('table-editing-simple-output', 'figure'),
    Input('table-editing-simple', 'data'),
    Input('table-editing-simple', 'columns'))
def display_output(rows, columns):
    df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
    return px.line(df, x="Month", y="#Passengers")

if __name__ == '__main__':
    app.run_server(debug=True)