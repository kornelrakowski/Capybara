from dash import Dash, dcc, html, Input, Output, State
import dash
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc

from datetime import datetime, timedelta
from urllib.request import urlretrieve
import pandas as pd
import os

def list_datasets():
	datasets = os.listdir('datasets/')
	assets = []
	for dataset in datasets:
		assets.append(dataset.replace('.csv',''))
	return sorted(assets)

assets = list_datasets()
print(assets)

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions = True)

if len(assets) != 0:
	assets_dropdown = dbc.DropdownMenu(label='Assets', children=[
		dcc.RadioItems(assets, assets[0], id='asset', labelStyle={'display': 'block'}),
	])
else:
	assets_dropdown = dbc.DropdownMenu(label='Assets', disabled=True, children=[
		dcc.RadioItems(assets, id='asset', labelStyle={'display': 'block'}),
	])	

app.layout = html.Div(
	dbc.Container([
		dbc.Row([
			dbc.Col([
				dbc.Nav([
					dbc.NavItem(
						dbc.Button("Options", id="open-offcanvas", n_clicks=0)
					),
					dbc.NavItem(
						assets_dropdown,
					),
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
					),
				])
			])
		]),
		dbc.Offcanvas(
			html.Div([
				dbc.Row([
					html.H5('Import new dataset'),
					dbc.Input(placeholder='asset symbol', id='import_symbol'),
					dbc.Button('Import', id='import_button', n_clicks=0),
					html.Div([], id='import_message')
				]),
				dbc.Row([
					html.H5('Technical Indicators'),
					dbc.DropdownMenu(label='Select assets', children=[
						dcc.Checklist(assets, id='set_of_assets', labelStyle={'display': 'block'}),
					]),
					dbc.DropdownMenu(label='Select modules', children=[
						dcc.Checklist(['Technical Indicators', 'Signals', 'Candlestick Patterns'], id='set_of_modules', labelStyle={'display': 'block'}),
					]),
					dbc.Button('Generate', id='generate_button', n_clicks=0),
					html.Div([], id='generate_message')
				]),
			]),
			id='offcanvas',
			title='Options',
			is_open=False,
		),
		dbc.Row([
			dbc.Col([
				dcc.Graph('graph')
			])
		]),
	], fluid=True)
)

@app.callback(
	Output("offcanvas", "is_open"),
	Input("open-offcanvas", "n_clicks"),
	State("offcanvas", "is_open"),
)

def toggle_offcanvas(n1, is_open):
	if n1:
		return not is_open
	return is_open

@app.callback(
	Output('import_message', 'children'),
	Input('import_button', 'n_clicks'),
	State('import_symbol', 'value'),
)

def import_dataset(import_button, import_symbol):
	if type(import_symbol) == str:
		url = 'https://stooq.com/q/d/l/?s=' + import_symbol + '&i=d'
		csv_file = ('datasets/' + import_symbol + '.csv')
		urlretrieve(url, csv_file)
		alert = dbc.Alert('{} imported'.format(str(import_symbol)), color='success', dismissable=True)
		return alert

@app.callback(
	Output('generate_message', 'children'),
	Input('generate_button', 'n_clicks'),
	State('set_of_assets', 'value'),
	State('set_of_modules', 'value'),
)

def generate(generate_button, set_of_assets, set_of_modules):
	if (type(set_of_modules) == list) and (type(set_of_assets) == list):

		print('Selected modules: {}'.format(set_of_modules))
		print('Selected assets: {}'.format(set_of_assets))

		for asset in set_of_assets:

			print(asset)

			df = pd.read_csv('datasets/' + asset + '.csv')

			df['Typical price'] = ( df['High'] + df['Low'] + df['Close'] ) / 3

			if 'Technical Indicators' in set_of_modules:

				# SMA
				periods = [10, 20, 50, 100, 200]
				for period in periods:
					df['SMA ' + str(period)] = df['Close'].rolling(period).mean()

				df['SMA 10/50 ratio'] = df['SMA 10'] / df['SMA 50']
				df['SMA 20/100 ratio'] = df['SMA 20'] / df['SMA 100']		
				df['SMA 50/200 ratio'] = df['SMA 50'] / df['SMA 200']

				# EMA
				periods = [10, 20, 50, 100, 200]
				for period in periods:
					df['EMA ' + str(period)] = df['Close'].ewm(span=period, min_periods=period, adjust=False).mean()

				df['EMA 10/50 ratio'] = df['EMA 10'] / df['EMA 50']
				df['EMA 20/100 ratio'] = df['EMA 20'] / df['EMA 100']
				df['EMA 50/200 ratio'] = df['EMA 50'] / df['EMA 200']

				# Bollinger
				standard_deviation = df['Typical price'].rolling(20).std()
				df['Upper band'] = df['SMA 20'] + 2*standard_deviation
				df['Lower band'] = df['SMA 20'] - 2*standard_deviation
				df['Percent_b'] = (df['Close'] - df['Lower band']) / (df['Upper band'] - df['Lower band'])
				df['Bandwidth'] = (df['Upper band'] - df['Lower band']) / df['SMA 20']

				# RSI
				df.loc[df['Close'] > df['Close'].shift(1), 'Upward change'] = df['Close'] - df['Close'].shift(1)
				df.loc[df['Close'] <= df['Close'].shift(1), 'Upward change'] = 0
				df.loc[df['Close'] < df['Close'].shift(1), 'Downward change'] = df['Close'].shift(1) - df['Close']
				df.loc[df['Close'] >= df['Close'].shift(1), 'Downward change'] = 0
				upward_SMMA = df['Upward change'].ewm(alpha=1/14).mean()
				downward_SMMA = df['Downward change'].ewm(alpha=1/14).mean()
				relative_strength = upward_SMMA / downward_SMMA
				rsi = 100 - (100 / (1+ relative_strength))
				df['RSI'] = rsi

				# MACD
				EMA_26 = df['Close'].ewm(alpha=2/26).mean()
				EMA_12 = df['Close'].ewm(alpha=2/12).mean()
				df['MACD'] = EMA_12 - EMA_26
				df['MACD Signal Line'] = df['MACD'].ewm(alpha=2/9).mean()
				df['MACD Histogram'] = df['MACD'] - df['MACD Signal Line']

				# Stochastic
				df['Stochastic %K'] = ((df['Close'] - df['Low'].rolling(10).min()) / (df['High'].rolling(10).max() - df['Low'].rolling(10).min())) * 100
				df['Stochastic %D'] = df['Stochastic %K'].rolling(3).mean()
			
				# Williams %R
				df['Williams %R'] = ( df['High'].rolling(14).max() - df['Close']) / ( df['High'].rolling(14).max() - df['Low'].rolling(14).min()) * -100

				# CCI
				df['CCI'] = ( df['Typical price'] - df['Typical price'].rolling(20).mean() ) / ( abs(df['Typical price'] - df['Typical price'].rolling(20).mean()).mean() * 0.015 )

				# Aroon
				df['Aroon Up'] = 100 * df.High.rolling(25 + 1).apply(lambda x: x.argmax()) / 25
				df['Aroon Down'] = 100 * df.Low.rolling(25 + 1).apply(lambda x: x.argmin()) / 25

			df.to_csv('datasets/' + asset + '.csv', index=False)

		elif 'Signals' in set_of_modules:

			# Reading source file
			df = pd.read_csv('datasets/' + asset + '.csv')

			# Buy/sell signals
			df['SMA 10/50 Signal'] = np.select(
				[(df['SMA 10/50 ratio'] > 1) & (df['SMA 10/50 ratio'].shift(1) < 1), (df['SMA 10/50 ratio'] < 1) & (df['SMA 10/50 ratio'].shift(1) > 1)], 
				[1, -1])
			df['SMA 20/100 Signal'] = np.select(
				[(df['SMA 20/100 ratio'] > 1) & (df['SMA 20/100 ratio'].shift(1) < 1), (df['SMA 20/100 ratio'] < 1) & (df['SMA 20/100 ratio'].shift(1) > 1)], 
				[1, -1])
			df['SMA 50/200 Signal'] = np.select(
				[(df['SMA 50/200 ratio'] > 1) & (df['SMA 50/200 ratio'].shift(1) < 1), (df['SMA 50/200 ratio'] < 1) & (df['SMA 50/200 ratio'].shift(1) > 1)], 
				[1, -1])
			df['EMA 10/50 Signal'] = np.select(
				[(df['EMA 10/50 ratio'] > 1) & (df['EMA 10/50 ratio'].shift(1) < 1), (df['EMA 10/50 ratio'] < 1) & (df['EMA 10/50 ratio'].shift(1) > 1)], 
				[1, -1])
			df['EMA 20/100 Signal'] = np.select(
				[(df['EMA 20/100 ratio'] > 1) & (df['EMA 20/100 ratio'].shift(1) < 1), (df['EMA 20/100 ratio'] < 1) & (df['EMA 20/100 ratio'].shift(1) > 1)], 
				[1, -1])
			df['EMA 50/200 Signal'] = np.select(
				[(df['EMA 50/200 ratio'] > 1) & (df['EMA 50/200 ratio'].shift(1) < 1), (df['EMA 50/200 ratio'] < 1) & (df['EMA 50/200 ratio'].shift(1) > 1)], 
				[1, -1])
			df['MACD Signal'] = np.select(
				[(df['Trend 20'] > 1) & ((df['MACD Histogram']>0) & (df['MACD Histogram'].shift(1)<0)) , 
					(df['Trend 20'] < 1) & ((df['MACD Histogram']<0) & (df['MACD Histogram'].shift(1)>0))], 
				[1, -1])
			df['RSI Signal'] = np.select(
				[(df['Trend 20'] > 1) & (df['RSI'] > 40) & (df['RSI'].shift(1) < 40), 
					(df['Trend 20'] < 1) & (df['RSI'] < 60) & (df['RSI'].shift(1) > 60)], 
				[1, -1])
			df['Bollinger Signal'] = np.select(
				[(df['Close'] < df['Lower band']) & (df['Close'].shift(1) > df['Lower band'].shift(1)), 
					(df['Close'] > df['Upper band']) & (df['Close'].shift(1) < df['Upper band'].shift(1))], 
				[1, -1])
			df['Stochastic Signal'] = np.select(
				[(df['Trend 20'] > 1) & ((df['Stochastic %D']>20) & (df['Stochastic %D'].shift(1)<20)), 
					(df['Trend 20'] < 1) & ((df['Stochastic %D']<80) & (df['Stochastic %D'].shift(1)>80))],
				[1, -1])
			df['Williams %R Signal'] = np.select(
					[(df['Williams %R'] > -80) & (df['Williams %R'].shift(1) < -80), 
					(df['Williams %R'] < -20) & (df['Williams %R'].shift(1) > -20)],
				[1, -1])
			df['CCI Signal'] = np.select(
				[(df['CCI']>-100) & (df['CCI'].shift(1)<-100), 
					(df['CCI']<100) & (df['CCI'].shift(1)>100)],
				[1, -1])
			df['Aroon Signal'] = np.select(
				[(df['Trend 50'] > 1) & (df['Aroon Up'] > 70) & (df['Aroon Up'].shift(1) < 70), 
					(df['Trend 50'] < 1) & (df['Aroon Down'] > 70) & (df['Aroon Down'].shift(1) < 30)],
				[1, -1])

			df.to_csv('datasets/' + asset + '.csv', index=False)

		elif 'Candlestick Patterns' in set_of_modules:

			# Reading source file
			df = pd.read_csv('datasets/' + asset + '.csv')

			realbody = abs(df['Open'] - df['Close'])
			candle_range = df['High'] - df['Low']
			upper_shadow = df['High'] - df[['Close', 'Open']].max(axis=1)
			lower_shadow = df[['Close', 'Open']].min(axis=1) - df['Low']

			# TREND REVERSAL PATTERNS
			df['White Marubozu'] = np.where(
				(df['Close'] > df['Open']) &
				(df['Close'] == df['High']) &
				(df['Open'] == df['Low'])
			, 1, 0)
			df['Black Marubozu'] = np.where(
				(df['Close'] < df['Open']) &
				(df['Close'] == df['Low']) &
				(df['Open'] == df['High'])
			, -1, 0)

			df['Bullish Engulfing'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'] > df['Open']) &
				(df['Close'].shift(1) < df['Open'].shift(1)) &
				(df['Close'] > df['Open'].shift(1)) &
				(df['Open'] < df['Close'].shift(1))
			, 1, 0)
			df['Bearish Engulfing'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'] < df['Open']) &
				(df['Close'].shift(1) > df['Open'].shift(1)) &
				(df['Close'] < df['Open'].shift(1)) &
				(df['Open'] > df['Close'].shift(1))
			, -1, 0)
			df['Bullish Harami'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'] > df['Open']) &
				(df['Close'].shift(1) < df['Open'].shift(1)) &
				(df['Close'] < df['Open'].shift(1)) &
				(df['Open'] > df['Close'].shift(1))
			, 1, 0)
			df['Bearish Harami'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'] < df['Open']) &
				(df['Close'].shift(1) > df['Open'].shift(1)) &
				(df['Close'] > df['Open'].shift(1)) &
				(df['Open'] < df['Close'].shift(1))
			, -1, 0)
			df['Tweezer Bottom'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Open'] < df['Close']) &
				(df['Open'].shift(1) < df['Close'].shift(1)) &
				(df['Low'] == df['Low'].shift(1))
			, 1, 0)
			df['Tweezer Top'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Open'] > df['Close']) &
				(df['Open'].shift(1) > df['Close'].shift(1)) &
				(df['High'] == df['High'].shift(1))
			, -1, 0)
			df['Piercing Line'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'] > df['Open']) &
				(df['Close'].shift(1) < df['Open'].shift(1)) &
				(df['Open'] < df['Close'].shift(1)) &
				(df['Close'] > (df['Open'].shift(1) + df['Close'].shift(1))/2)
			, 1, 0)
			df['Dark Cloud Cover'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'] < df['Open']) &
				(df['Close'].shift(1) > df['Open'].shift(1)) &
				(df['Close'] > df['Open'].shift(1)) &
				(df['Close'] < (df['Open'].shift(1) + df['Close'].shift(1))/2)
			, -1, 0)

			df['Morning Star'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'].shift(2) < df['Open'].shift(2)) &
				(df['Close'] > df['Open']) &
				(df['Open'] > df[['Close', 'Open']].max(axis=1).shift(1)) &
				(df['Close'].shift(2) > df[['Close', 'Open']].max(axis=1).shift(1)) &
				(df['Close'] > (df['Close'].shift(2) + df['Open'].shift(2))/2)
			, 1, 0)
			df['Evening Star'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'].shift(2) > df['Open'].shift(2)) &
				(df['Close'] < df['Open']) &
				(df['Open'] < df[['Close', 'Open']].min(axis=1).shift(1)) &
				(df['Close'].shift(2) < df[['Close', 'Open']].min(axis=1).shift(1)) &
				(df['Close'] < (df['Close'].shift(2) + df['Open'].shift(2))/2)
			, -1, 0)
			df['Three White Soldiers'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'] > df['Open']) &
				(df['Close'].shift(1) > df['Open'].shift(1)) &
				(df['Close'].shift(2) > df['Open'].shift(2)) &
				(df['Close'] > df['Close'].shift(1)) &
				(df['Close'].shift(1) > df['Close'].shift(2)) &
				(df['Open'] > df['Open'].shift(1)) &
				(df['Open'].shift(1) > df['Open'].shift(2)) &
				(realbody > 0.8 * candle_range) &
				(realbody.shift(1) > 0.8 * candle_range.shift(1)) &
				(realbody.shift(2) > 0.8 * candle_range.shift(2)) &
				(df['Open'] < df['Close'].shift(1)) &
				(df['Open'].shift(1) < df['Close'].shift(2))
			, 1, 0)
			df['Three Black Crows'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'] < df['Open']) &
				(df['Close'].shift(1) < df['Open'].shift(1)) &
				(df['Close'].shift(2) < df['Open'].shift(2)) &
				(df['Close'] < df['Close'].shift(1)) &
				(df['Close'].shift(1) < df['Close'].shift(2)) &
				(df['Open'] < df['Open'].shift(1)) &
				(df['Open'].shift(1) < df['Open'].shift(2)) &
				(realbody > 0.8 * candle_range) &
				(realbody.shift(1) > 0.8 * candle_range.shift(1)) &
				(realbody.shift(2) > 0.8 * candle_range.shift(2)) &
				(df['Open'] < df['Close'].shift(1)) &
				(df['Open'].shift(1) < df['Close'].shift(2))
			, -1, 0)
			df['Three Inside Up'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Open'].shift(2) > df['Close'].shift(2)) &
				(df['Open'].shift(1) < df['Close'].shift(1)) &
				(df['Open'] < df['Close']) &
				(df['Close'].shift(1) < df['Open'].shift(2)) &
				(df['Close'].shift(2) < df['Open'].shift(1)) &
				(df['Close'] > df['Close'].shift(1)) &
				(df['Open'] > df['Open'].shift(1))
			,1 ,0)
			df['Three Inside Down'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Open'].shift(2) < df['Close'].shift(2)) &
				(df['Open'].shift(1) > df['Close'].shift(1)) &
				(df['Open'] > df['Close']) &
				(df['Close'].shift(1) > df['Open'].shift(2)) &
				(df['Close'].shift(2) > df['Open'].shift(1)) &
				(df['Close'] < df['Close'].shift(1)) &
				(df['Open'] < df['Open'].shift(1))
			,-1 ,0)
			df['Three Outside Up'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Open'].shift(2) > df['Close'].shift(2)) &
				(df['Open'].shift(1) < df['Close'].shift(1)) &
				(df['Open'] < df['Close']) &
				(df['Close'].shift(1) > df['Open'].shift(2)) &
				(df['Close'].shift(2) > df['Open'].shift(1)) &
				(df['Close'] > df['Close'].shift(1)) &
				(df['Open'] > df['Open'].shift(1))
			,1 ,0)
			df['Three Outside Down'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Open'].shift(2) < df['Close'].shift(2)) &
				(df['Open'].shift(1) > df['Close'].shift(1)) &
				(df['Open'] > df['Close']) &
				(df['Close'].shift(1) > df['Open'].shift(2)) &
				(df['Close'].shift(2) > df['Open'].shift(1)) &
				(df['Close'] < df['Close'].shift(1)) &
				(df['Open'] < df['Open'].shift(1))
			,-1 ,0)

			df['Upside Tasuki Gap'] = np.where(
				(df['Trend 20'] > 1) &
				(df['Close'].shift(2) > df['Open'].shift(2)) &
				(df['Close'].shift(1) > df['Open'].shift(1)) &
				(df['Open'] > df['Close']) &
				(df['Open'].shift(1) > df['Close'].shift(2)) &
				(df['Open'] > df['Open'].shift(1)) &
				(df['Close'] < df['Close'].shift(2)) &
				(df['Open'] < df['Close'].shift(1)) &
				(df['Close'] > df['Open'].shift(2))
			, 1, 0)
			df['Downside Tasuki Gap'] = np.where(
				(df['Trend 20'] < 1) &
				(df['Close'].shift(2) < df['Open'].shift(2)) &
				(df['Close'].shift(1) < df['Open'].shift(1)) &
				(df['Open'] < df['Close']) &
				(df['Open'].shift(1) < df['Close'].shift(2)) &
				(df['Open'] < df['Open'].shift(1)) &
				(df['Close'] > df['Close'].shift(2)) &
				(df['Open'] > df['Close'].shift(1)) &
				(df['Close'] < df['Open'].shift(2))
			, -1, 0)

			df.to_csv('datasets/' + asset + '.csv', index=False)

		alert = dbc.Alert('Modules executed: {}'.format(set_of_modules), color='success', dismissable=True)
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
)

def display_graph(asset, date_range, main_chart, overlays, oscillator1, oscillator2, signals, candlestick_patterns):

	if len(assets) != 0:

		df = pd.read_csv('datasets/' + asset + '.csv')

		columns = df.columns

		fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.03, row_heights=[0.6, 0.2, 0.2])

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

		for pattern in candlestick_patterns:
			show_candlestick_patterns(pattern)


		# Removing empty dates from X axis            ! NEED RUN FASTER
	#	dt_all = pd.date_range(start=df['Date'].iloc[0],end=df['Date'].iloc[-1])
	#	dt_obs = [d.strftime("%Y-%m-%d") for d in pd.to_datetime(df['Date'])]
	#	dt_breaks = [d for d in dt_all.strftime("%Y-%m-%d").tolist() if not d in dt_obs]
	#	fig.update_xaxes(rangebreaks=[dict(values=dt_breaks)])



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
