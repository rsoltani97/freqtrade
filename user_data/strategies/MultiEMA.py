from freqtrade.strategy import IStrategy, merge_informative_pair
from pandas import DataFrame
import talib.abstract as ta
import freqtrade.vendor.qtpylib.indicators as qtpylib
from freqtrade.strategy import CategoricalParameter, DecimalParameter, IntParameter
import numpy  # noqa
from freqtrade.persistence import Trade


class MultiEMA(IStrategy):
    """
    EMAPriceCrossoverWithTreshold
    author@: Paul Csapak
    github@: https://github.com/paulcpk/freqtrade-strategies-that-work
    How to use it?
    > freqtrade download-data --timeframes 1h --timerange=20180301-20200301
    > freqtrade backtesting --export trades -s EMAPriceCrossoverWithTreshold --timeframe 1h --timerange=20180301-20200301
    > freqtrade plot-dataframe -s EMAPriceCrossoverWithTreshold --indicators1 ema800 --timeframe 1h --timerange=20180301-20200301
    """

    # Minimal ROI designed for the strategy.
    # This attribute will be overridden if the config file contains "minimal_roi"
    # minimal_roi = {
    #     "40": 0.0,
    #     "30": 0.01,
    #     "20": 0.02,
    #     "0": 0.04
    # }

    # This attribute will be overridden if the config file contains "stoploss"
    stoploss = -0.247

    # Optimal timeframe for the strategy
    timeframe = '1h'

    # trailing stoploss
    trailing_stop = True

    emas = [710, 350, 430, 900]
    sell_thresholds = [2, 5, 3, 9]

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for i, val in enumerate(self.emas):
            dataframe['ema_{}'.format(val)] = ta.EMA(dataframe, timeperiod=val)
            dataframe['ema_thresh_{}'.format(val)] = dataframe['ema_{}'.format(val)] \
                                                     * (100 - self.sell_thresholds[i]) / 100

        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for i, ema in enumerate(self.emas):
            dataframe.loc[
                (
                        (qtpylib.crossed_above(dataframe['close'], dataframe['ema_{}'.format(ema)])) &
                        (dataframe['volume'] > 0)
                ),
                'buy_{}'.format(i)] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        for i, ema in enumerate(self.emas):
            dataframe.loc[
                (
                    qtpylib.crossed_below(dataframe['close'], dataframe['ema_thresh_{}'.format(ema)])
                ),
                'sell_{}'.format(i)] = 1
        return dataframe

    def confirm_trade_entry(self, pair: str, order_type: str, amount: float, rate: float,
                            time_in_force: str, **kwargs) -> bool:
        return True

    def confirm_trade_exit(self, pair: str, trade: Trade, order_type: str, amount: float,
                           rate: float, time_in_force: str, sell_reason: str, **kwargs) -> bool:
        return True
