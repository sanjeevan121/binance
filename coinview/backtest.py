import backtrader as bt
import datetime
import math

class maxRiskSizer(bt.Sizer):
    '''
    Returns the number of shares rounded down that can be purchased for the
    max rish tolerance
    '''
    params = (('risk', 0.3),)

    def __init__(self):
        if self.p.risk > 1 or self.p.risk < 0:
            raise ValueError('The risk parameter is a percentage which must be'
                'entered as a float. e.g. 0.5')

    def _getsizing(self, comminfo, cash, data, isbuy):
        if isbuy == True:
            size = math.floor((cash * self.p.risk) / data[0])
        else:
            size = math.floor((cash * self.p.risk) / data[0]) * -1
        return size



class RSIStrategy(bt.Strategy):

    def __init__(self):
        self.rsi = bt.ind.RSI(self.data, period=14)


    def next(self):
        if self.rsi < 20 and not self.position:
            self.buy()

        if self.rsi > 80 and self.position:
            self.close()


cerebro = bt.Cerebro()


data = bt.feeds.GenericCSVData(dataname='data/2020_15minutes.csv', dtformat=2, compression=15,
                               timeframe=bt.TimeFrame.Minutes)

cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.addstrategy(RSIStrategy)
#add the sizer
cerebro.addsizer(maxRiskSizer)
cerebro.run()

cerebro.plot()