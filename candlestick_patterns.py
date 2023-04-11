import pandas as pd
import numpy as np

def find_pattern(open_price, high_price, low_price, close_price, pattern):

	realbody = (open_price - close_price).abs()
	candle_range = high_price - low_price
	upper_shadow = high_price - pd.concat([close_price, open_price], axis=1).max(axis=1)
	lower_shadow = pd.concat([close_price, open_price], axis=1).min(axis=1) - low_price

	# TREND REVERSAL PATTERNS
	if pattern == 'White Marubozu':
		series = np.where(
			(close_price > open_price) &
			(close_price == high_price) &
			(open_price == low_price)
		, 1, 0)

	if pattern == 'Black Marubozu':
		series = np.where(
			(close_price < open_price) &
			(close_price == low_price) &
			(open_price == high_price)
		, -1, 0)

	if pattern == 'Bullish Engulfing':
		series = np.where(
			(close_price > open_price) &
			(close_price.shift(1) < open_price.shift(1)) &
			(close_price > open_price.shift(1)) &
			(open_price < close_price.shift(1))
		, 1, 0)

	if pattern == 'Bearish Engulfing':
		series = np.where(
			(close_price < open_price) &
			(close_price.shift(1) > open_price.shift(1)) &
			(close_price < open_price.shift(1)) &
			(open_price > close_price.shift(1))
		, -1, 0)

	if pattern == 'Bullish Harami':
		series = np.where(
			(close_price > open_price) &
			(close_price.shift(1) < open_price.shift(1)) &
			(close_price < open_price.shift(1)) &
			(open_price > close_price.shift(1))
		, 1, 0)

	if pattern == 'Bearish Harami':
		series = np.where(
			(close_price < open_price) &
			(close_price.shift(1) > open_price.shift(1)) &
			(close_price > open_price.shift(1)) &
			(open_price < close_price.shift(1))
		, -1, 0)

	if pattern == 'Tweezer Bottom':
		series = np.where(
			(open_price < close_price) &
			(open_price.shift(1) < close_price.shift(1)) &
			(low_price == low_price.shift(1))
		, 1, 0)

	if pattern == 'Tweezer Top':
		series = np.where(
			(open_price > close_price) &
			(open_price.shift(1) > close_price.shift(1)) &
			(high_price == high_price.shift(1))
		, -1, 0)

	if pattern == 'Piercing Line':
		series = np.where(
			(close_price > open_price) &
			(close_price.shift(1) < open_price.shift(1)) &
			(open_price < close_price.shift(1)) &
			(close_price > (open_price.shift(1) + close_price.shift(1))/2)
		, 1, 0)

	if pattern == 'Dark Cloud Cover':
		series = np.where(
			(close_price < open_price) &
			(close_price.shift(1) > open_price.shift(1)) &
			(close_price > open_price.shift(1)) &
			(close_price < (open_price.shift(1) + close_price.shift(1))/2)
		, -1, 0)

	if pattern == 'Morning Star':
		series = np.where(
			(close_price.shift(2) < open_price.shift(2)) &
			(close_price > open_price) &
			(open_price > pd.concat([close_price, open_price], axis=1).max(axis=1).shift(1)) &
			(close_price.shift(2) > pd.concat([close_price, open_price], axis=1).max(axis=1).shift(1)) &
			(close_price > (close_price.shift(2) + open_price.shift(2))/2)
		, 1, 0)

	if pattern == 'Evening Star':
		series = np.where(
			(close_price.shift(2) > open_price.shift(2)) &
			(close_price < open_price) &
			(open_price < pd.concat([close_price, open_price], axis=1).min(axis=1).shift(1)) &
			(close_price.shift(2) < pd.concat([close_price, open_price], axis=1).min(axis=1).shift(1)) &
			(close_price < (close_price.shift(2) + open_price.shift(2))/2)
		, -1, 0)

	if pattern == 'Three White Soldiers':
		series = np.where(
			(close_price > open_price) &
			(close_price.shift(1) > open_price.shift(1)) &
			(close_price.shift(2) > open_price.shift(2)) &
			(close_price > close_price.shift(1)) &
			(close_price.shift(1) > close_price.shift(2)) &
			(open_price > open_price.shift(1)) &
			(open_price.shift(1) > open_price.shift(2)) &
			(realbody > 0.8 * candle_range) &
			(realbody.shift(1) > 0.8 * candle_range.shift(1)) &
			(realbody.shift(2) > 0.8 * candle_range.shift(2)) &
			(open_price < close_price.shift(1)) &
			(open_price.shift(1) < close_price.shift(2))
		, 1, 0)

	if pattern == 'Three Black Crows':
		series = np.where(
			(close_price < open_price) &
			(close_price.shift(1) < open_price.shift(1)) &
			(close_price.shift(2) < open_price.shift(2)) &
			(close_price < close_price.shift(1)) &
			(close_price.shift(1) < close_price.shift(2)) &
			(open_price < open_price.shift(1)) &
			(open_price.shift(1) < open_price.shift(2)) &
			(realbody > 0.8 * candle_range) &
			(realbody.shift(1) > 0.8 * candle_range.shift(1)) &
			(realbody.shift(2) > 0.8 * candle_range.shift(2)) &
			(open_price < close_price.shift(1)) &
			(open_price.shift(1) < close_price.shift(2))
		, -1, 0)

	if pattern == 'Three Inside Up':
		series = np.where(
			(open_price.shift(2) > close_price.shift(2)) &
			(open_price.shift(1) < close_price.shift(1)) &
			(open_price < close_price) &
			(close_price.shift(1) < open_price.shift(2)) &
			(close_price.shift(2) < open_price.shift(1)) &
			(close_price > close_price.shift(1)) &
			(open_price > open_price.shift(1))
		,1 ,0)

	if pattern == 'Three Inside Down':
		series = np.where(
			(open_price.shift(2) < close_price.shift(2)) &
			(open_price.shift(1) > close_price.shift(1)) &
			(open_price > close_price) &
			(close_price.shift(1) > open_price.shift(2)) &
			(close_price.shift(2) > open_price.shift(1)) &
			(close_price < close_price.shift(1)) &
			(open_price < open_price.shift(1))
		,-1 ,0)

	if pattern == 'Three Outside Up':
		series = np.where(
			(open_price.shift(2) > close_price.shift(2)) &
			(open_price.shift(1) < close_price.shift(1)) &
			(open_price < close_price) &
			(close_price.shift(1) > open_price.shift(2)) &
			(close_price.shift(2) > open_price.shift(1)) &
			(close_price > close_price.shift(1)) &
			(open_price > open_price.shift(1))
		,1 ,0)

	if pattern == 'Three Outside Down':
		series = np.where(
			(open_price.shift(2) < close_price.shift(2)) &
			(open_price.shift(1) > close_price.shift(1)) &
			(open_price > close_price) &
			(close_price.shift(1) > open_price.shift(2)) &
			(close_price.shift(2) > open_price.shift(1)) &
			(close_price < close_price.shift(1)) &
			(open_price < open_price.shift(1))
		,-1 ,0)

	if pattern == 'Upside Tasuki Gap':
		series = np.where(
			(close_price.shift(2) > open_price.shift(2)) &
			(close_price.shift(1) > open_price.shift(1)) &
			(open_price > close_price) &
			(open_price.shift(1) > close_price.shift(2)) &
			(open_price > open_price.shift(1)) &
			(close_price < close_price.shift(2)) &
			(open_price < close_price.shift(1)) &
			(close_price > open_price.shift(2))
		, 1, 0)

	if pattern == 'Downside Tasuki Gap':
		series = np.where(
			(close_price.shift(2) < open_price.shift(2)) &
			(close_price.shift(1) < open_price.shift(1)) &
			(open_price < close_price) &
			(open_price.shift(1) < close_price.shift(2)) &
			(open_price < open_price.shift(1)) &
			(close_price > close_price.shift(2)) &
			(open_price > close_price.shift(1)) &
			(close_price < open_price.shift(2))
		, -1, 0)

	return series