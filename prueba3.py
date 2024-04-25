import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import dash_bootstrap_components as dbc

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.YETI], suppress_callback_exceptions=True)

# Diccionario para almacenar los datos ingresados para cada línea de producción
datos_por_linea = {
    'linea1': {},
    'linea2': {},
    'linea3': {}
}

# Lista para almacenar los valores máximos de OEE alcanzados para cada línea de producción
maximos_oee = {
    'linea1': 0,
    'linea2': 0,
    'linea3': 0
}

app.layout = dbc.Container([
    html.H1('Dashboard Prueba', className='my-4 text-center'),
    dbc.Row([
        dbc.Col([
            html.Label('Tiempo Total Disponible de Producción (horas):'),
            dcc.Input(id='input-tiempo-total', type='number', value=7.5, step=0.1, className='form-control')
        ], width=3),
        dbc.Col([
            html.Label('Tiempo de Inactividad por Errores/Problemas (horas):'),
            dcc.Input(id='input-tiempo-inactividad-errores', type='number', value=1, step=0.1, className='form-control')
        ], width=3),
        dbc.Col([
            html.Label('Producción Real (lt):'),
            dcc.Input(id='input-produccion-real', type='number', value=1, className='form-control')
        ], width=3),
        dbc.Col([
            html.Label('Producción Máxima (lt):'),
            dcc.Input(id='input-produccion-maxima', type='number', value=1, className='form-control')
        ], width=3),
    ], className='my-5'),
    dbc.Row([
        dbc.Col([
            html.Label('Productos Buenos:'),
            dcc.Input(id='input-productos-buenos', type='number', value=1, className='form-control')
        ], width=3),
        dbc.Col([
            html.Label('Seleccionar Línea de Producción:'),
            dcc.Dropdown(
                id='dropdown-linea-produccion',
                options=[
                    {'label': 'Línea 1', 'value': 'linea1'},
                    {'label': 'Línea 2', 'value': 'linea2'},
                    {'label': 'Línea 3', 'value': 'linea3'}
                ],
                value=None,
                className='form-select'
            )
        ], width=3),
    ], className='my-5'),
    dbc.Row([
        dbc.Col([
            html.Div(id='oee-output-linea1')
        ], width=3),
        dbc.Col([
            html.Div(id='oee-output-linea2')
        ], width=3),
        dbc.Col([
            html.Div(id='oee-output-linea3')
        ], width=3),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='oee-graph-linea1')
        ], width=3),
        dbc.Col([
            dcc.Graph(id='oee-graph-linea2')
        ], width=3),
        dbc.Col([
            dcc.Graph(id='oee-graph-linea3')
        ], width=3),
    ])
], className='p-6')

@app.callback(
    [Output('input-tiempo-total', 'value'),
     Output('input-tiempo-inactividad-errores', 'value'),
     Output('input-produccion-real', 'value'),
     Output('input-produccion-maxima', 'value'),
     Output('input-productos-buenos', 'value')],
    [Input('dropdown-linea-produccion', 'value')]
)
def cargar_valores_linea(linea_produccion):
    if linea_produccion is None:
        return None, None, None, None, None

    if linea_produccion in datos_por_linea:
        datos_linea = datos_por_linea[linea_produccion]
        try:
            tiempo_total = float(datos_linea.get('tiempo_total', 0))
            tiempo_inactividad_errores = float(datos_linea.get('tiempo_inactividad_errores', 0))
            produccion_real = float(datos_linea.get('produccion_real', 0))
            produccion_maxima = float(datos_linea.get('produccion_maxima', 0))
            productos_buenos = float(datos_linea.get('productos_buenos', 0))
            return tiempo_total, tiempo_inactividad_errores, produccion_real, produccion_maxima, productos_buenos
        except (ValueError, TypeError):
            return 0, 0, 0, 0, 0
    else:
        return 0, 0, 0, 0, 0



@app.callback(
    [Output('oee-output-linea1', 'children'),
     Output('oee-graph-linea1', 'figure'),
     Output('oee-output-linea2', 'children'),
     Output('oee-graph-linea2', 'figure'),
     Output('oee-output-linea3', 'children'),
     Output('oee-graph-linea3', 'figure')],
    [Input('input-tiempo-total', 'value'),
     Input('input-tiempo-inactividad-errores', 'value'),
     Input('input-produccion-real', 'value'),
     Input('input-produccion-maxima', 'value'),
     Input('input-productos-buenos', 'value'),
     Input('dropdown-linea-produccion', 'value')]
)
def calcular_oee(tiempo_total, tiempo_inactividad_errores, produccion_real, produccion_maxima, productos_buenos, linea_produccion):
    try:
        if tiempo_total is None or tiempo_inactividad_errores is None or produccion_real is None or produccion_maxima is None or productos_buenos is None or linea_produccion is None:
            return "", {'data': [], 'layout': {}}, "", {'data': [], 'layout': {}}, "", {'data': [], 'layout': {}}

        tiempo_total = float(tiempo_total)
        tiempo_inactividad_errores = float(tiempo_inactividad_errores)
        tiempo_real = tiempo_total - tiempo_inactividad_errores
        disponibilidad = (tiempo_real / tiempo_total) * 100
        rendimiento = (float(produccion_real) / float(produccion_maxima)) * 100
        calidad = (float(productos_buenos) / float(produccion_real)) * 100
        oee = disponibilidad * rendimiento * calidad / 10000

        # Guardar los datos en el diccionario correspondiente
        if linea_produccion not in datos_por_linea:
            datos_por_linea[linea_produccion] = {}
        datos_por_linea[linea_produccion] = {
            'tiempo_total': tiempo_total,
            'tiempo_inactividad_errores': tiempo_inactividad_errores,
            'produccion_real': produccion_real,
            'produccion_maxima': produccion_maxima,
            'productos_buenos': productos_buenos,
            'oee': oee
        }

        # Actualizar el máximo OEE alcanzado si es necesario
        if oee > maximos_oee[linea_produccion]:
            maximos_oee[linea_produccion] = oee

        # Preparar los datos para el gráfico de la línea seleccionada
        x_labels = ['Disponibilidad', 'Rendimiento', 'Calidad', 'OEE']
        y_values = [disponibilidad, rendimiento, calidad, oee]
        colors = ['blue', 'green', 'orange', 'red']
        text_values = [f'{label}: {value:.2f}%' for label, value in zip(x_labels, y_values)]
        oee_figure = {
            'data': [
                {'x': x_labels,
                 'y': y_values,
                 'type': 'bar',
                 'marker': {'color': colors},
                 'text': text_values}
            ],
            'layout': {
                'yaxis': {'range': [0, 100]}
            }
        }

        # Mostrar los resultados en función de la línea seleccionada
        if linea_produccion == 'linea1':
            return f'OEE: {oee:.2f}%', oee_figure, "", {'data': [], 'layout': {}}, "", {'data': [], 'layout': {}}
        elif linea_produccion == 'linea2':
            return "", {'data': [], 'layout': {}}, f'OEE: {oee:.2f}%', oee_figure, "", {'data': [], 'layout': {}}
        elif linea_produccion == 'linea3':
            return "", {'data': [], 'layout': {}}, "", {'data': [], 'layout': {}}, f'OEE: {oee:.2f}%', oee_figure

    except (ValueError, TypeError):
        return "Ingrese valores válidos", {'data': [], 'layout': {}}, "Ingrese valores válidos", {'data': [], 'layout': {}}, "Ingrese valores válidos", {'data': [], 'layout': {}}



if __name__ == '__main__':
    app.run_server(debug=True)
