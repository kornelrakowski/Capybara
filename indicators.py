import pandas as pd
import numpy as np

''' Every function in this package accepts pandas Series as input or inputs, parameters and returns pandas Series as output/outputs '''

def simple_moving_average(close_price, period):
	return close_price.rolling(period).mean()

def exponential_moving_average(close_price, period):
	return close_price.ewm(span=period, min_periods=period, adjust=False).mean()

def bollinger(high_price, low_price, close_price):
	typical_price = (high_price + low_price + close_price) / 3
	standard_deviation = typical_price.rolling(20).std()
	sma = simple_moving_average(close_price, 20)
	upper_band = sma + 2 * standard_deviation
	lower_band = sma - 2 * standard_deviation

	return upper_band, lower_band

def relative_strength_index(close_price, period=14):

	upward_change = np.select(
		[close_price > close_price.shift(1)],
		[close_price - close_price.shift(1)]
	)
	downward_change = np.select(
		[close_price < close_price.shift(1)],
		[close_price.shift(1) - close_price]
	)

#	df.loc[df['Close'] > df['Close'].shift(1), 'Upward change'] = close_price - close_price.shift(1)
#	df.loc[df['Close'] <= df['Close'].shift(1), 'Upward change'] = 0
#	df.loc[df['Close'] < df['Close'].shift(1), 'Downward change'] = close_price.shift(1) - close_price
#	df.loc[df['Close'] >= df['Close'].shift(1), 'Downward change'] = 0

	upward_SMMA = pd.Series(upward_change).ewm(alpha=1/period).mean()
	downward_SMMA = pd.Series(downward_change).ewm(alpha=1/period).mean()
	relative_strength = upward_SMMA / downward_SMMA	
	rsi = 100 - (100 / (1+ relative_strength))

	return rsi

	'''

	upward_SMMA = df['Upward change'].ewm(alpha=1/14).mean()
	downward_SMMA = df['Downward change'].ewm(alpha=1/14).mean()
	relative_strength = upward_SMMA / downward_SMMA
	rsi = 100 - (100 / (1+ relative_strength))
	df['RSI'] = rsi
	'''

def moving_average_convergence_divergence(close_price, slow_ma_period=26, fast_ma_period=12, macd_ma_period=9):
	slow_ma = close_price.ewm(alpha=2/slow_ma_period).mean()
	fast_ma = close_price.ewm(alpha=2/fast_ma_period).mean()

	macd = fast_ma - slow_ma
	macd_signal_line = macd.ewm(alpha=2/macd_ma_period).mean()
	macd_histogram = macd - macd_signal_line

	return macd, macd_signal_line, macd_histogram

def stochastic(high_price, low_price, close_price):
	stochastic_k = ((close_price - low_price.rolling(10).min()) / (high_price.rolling(10).max() - low_price.rolling(10).min())) * 100
	stochastic_d = stochastic_k.rolling(3).mean()

	return stochastic_k, stochastic_d

def williams_r(high_price, low_price, close_price, period=14):
	williams = (high_price.rolling(14).max() - close_price) / (high_price.rolling(14).max() - low_price.rolling(14).min()) * -100
	return williams

def commodity_channel_index(high_price, low_price, close_price):
	typical_price = (high_price + low_price + close_price) / 3
	cci = ( typical_price - typical_price.rolling(20).mean() ) / ( abs(typical_price - typical_price.rolling(20).mean()).mean() * 0.015 )
	return cci	

def aroon(high_price, low_price):
	aroon_up = 100 * high_price.rolling(25 + 1).apply(lambda x: x.argmax()) / 25
	aroon_down = 100 * low_price.rolling(25 + 1).apply(lambda x: x.argmin()) / 25

	return aroon_up, aroon_down