import functions as fc
import MetaTrader5 as mt5
import pandas as pd
import pandas_ta as ta
import time
from datetime import datetime
from pytz import timezone

if mt5.initialize():
    print('Login sucess')
else:
    print('Login error', mt5.last_error())

active = 'EURUSD'

ok = mt5.symbol_select(active, True)

if not ok:
    print("Asset addition failed ", active)
    mt5.shutdown()

# Hours
initial_operation = '10:30'
limit_operation = '23:55'
limit_close_postion = '23:50'

# IFR
sobre_compra = 52
sobre_venda = 48
period_IFR = 7
period_media = 200

# parameters
lotes = 0.01
stoploss = 0.00005
takeprofit = 0.00005

versao_EA = '1.00'
contm = 0  # contador de minutos operacionais do robô
position = ''

while True:
    region = timezone("Etc/UTC")
    d = datetime.now(tz=timezone('America/Sao_Paulo'))

    if fc.can_trade(initial_operation, limit_operation):
        # d = datetime.now()
        m = d.minute
        h = d.hour
        s = d.second

        if not fc.positioned(active):
            print(active, "Waiting... Date/Time = ", d)
        else:
            tick = mt5.symbol_info_tick(active).ask
            if position == 'SELL':
                print(s, ' - SELL : Price = ', tick, ", TP: ", v.request.tp, ", SL: ", v.request.sl),
            if position == 'BUY':
                print(s, ' - BUY : Price = ', tick, ", TP: ", c.request.tp, ", SL: ", c.request.sl)

        if s == 59:
            contm += 1

            c2 = mt5.copy_rates_from_pos(active, mt5.TIMEFRAME_M1, 0, period_IFR + 5)
            c2 = pd.DataFrame(c2)
            c2 = fc.timestamptodate(c2)

            m1 = mt5.copy_rates_from_pos(active, mt5.TIMEFRAME_M1, 0, period_media)
            m1 = pd.DataFrame(m1)
            m1 = fc.timestamptodate(m1)

            media = ta.sma(m1['close'], length=period_media)

            IFR = ta.rsi(c2['close'], length=period_IFR)

            print(media)

            if (IFR.iloc[-1] >= sobre_compra) & (fc.positioned(active) == False):
                print('Sell! -> IFR >= ', sobre_compra)
                v = fc.sell_market(active, takeprofit, stoploss, lotes)
                position = 'SELL'

            if (IFR.iloc[-1] <= sobre_venda) & (fc.positioned(active) == False):
                print('BUY! -> IFR <= ', sobre_venda)
                c = fc.buy_market(active, takeprofit, stoploss, lotes)
                position = 'BUY'

            print('IFR = ', IFR.iloc[-1], ", Sobre COMPRA: ", sobre_compra, ", Sobre VENDA: ", sobre_venda)

        if fc.positioned(active) & (d.strftime("%H:%M:%S") >= limit_close_postion):
            fc.close_position(active)
            posicao = ''
            print('Close Position')

        time.sleep(1)

    else:
        print('Attention! Out of Hours', datetime.now())

        if fc.positioned(active) & (d.strftime("%H:%M:%S") >= limit_close_postion):
            fc.close_position(active)
            posicao = ''
            print('Close Position')

        time.sleep(10)