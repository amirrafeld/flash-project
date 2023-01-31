from flaskblog import create_app
import dash
import random
from dash.dependencies import Input, Output
from flask import Blueprint
from flask_debugtoolbar import DebugToolbarExtension
from flaskblog.dash.routes import update_dash_layout, techanical_data
import dash_bootstrap_components as dbc
import time

app = create_app()
ks = Blueprint('ks', __name__)
app.register_blueprint(ks, url_prefix='/test/')
dash_app = dash.Dash(__name__, server=app, url_base_pathname='/dash/', external_stylesheets=[dbc.themes.CYBORG], )


X = list(range(10))
Y = [random.uniform(0, 1) for i in range(10)]
dash_app.Layout = update_dash_layout(dash_app)


@dash_app.callback(Output('graph-container', 'style'),
                   [Input('submitButton', 'n_clicks')])
def update_graph_scatter(n_clicks):
    if n_clicks:
        time.sleep(7)
        return {'display': 'block'}
    return {'display': 'none'}


@dash_app.callback(Output(component_id='live-graph', component_property='figure'),
                   [Input(component_id='submitButton', component_property='n_clicks'),
                    Input('stockInput', 'value'),
                    Input(component_id='date', component_property='value'),
                    Input(component_id='graph-update', component_property='n_intervals')
                    ], prevent_initial_call=True
                   )
def try_dash(n_click, stock_input, date, n_interval):
    techanical_data(n_clicks=n_click, ticker=stock_input, period=date, refresh=n_interval)


app.debug = True
toolbar = DebugToolbarExtension(app)
if __name__ == "__main__":
    app.run(debug=True, load_dotenv=True)
