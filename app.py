from dash import Dash, dcc, html, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from urllib.request import urlretrieve
from datetime import datetime, timedelta
import os
import pandas as pd
import numpy as np

import indicators
import signals
import candlestick_patterns

path = 'datasets/'
if not os.path.exists(path):
	os.makedirs(path)

def list_datasets():
	datasets = os.listdir(path)
	assets = []
	for dataset in datasets:
		assets.append(dataset.replace('.csv',''))
	return sorted(assets)

avalaible_datasets = list_datasets()													# Initial creating list of datasets

all_indicators = ['SMA 5', 'SMA 10', 'SMA 20', 'SMA 50', 'SMA 100', 'SMA 200', 
	'EMA 5', 'EMA 10', 'EMA 20', 'EMA 50', 'EMA 100', 'EMA 200', 
	'Bollinger', 'MACD', 'RSI', 'Stochastic', 'Williams %R', 'CCI', 'Aroon']

all_overlays = ['SMA 5', 'SMA 10', 'SMA 20', 'SMA 50', 'SMA 100', 'SMA 200', 'EMA 5', 'EMA 10', 'EMA 20', 'EMA 50', 'EMA 100', 'EMA 200', 'Bollinger']
all_oscillators = ['Volume', 'MACD', 'RSI', 'Stochastic', 'Williams %R', 'CCI', 'Aroon']
all_signals = [
	'Crossover SMA 5/20', 'Crossover SMA 10/50', 'Crossover SMA 20/100', 'Crossover SMA 50/200', 'MACD', 'RSI', 'Bollinger', 'Stochastic', 'Williams %R', 'CCI', 'Aroon']
all_candlestick_patterns = ['White Marubozu', 'Black Marubozu', 
	'Bullish Engulfing', 'Bearish Engulfing', 'Bullish Harami', 'Bearish Harami', 'Tweezer Bottom', 'Tweezer Top', 'Piercing Line', 'Dark Cloud Cover', 
	'Morning Star', 'Evening Star', 'Three White Soldiers', 'Three Black Crows',
	'Three Inside Up', 'Three Inside Down', 'Three Outside Up', 'Three Outside Down',
	'Upside Tasuki Gap', 'Downside Tasuki Gap']

nav_items = [
	dbc.NavItem([
		dbc.Button('+', id='open_offcanvas_button', n_clicks=0),
	]),
	dbc.NavItem([
		dbc.Button('Import', id='open_modal_button', n_clicks=0),
	]),
	dbc.NavItem([
		dcc.Dropdown(avalaible_datasets, id='asset'),
	], style={'width': 100}),
	dbc.NavItem(
		dbc.DropdownMenu(label='Range', children=[
			dcc.RadioItems(['3M', '6M', '1Y', '3Y', 'Max'], 'Max', id='date_range', labelStyle={'display': 'block'}),
		], id='range_dropdown'),						
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Main chart', children=[
			dcc.RadioItems(['Candlesticks', 'Close'], 'Close', id='main_chart', labelStyle={'display': 'block'}),
		], id='main_chart_dropdown'),
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Overlays', children = [
			dcc.Checklist(options=[], id='overlays', labelStyle={'display': 'block'})
		], id='overlays_dropdown'),
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Oscillator 1', children = [
			dcc.RadioItems(options=[], value='Volume', id='oscillator1', labelStyle={'display': 'block'})
		], id='oscillator1_dropdown'),
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Oscillator 2', children = [
			dcc.RadioItems(options=[], value='MACD' , id='oscillator2', labelStyle={'display': 'block'})
		], id='oscillator2_dropdown'),
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Signals', children = [
			dcc.Checklist(options=[], id='signals', labelStyle={'display': 'block'})
		], id='signals_dropdown'),
	),
	dbc.NavItem(
		dbc.DropdownMenu(label='Candlestick Patterns', children = [
			dcc.Checklist(options=[], id='candlestick_patterns', labelStyle={'display': 'block'})
		], id='candlestick_patterns_dropdown'),
	)			
]

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions = True)

app.layout = html.Div(
	dbc.Container([
		dbc.Row([
			dbc.Col([
				dbc.Nav(
					nav_items
				)
			])
		]),
		dbc.Modal([
			dbc.ModalHeader('Import new dataset'),
			dbc.ModalBody([
				dbc.Input(placeholder='Type asset symbol (e.g. "KGH")', id='import_symbol'),
				html.Div([], id='import_message'),
			]),
			dbc.ModalFooter([
				dbc.Button('Import', id='import_button', n_clicks=0),
				dbc.Button('Close', id='close_modal_button', n_clicks=0)
			]),
		], id='modal', is_open=False),
		dbc.Offcanvas(
			html.Div([
				html.H5('Select assets'),
				dcc.Dropdown(options=avalaible_datasets, value=[], id='assets_dropdown', multi=True),
				dcc.Checklist(options=['Select All'], value=[], id='select_all_assets'),

				html.H5('Select indicators'),
				dcc.Dropdown(options=all_indicators, value=[], id='indicators_dropdown', multi=True),
				dcc.Checklist(options=['Select All'], value=[], id='select_all_indicators'),

				dbc.Button('Calculate indicators', id='calculate_indicators_button', n_clicks=0),
				html.Div([], id='calculate_indicators_message'),

				html.H5('Select candlestick patterns'),
				dcc.Dropdown(options=all_candlestick_patterns, value=[], id='select_candlestick_patterns_dropdown', multi=True),
				dcc.Checklist(options=['Select All'], value=[], id='select_all_candlestick_patterns'),

				dbc.Button('Find candlestick patterns', id='find_candlestick_patterns_button', n_clicks=0),
				html.Div([], id='find_candlestick_patterns_message'),

				html.H5('Select signals'),
				dcc.Dropdown(options=all_signals, value=[], id='select_signals_dropdown', multi=True),
				dcc.Checklist(options=['Select All'], value=[], id='select_all_signals'),

				dbc.Button('Find signals', id='find_signals_button', n_clicks=0),
				html.Div([], id='find_signals_message'),

			]),
			id='offcanvas',
			title='Data',
			is_open=False
		),
		dbc.Row([
			dbc.Col([
				dcc.Graph('graph')
			])
		]),
	], fluid=True)
)

''' Disable dropdowns if asset is not selected '''
@app.callback(
	Output('range_dropdown', 'disabled'),
	Output('main_chart_dropdown', 'disabled'),
	Output('overlays_dropdown', 'disabled'),
	Output('oscillator1_dropdown', 'disabled'),
	Output('oscillator2_dropdown', 'disabled'),
	Output('signals_dropdown', 'disabled'),
	Output('candlestick_patterns_dropdown', 'disabled'),
	Input('asset', 'value')
)

def disable_nav_items(asset):
	if asset:
		disabled = False
	else:
		disabled = True
	return disabled, disabled, disabled, disabled, disabled, disabled, disabled

''' Update DropdownMenus in NavBar '''
@app.callback(
	Output('overlays', 'options'),
	Output('oscillator1', 'options'),
	Output('oscillator2', 'options'),
	Output('signals', 'options'),
	Output('candlestick_patterns', 'options'),
	Input('asset', 'value')
)

def update_dropdown(asset):
	if asset:
		df = pd.read_csv(f'datasets/{asset}.csv')
		columns = df.columns

		avalaible_overlays = [item for item in all_overlays if item in columns]
		if ('Upper band' in columns) and ('Lower band' in columns):
			avalaible_overlays.append('Bollinger')

		avalaible_oscillators = [item for item in all_oscillators if item in columns]
		if ('Stochastic %K' in columns) and ('Stochastic %D' in columns):
			avalaible_oscillators.append('Stochastic')
		if ('Aroon Up' in columns) and ('Aroon Down' in columns):
			avalaible_oscillators.append('Aroon')

		avalaible_signals = [item for item in all_signals if f'{item} Signal' in columns]

		avalaible_candlestick_patterns = [item for item in all_candlestick_patterns if item in columns]

		return avalaible_overlays, avalaible_oscillators, avalaible_oscillators, avalaible_signals, avalaible_candlestick_patterns
	else:
		return [], [], [], [], []
	
''' Toggle offcanvas '''
@app.callback(
	Output('offcanvas', 'is_open'),
	Input('open_offcanvas_button', 'n_clicks'),
	State('offcanvas', 'is_open'),
	prevent_initial_call=True
)

def toggle_offcanvas(n1, is_open):
	if n1:
		return not is_open
	return is_open

''' Selecting all assets in dropdown '''
@app.callback(
	Output('assets_dropdown', 'value'),
	Input('select_all_assets', 'value'),
	State('assets_dropdown', 'options'),
)

def select_all(selected, options):
	if 'Select All' in selected:
		return options

''' Selecting all indicators in dropdown '''
@app.callback(
	Output('indicators_dropdown', 'value'),
	Input('select_all_indicators', 'value'),
	State('indicators_dropdown', 'options'),
)

def select_all(selected, options):
	if 'Select All' in selected:
		return options

''' Selecting all candlestick patterns in dropdown '''
@app.callback(
	Output('select_candlestick_patterns_dropdown', 'value'),
	Input('select_all_candlestick_patterns', 'value'),
	State('select_candlestick_patterns_dropdown', 'options'),
)

def select_all(selected, options):
	if 'Select All' in selected:
		return options

''' Selecting all signals in dropdown '''
@app.callback(
	Output('select_signals_dropdown', 'value'),
	Input('select_all_signals', 'value'),
	State('select_signals_dropdown', 'options'),
)

def select_all(selected, options):
	if 'Select All' in selected:
		return options

''' Calculating technical indicators '''

@app.callback(
	Output('calculate_indicators_message', 'children'),
	Input('calculate_indicators_button', 'n_clicks'),
	State('assets_dropdown', 'value'),
	State('indicators_dropdown', 'value'),
	prevent_initial_call=True
)

def calculate_indicators(button, selected_assets, selected_indicators):

	for asset in selected_assets:

		df = pd.read_csv(f'datasets/{asset}.csv')

		open_price = df['Open']
		high_price = df['High']
		low_price = df['Low']
		close_price = df['Close']

		selected_SMA = [element for element in selected_indicators if 'SMA ' in element]
		periods = [element.split(' ')[1] for element in selected_SMA]
		for period in periods:
			df[f'SMA {period}'] = indicators.simple_moving_average(close_price, int(period))

		selected_EMA = [element for element in selected_indicators if 'EMA ' in element]
		periods = [element.split(' ')[1] for element in selected_EMA]
		for period in periods:
			df[f'EMA {period}'] = indicators.exponential_moving_average(close_price, int(period))

		if 'Bollinger' in selected_indicators:
			df['Upper band'], df['Lower band'] = indicators.bollinger(high_price, low_price, close_price)

		if 'RSI' in selected_indicators:
			df['RSI'] = indicators.relative_strength_index(close_price)

		if 'MACD' in selected_indicators:
			df['MACD'], df['MACD Signal Line'], df['MACD Histogram'] = indicators.moving_average_convergence_divergence(close_price)

		if 'Stochastic' in selected_indicators:
			df['Stochastic %K'], df['Stochastic %D'] = indicators.stochastic(high_price, low_price, close_price)

		if 'Williams %R' in selected_indicators:
			df['Williams %R'] = indicators.williams_r(high_price, low_price, close_price)

		if 'CCI' in selected_indicators:
			df['CCI'] = indicators.commodity_channel_index(high_price, low_price, close_price)

		if 'Aroon' in selected_indicators:
			df['Aroon Up'], df['Aroon Down'] = indicators.aroon(high_price, low_price)

		df.to_csv(f'datasets/{asset}.csv', index=False)

	alert = dbc.Alert('Succes', color='success', dismissable=True)
	return alert

''' Finding candlestick patterns '''

@app.callback(
	Output('find_candlestick_patterns_message', 'children'),
	Input('find_candlestick_patterns_button', 'n_clicks'),
	State('assets_dropdown', 'value'),
	State('select_candlestick_patterns_dropdown', 'value'),
	prevent_initial_call=True
)

def find_candlestick_patterns(button, selected_assets, selected_candlestick_patterns):

	for asset in selected_assets:

		df = pd.read_csv(f'datasets/{asset}.csv')

		open_price = df['Open']
		high_price = df['High']
		low_price = df['Low']
		close_price = df['Close']

		for pattern in selected_candlestick_patterns:
			df[pattern] = candlestick_patterns.find_pattern(open_price, high_price, low_price, close_price, pattern)

		df.to_csv(f'datasets/{asset}.csv', index=False)

	alert = dbc.Alert('Succes', color='success', dismissable=True)
	return alert

''' Finding singnals '''

@app.callback(
	Output('find_signals_message', 'children'),
	Input('find_signals_button', 'n_clicks'),
	State('assets_dropdown', 'value'),
	State('select_signals_dropdown', 'value'),
	prevent_initial_call=True
)

def find_signals(button, selected_assets, selected_signals):

	for asset in selected_assets:

		df = pd.read_csv(f'datasets/{asset}.csv')
		
		close_price = df['Close']

		'''
		'Crossover SMA 5/20', 'Crossover SMA 10/50', 'Crossover SMA 20/100', 'Crossover SMA 50/200'

		selected_EMA = [element for element in selected_indicators if 'EMA ' in element]
		periods = [element.split(' ')[1] for element in selected_EMA]
		for period in periods:
			df[f'EMA {period}'] = indicators.exponential_moving_average(close_price, int(period))
		'''

		selected_ma_crossovers = [element for element in selected_signals if 'Crossover SMA' in element]
		periods = [element.split(' ')[2] for element in selected_ma_crossovers]
		for period in periods:
			fast_and_slow = period.split('/')
			fast_ma = df[f'SMA {fast_and_slow[0]}']
			slow_ma = df[f'SMA {fast_and_slow[1]}']
		
			df[f'Crossover SMA {period} Signal'] = signals.moving_average_crossover(fast_ma, slow_ma)



		if 'RSI' in selected_signals:
			df['RSI Signal'] = signals.relative_strength_index(close_price, df['RSI'])

		if 'MACD' in selected_signals:
			df['MACD Signal'] = signals.moving_average_convergence_divergence(df['MACD Histogram'])

		if 'Bollinger' in selected_signals:
			df['Bollinger Signal'] = signals.bollinger(close_price, df['Upper band'], df['Lower band'])

		if 'Stochastic' in selected_signals:
			df['Stochastic Signal'] = signals.stochastic(df['Stochastic %D'])

		if 'Williams %R' in selected_signals:
			df['Williams %R Signal'] = signals.williams_r(df['Williams %R'])

		if 'CCI' in selected_signals:
			df['CCI Signal'] = signals.commodity_channel_index(df['CCI'])

		if 'Aroon' in selected_signals:
			df['Aroon Signal'] = signals.aroon(df['Aroon Up'], df['Aroon Down'])

		df.to_csv(f'datasets/{asset}.csv', index=False)

	alert = dbc.Alert('Succes', color='success', dismissable=True)
	return alert

''' Toggle modal '''
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

''' Import dataset '''
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
	Input('overlays', 'value'),
	Input('oscillator1', 'value'),
	Input('oscillator2', 'value'),
	Input('signals', 'value'),
	Input('candlestick_patterns', 'value'),
	prevent_initial_call=True
)

def display_graph(asset, date_range, main_chart, overlays, oscillator1, oscillator2, signals, candlestick_patterns):

	fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

	if asset is not None:

		df = pd.read_csv('datasets/' + asset + '.csv')

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

		# OVERLAYS
		if type(overlays) == list:		
			if 'SMA 5' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 5'], name='SMA 5'), row=1, col=1)
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
			if 'EMA 5' in overlays:
				fig.add_trace(go.Scatter(x=df['Date'], y=df['EMA 5'], name='EMA 5'), row=1, col=1)
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
				fig.add_trace(go.Scatter(x=df['Date'], y=df['SMA 20'], name='SMA 20'), row=1, col=1)


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

		if oscillator1:
			oscillator_update(oscillator1, 2)
		if oscillator2:
			oscillator_update(oscillator2, 3)

		# SIGNALS
		def show_signals(signal_type):
			df_slice = df.loc[df[signal_type + ' Signal'] == 1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Close'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='green', symbol='triangle-up', size=10), name=signal_type)) 
			df_slice = df.loc[df[signal_type + ' Signal'] == -1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Close'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='red', symbol='triangle-down', size=10), name=signal_type)) 

		if type(signals) == list:
			for signal in signals:
				show_signals(signal)

		# CANDLESTICK PATTERS
		def show_candlestick_patterns(pattern):
			df_slice = df.loc[df[pattern] == 1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Close'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='green', symbol='circle', size=10), name=pattern)) 
			df_slice = df.loc[df[pattern] == -1]
			x_list = df_slice['Date'].to_list()
			y_list = df_slice['Close'].to_list()
			fig.add_trace(go.Scatter(x=x_list, y=y_list, mode='markers', marker=dict(color='red', symbol='circle', size=10), name=pattern)) 

		if type(candlestick_patterns) == list:
			for pattern in candlestick_patterns:
				show_candlestick_patterns(pattern)

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

		# Removing empty dates from X axis            ! NEED RUN FASTER
	#	dt_all = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1])
	#	dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df['Date'])]
	#	dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
	#	fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])