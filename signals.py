import pandas as pd
import numpy as np

def moving_average_crossover(fast_ma, slow_ma):
	signal = np.select(
		[(slow_ma < fast_ma) & (slow_ma.shift(1) > fast_ma.shift(1)),
		(slow_ma > fast_ma) & (slow_ma.shift(1) < fast_ma.shift(1))],
		[1, -1]
	)
	return signal

def relative_strength_index(close_price, rsi, overbougth_level=70, oversold_level=30):
	signal = np.select(
		[(rsi > oversold_level) & (rsi.shift(1) < oversold_level), 
		(rsi < overbougth_level) & (rsi.shift(1) > overbougth_level)], 
		[1, -1]
	)
	return signal

def moving_average_convergence_divergence(macd_histogram):

	signal = np.select(
		[((macd_histogram>0) & (macd_histogram.shift(1)<0)) , 
		((macd_histogram<0) & (macd_histogram.shift(1)>0))], 
		[1, -1])

	return signal

def bollinger(close_price, upper_band, lower_band):
	signal = np.select(
		[(close_price < lower_band) & (close_price.shift(1) > lower_band.shift(1)), 
		(close_price > upper_band) & (close_price.shift(1) < upper_band.shift(1))], 
		[1, -1])

	return signal

def stochastic(stochastic_d):
	signal = np.select(
		[((stochastic_d>20) & (stochastic_d.shift(1)<20)), 
		((stochastic_d<80) & (stochastic_d.shift(1)>80))],
		[1, -1])

	return signal

def williams_r(williams_r):
	signal = np.select(
		[(williams_r > -80) & (williams_r.shift(1) < -80), 
		(williams_r < -20) & (williams_r.shift(1) > -20)],
		[1, -1])

	return signal

def commodity_channel_index(cci):
	signal = np.select(
		[(cci >- 100) & (cci.shift(1) <- 100), 
		(cci < 100) & (cci.shift(1) > 100)],
		[1, -1])

	return signal

def aroon(aroon_up, aroon_down):
	signal = np.select(
		[(aroon_up > 70) & (aroon_up.shift(1) < 70), 
		(aroon_down > 70) & (aroon_down.shift(1) < 30)],
		[1, -1])

	return signal
