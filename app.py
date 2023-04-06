from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.request import urlretrieve
from datetime import datetime, timedelta
import os
import pandas as pd

def list_datasets():
	datasets = os.listdir('datasets/')
	assets = []
	for dataset in datasets:
		assets.append(dataset.replace('.csv',''))
	return sorted(assets)

avalaible_datasets = list_datasets()													# Initial creating list of datasets

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions = True)

app.layout = html.Div(
	dbc.Container([
		# NAVIGATION
		dbc.Row([
			dbc.Col([
				dbc.Nav([
					dbc.NavItem([
						dbc.Button('Data', id='open_modal_button', n_clicks=0),
					]),
					dbc.NavItem([
						dcc.Dropdown(avalaible_datasets, id='asset'),
					]),
					dbc.NavItem(
						dbc.DropdownMenu(label='Range', children=[
							dcc.RadioItems(['3M', '6M', '1Y', '3Y', 'Max'], 'Max', id='date_range', labelStyle={'display': 'block'}),
						]),						
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Main chart', children=[
							dcc.RadioItems(['Candlesticks', 'Close'], 'Close', id='main_chart', labelStyle={'display': 'block'}),
						]),
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Overlays', children=[
							dcc.Checklist(['SMA 10', 'SMA 20', 'SMA 50', 'SMA 100', 'SMA 200', 'EMA 10', 'EMA 20', 'EMA 50', 'EMA 100', 'EMA 200', 'Bollinger'], id='overlays', labelStyle={'display': 'block'}),
						]),
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Oscillator 1', children=[
							dcc.RadioItems(['Volume', 'MACD', 'RSI', 'Stochastic', 'SMA Ratios', 'EMA Ratios', 'Williams %R', 'CCI', 'Aroon'], 'RSI', id='oscillator1', labelStyle={'display': 'block'}),
						]),
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Oscillator 2', children=[
							dcc.RadioItems(['Volume', 'MACD', 'RSI', 'Stochastic', 'SMA Ratios', 'EMA Ratios', 'Williams %R', 'CCI', 'Aroon'], 'MACD' , id='oscillator2', labelStyle={'display': 'block'}),
						]),
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Signals', children=[
							dcc.Checklist(['SMA 10/50', 'SMA 20/100', 'SMA 50/200', 'EMA 10/50', 'EMA 20/100', 'EMA 50/200', 'MACD', 'RSI', 'Bollinger', 'Stochastic', 'Williams %R', 'CCI', 'Aroon'], id='signals', labelStyle={'display': 'block'}),
						]),
					),
					dbc.NavItem(
						dbc.DropdownMenu(label='Candlestick Patterns', children=[
							dcc.Checklist(['White Marubozu', 'Black Marubozu', 
								'Bullish Engulfing', 'Bearish Engulfing', 'Bullish Harami', 'Bearish Harami', 'Tweezer Bottom', 'Tweezer Top', 'Piercing Line', 'Dark Cloud Cover', 
								'Morning Star', 'Evening Star', 'Three White Soldiers', 'Three Black Crows',
								'Three Inside Up', 'Three Inside Down', 'Three Outside Up', 'Three Outside Down',
								'Upside Tasuki Gap', 'Downside Tasuki Gap'], id='candlestick_patterns', labelStyle={'display': 'block'}),
						]),
					)			
				])
			])
		]),
		# IMPORT MODAL
		dbc.Modal([
			dbc.ModalHeader('Import new dataset'),
			dbc.ModalBody([
				dbc.Input(placeholder='Type asset symbol', id='import_symbol'),
				html.Div([], id='import_message')
			]),
			dbc.ModalFooter([
				dbc.Button('Import', id='import_button', n_clicks=0),
				dbc.Button('Close', id='close_modal_button', n_clicks=0)
			]),
		], id='modal', is_open=False),
		# GRAPH
		dbc.Row([
			dbc.Col([
				dcc.Graph('graph')
			])
		]),
	], fluid=True)
)

@app.callback(
	Output('modal', 'is_open'),
	[Input('open_modal_button', 'n_clicks'),
	Input('close_modal_button', 'n_clicks')],
	[State('modal', 'is_open')],
	prevent_initial_call=True
)

def toggle_modal(n1, n2, is_open):
	if n1 or n2:
		return not is_open
	return is_open

@app.callback(
	Output('import_message', 'children'),
	[Input('import_button', 'n_clicks')],
	[State('import_symbol', 'value')],
	prevent_initial_call=True
)

def import_dataset(import_button, import_symbol):
	if type(import_symbol) == str:
		url = 'https://stooq.com/q/d/l/?s=' + import_symbol + '&i=d'
		csv_file = ('datasets/' + import_symbol + '.csv')
		urlretrieve(url, csv_file)
		avalaible_datasets.append(import_symbol)													# Updating list of datasets
		alert = dbc.Alert('{} imported'.format(str(import_symbol)), color='success', dismissable=True)
		return alert

@app.callback(
	Output('graph', 'figure'),
	Input('asset', 'value'),
	Input('date_range', 'value'),
	Input('main_chart', 'value'),
#	Input('overlays', 'value'),
#	Input('oscillator1', 'value'),
#	Input('oscillator2', 'value'),
#	Input('signals', 'value'),
#	Input('candlestick_patterns', 'value'),
	prevent_initial_call=False
)

def display_graph(asset, date_range, main_chart):												#, overlays, oscillator1, oscillator2, signals, candlestick_patterns):

	fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

	if asset is not None:

		df = pd.read_csv('datasets/' + asset + '.csv')
		columns = df.columns

		# X AXIS RANGE

		if date_range != 'Max':
			if date_range == '3M':
				delta = timedelta(days = 30)
			elif date_range == '6M':
				delta = timedelta(days = 180)
			elif date_range == '1Y':
				delta = timedelta(days = 365)
			elif date_range == '3Y':
				delta = timedelta(days = 3 * 365)

			end_date = df['Date'].iloc[-1]
			end_date_object = datetime.strptime(end_date, '%Y-%m-%d').date()
			start_date_object = end_date_object - delta
			start_date = start_date_object.strftime('%Y-%m-%d')

			fig.update_xaxes(range=[start_date, end_date])	

		# Y AXIS RANGE

			subset = df[(df['Date'] > start_date) & (df['Date'] < end_date)]

			main_chart_max = subset['Close'].max() * 1.05
			main_chart_min = subset['Close'].min() * 0.95

			fig.update_yaxes(range=[main_chart_min, main_chart_max], row=1, col=1)

		# MAIN CHART
		if main_chart == 'Candlesticks':
			fig.add_trace(go.Candlestick(
				x=df['Date'],
				open=df['Open'],
				high=df['High'],
				low=df['Low'],
				close=df['Close'],
				increasing_line_color='black',
				decreasing_line_color='black',
				increasing_fillcolor='white',
				decreasing_fillcolor='black',
				increasing_line_width=1,
				decreasing_line_width=1,
				showlegend=False,
			), row=1, col=1)
		elif main_chart == 'Close':
			fig.add_trace(go.Scatter(x=df['Date'], y=df['Close'], name='Close Price'), row=1, col=1)

		'''

		# OVERLAYS
		if type(overlays) == list:		
			if 'SMA 10' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 10'], name='SMA 10'), row=1, col=1)
			if 'SMA 20' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 20'], name='SMA 20'), row=1, col=1)
			if 'SMA 50' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 50'], name='SMA 50'), row=1, col=1)
			if 'SMA 100' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 100'], name='SMA 100'), row=1, col=1)
			if 'SMA 200' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 200'], name='SMA 200'), row=1, col=1)
			if 'EMA 10' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 10'], name='EMA 10'), row=1, col=1)
			if 'EMA 20' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 20'], name='EMA 20'), row=1, col=1)
			if 'EMA 50' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 50'], name='EMA 50'), row=1, col=1)
			if 'EMA 100' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 100'], name='EMA 100'), row=1, col=1)
			if 'EMA 200' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 200'], name='EMA 200'), row=1, col=1)
			if 'Bollinger' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Upper band'], name='Upper band'), row=1, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Lower band'], name='Lower band'), row=1, col=1)

		# OSCILLATORS
		def oscillator_update(oscillator_number, row_number):
			if oscillator_number == 'Volume':
				fig.add_trace(go.Bar(x=df['Date'], y=df['Volume'], name='Volume'), row=row_number, col=1)
				fig.update_yaxes(title_text='Volume', row=row_number, col=1)
			elif oscillator_number == 'MACD':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD'], line_color='blue', name='MACD'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['MACD Signal Line'], line_color='red', name='MACD Signal Line'), row=row_number, col=1)
				fig.add_trace(go.Bar(x=df['Date'], y=df['MACD Histogram'], name='MACD Histogram'), row=row_number, col=1)
				fig.update_yaxes(title_text='MACD', row=row_number, col=1)
				if date_range != 'Max':
					subset_max = subset['MACD'].max()
					subset_min = subset['MACD'].min()
					fig.update_yaxes(range=[subset_min, subset_max], row=row_number, col=1)
			elif oscillator_number == 'RSI':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['RSI'], line_color='blue', name='RSI'), row=row_number, col=1)
				fig.update_yaxes(title_text='RSI', tickvals=[30, 70], row=row_number, col=1)
			elif oscillator_number == 'Stochastic':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Stochastic %K'], name='Stochastic %K'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Stochastic %D'], name='Stochastic %D'), row=row_number, col=1)
				fig.update_yaxes(title_text='Stochastic', tickvals=[20, 80], row=row_number, col=1)
			elif oscillator_number == 'SMA Ratios':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 5/20 ratio'], name='SMA 5/20 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 10/50 ratio'], name='SMA 10/50 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 20/100 ratio'], name='SMA 20/100 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 50/200 ratio'], name='SMA 50/200 ratio'), row=row_number, col=1)
				fig.update_yaxes(title_text='SMA Ratios', row=row_number)
			elif oscillator_number == 'EMA Ratios':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 5/20 ratio'], name='EMA 5/20 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 10/50 ratio'], name='EMA 10/50 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 20/100 ratio'], name='EMA 20/100 ratio'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 50/200 ratio'], name='EMA 50/200 ratio'), row=row_number, col=1)
				fig.update_yaxes(title_text='EMA Ratios', row=row_number)
			elif oscillator_number == 'Williams %R':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Williams %R'], name='Williams %R'), row=row_number, col=1)
				fig.update_yaxes(title_text='Williams %R', row=row_number)
			elif oscillator_number == 'CCI':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['CCI'], name='CCI'), row=row_number, col=1)
				fig.update_yaxes(title_text='CCI', tickvals=[-100, 0, 100], row=row_number)
			elif oscillator_number == 'Aroon':
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Aroon Up'], name='Aroon Up'), row=row_number, col=1)
				fig.add_trace(go.Scatter(x=df['Date'], y=df['Aroon Down'], name='Aroon Down'), row=row_number, col=1)
				fig.update_yaxes(title_text='Aroon', row=row_number)

		oscillator_update(oscillator1, 2)
		oscillator_update(oscillator2, 3)

		# SIGNALS
		def show_signals(signal_type):
			df_slice = df.loc[df[signal_type + ' Signal'] == 1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Typical price'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='green', symbol='triangle-up', size=10), name=signal_type)) 
			df_slice = df.loc[df[signal_type + ' Signal'] == -1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Typical price'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='red', symbol='triangle-down', size=10), name=signal_type)) 

		if type(signals) == list:
			for signal in signals:
				show_signals(signal)

		# CANDLESTICK PATTERS
		def show_candlestick_patterns(pattern):
			df_slice = df.loc[df[pattern] == 1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Typical price'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='green', symbol='circle', size=10), name=pattern)) 
			df_slice = df.loc[df[pattern] == -1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Typical price'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='red', symbol='circle', size=10), name=pattern)) 

		if type(signals) == list:
			for pattern in candlestick_patterns:
				show_candlestick_patterns(pattern)

		'''

		# OTHER FORMATTING

		fig.update_xaxes(
			showline=True, linewidth=2, linecolor='gray', mirror=True, 
			gridcolor='white')
		fig.update_yaxes(
			showline=True, linewidth=2, linecolor='gray', mirror=True, 
			gridcolor='white',
			zeroline=True, zerolinewidth=1, zerolinecolor='gray')

		fig.update_xaxes(showticklabels=True, row=1, col=1)
		fig.update_xaxes(showticklabels=True, row=2, col=1)

		fig.update_layout(
			height=800,
			margin_t=10, margin_l=10, margin_r=20, margin_b=20, 
			paper_bgcolor='white', plot_bgcolor='whitesmoke',
			xaxis_rangeslider_visible=False,
			showlegend=False
		)

	return fig


if __name__ == '__main__':
	app.run_server(debug=True, use_reloader=True)

