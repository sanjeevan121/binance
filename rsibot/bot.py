import websocket, json, pprint, talib, numpy
import config
from binance.client import Client
from binance.enums import *
import backtrader as bt

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

EMA_PERIOD20 = 20
EMA_PERIOD5 = 5
TRADE_SYMBOL = 'ETHUSD'
TRADE_QUANTITY = 0.01

closes = []
in_position = False

client = Client(config.API_KEY, config.API_SECRET)

def order(side, quantity, symbol,order_type=ORDER_TYPE_MARKET):
    try:
        print("sending order")
        order = client.create_order(symbol=symbol, side=side, type=order_type, quantity=quantity)
        print(order)
    except Exception as e:
        print("an exception occured - {}".format(e))
        return False

    return True

    
def on_open(ws):
    print('opened connection')

def on_close(ws):
    print('closed connection')

def on_message(ws, message):
    global closes, in_position
    
    print('received message')
    json_message = json.loads(message)
    pprint.pprint(json_message)

    candle = json_message['k']

    is_candle_closed = candle['x']
    close = candle['c']

    if is_candle_closed:
        print("candle closed at {}".format(close))
        closes.append(float(close))
        print("closes")
        print(closes)

        if len(closes) > EMA_PERIOD20:
            np_closes = numpy.array(closes)
            ema5 = bt.ind.ExponentialMovingAverage(np_closes, EMA_PERIOD5)
            ema20 = bt.ind.ExponentialMovingAverage(np_closes, EMA_PERIOD20)
            print("all ema's calculated so far")
            print(ema5,ema20)
            last_ema= ema20[-1]
            print("the current 20 period ema is {}".format(ema20))
            cross=bt.ind.CrossOver(ema5,ema20)

            if cross < 0:
                if in_position:
                    print("Sell!")
                    # put binance sell logic here
                    order_succeeded = order(SIDE_SELL, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = False
                else:
                    print("It is overbought, but we don't own any. Nothing to do.")
            
            if cross>0:
                if in_position:
                    print("It is oversold, but you already own it, nothing to do.")
                else:
                    print("Buy!")
                    # put binance buy order logic here
                    order_succeeded = order(SIDE_BUY, TRADE_QUANTITY, TRADE_SYMBOL)
                    if order_succeeded:
                        in_position = True

                
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()