import pandas as pd
from trade import Trade
from data import CSVData
import threading

class MyCustomStrategy():

    def __init__(self, data, sl_pips, rr):

        self.data = data
        self.data_size = len(data)

        self.SESSION_HIGH = 0
        self.SESSION_LOW = float('inf')

        self.stop_loss_pips = sl_pips / (10**4)
        self.reward_risk_ratio = rr
        self.take_profit_pips = self.stop_loss_pips * self.reward_risk_ratio

        self.session_long_taken = False
        self.session_short_taken = False

        self.running_trades = set()
        self.closed_trades = set()

        self.delta_pips = 0

    def run_strategy(self):
        for date_time, candlestick in self.data.iterrows():
            current_time = date_time.time() #HHMMSS

            # print(candlestick)
            # Capture high and low between 1am and 9am
            if pd.Timestamp('01:00').time() < current_time <= pd.Timestamp('09:00').time():
                # first close all trades of the previous sessions
                for trade in self.running_trades:
                    self.closed_trades.add(trade)

                for trade in self.closed_trades:
                    if trade in self.running_trades:
                        self.running_trades.remove(trade)


                self.SESSION_HIGH = max(self.SESSION_HIGH, candlestick["high"])
                self.SESSION_LOW = min(self.SESSION_LOW, candlestick["low"])
                self.session_short_taken = False
                self.session_long_taken = False

            # we enter the period when we can take trades
            if current_time > pd.Timestamp('09:00').time():
                if not self.session_short_taken:  # if we have not already taken the short for the session
                    if candlestick['high'] > self.SESSION_HIGH: # and we surpass the session's high
                        trade = Trade(self.SESSION_HIGH, "short") # take the short for the session
                        self.running_trades.add(trade)
                        self.session_short_taken = True
                        print(f'short -> {date_time}')

                if not self.session_long_taken: # if we have not already taken the long for the session
                    if candlestick['low'] < self.SESSION_LOW: # and we go below the session's low
                        trade = Trade(self.SESSION_LOW, "long") # take the logn for the session
                        self.running_trades.add(trade)
                        self.session_long_taken = True
                        print(f'long -> {date_time}')

            self.validate_running_trades(candlestick['high'], candlestick['low'])

        self.calculate_summary()

    def validate_running_trades(self, candlestick_high, candlestick_low):
        trades_to_close = set()
        for trade in self.running_trades:
            if trade.direction == "short":
                if candlestick_high >= trade.entry_price + self.stop_loss_pips:
                    self.delta_pips -= self.stop_loss_pips

                    self.closed_trades.add(trade)

                    trades_to_close.add(trade)



                if candlestick_low <= trade.entry_price - self.take_profit_pips:
                    self.delta_pips += self.take_profit_pips

                    trade.result = "win"
                    self.closed_trades.add(trade)

                    trades_to_close.add(trade)

            if trade.direction == "long":
                if candlestick_low <= trade.entry_price - self.stop_loss_pips:
                    self.delta_pips -= self.stop_loss_pips

                    self.closed_trades.add(trade)

                    trades_to_close.add(trade)

                if candlestick_high >= trade.entry_price + self.take_profit_pips:
                    self.delta_pips += self.take_profit_pips

                    trade.result = "win"
                    self.closed_trades.add(trade)

                    trades_to_close.add(trade)

        for trade in trades_to_close:
            self.running_trades.remove(trade)

    def calculate_summary(self):
        self.delta_pips = self.delta_pips * 10000
        total_trades = len(self.closed_trades)
        winning_trades = len([trade for trade in self.closed_trades if trade.result == 'win'])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0

        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Delta Pips: {self.delta_pips:.1f}")


def execute_strategy(data, sl_pips, rr):
    print(f" < running strategy with SL - {sl_pips} pips and RR - {rr} >")
    my_strategy = MyCustomStrategy(data, sl_pips, rr)
    my_strategy.run_strategy()

if __name__=="__main__":
    threads = []
    data = CSVData("eurusd", 2022, "all").load()

    execute_strategy(data, 6, 5)

    # DUREAZA MULT DACA DAI DRUMUL LA CODUL DE MAI JOS!!!!!!
    # for sl_pips in range(2, 16):  # Values from 2 to 15 for the second argument
    #     for rr in range(1, 11):  # Values from 1 to 10 for the third argument
    #         execute_strategy(data, sl_pips, rr)

