import pandas as pd
from trade import Trade
from data import CSVData

class MyCustomStrategy():

    def __init__(self, data):

        self.data = data
        self.data_size = len(data)

        self.SESSION_HIGH = 0
        self.SESSION_LOW = float('inf')

        candlestick = None

        self.stop_loss_pips = 0.00002
        self.reward_risk_ratio = 10
        self.take_profit_pips = self.stop_loss_pips * self.reward_risk_ratio

        self.session_long_taken = False
        self.session_short_taken = False

        self.running_trades = []
        self.trades_taken = []

        self.delta_pips = 0

    def next(self):
        for date_time, candlestick in self.data.iterrows():
            current_time = date_time.time() #HHMMSS

            # print(candlestick)
            # Capture high and low between 1am and 9am
            if pd.Timestamp('01:00').time() < current_time <= pd.Timestamp('09:00').time():
                self.SESSION_HIGH = max(self.SESSION_HIGH, candlestick["high"])
                self.SESSION_LOW = min(self.SESSION_LOW, candlestick["low"])

            # we enter the period when we can take trades
            if current_time > pd.Timestamp('09:00').time():
                if not self.session_short_taken:  # if we have not already taken the short for the session
                    if candlestick['high'] > self.SESSION_HIGH: # and we surpass the session's high
                        trade = Trade(self.SESSION_HIGH, "short") # take the short for the session
                        self.running_trades.append(trade)
                        self.trades_taken.append(trade)
                        self.session_short_taken = True
                        print(f'short taken -> {date_time}')

                if not self.session_long_taken: # if we have not already taken the long for the session
                    if candlestick['low'] < self.SESSION_LOW: # and we go below the session's low
                        trade = Trade(self.SESSION_LOW, "long") # take the logn for the session
                        self.running_trades.append(trade)
                        self.trades_taken.append(trade)
                        self.session_long_taken = True
                        print(f'long taken -> {date_time}')

            self.validate_running_trades(candlestick['high'], candlestick['low'])

    def validate_running_trades(self, candlestick_high, candlestick_low):
        stop_loss_trades = set()
        take_profit_trades = set()

        for trade in self.running_trades:
            if trade.direction == "short":
                if self.SESSION_HIGH >= trade.entry_price - self.take_profit_pips:
                    self.delta_pips += self.take_profit_pips
                    take_profit_trades.add(trade)
                elif self.SESSION_HIGH <= trade.entry_price + self.stop_loss_pips:
                    self.delta_pips -= self.stop_loss_pips
                    stop_loss_trades.add(trade)

            if trade.direction == "long":
                if self.SESSION_LOW < trade.entry_price + self.take_profit_pips:
                    self.delta_pips -= self.stop_loss_pips
                    stop_loss_trades.add(trade)
                elif self.SESSION_HIGH >= trade.entry_price + trade.pips_to_take_profit:
                    self.delta_pips += self.take_profit_pips
                    take_profit_trades.add(trade)

        for stop_loss_trades in stop_loss_trades:
            self.running_trades.remove(stop_loss_trades)

        for trade_to_take_profit in take_profit_trades:
            self.running_trades.remove(trade_to_take_profit)
            # Reset session flags if necessary
            if trade_to_take_profit.direction == "long":
                self.session_long_taken = False
            else:
                self.session_short_taken = False
            # Record the trade details in trade history

    def calculate_summary(self):
        total_trades = len(self.trades_taken)
        winning_trades = len([trade for trade in self.trades_taken if trade.result == 'profit'])
        losing_trades = total_trades - winning_trades
        win_rate = winning_trades / total_trades * 100 if total_trades > 0 else 0

        print(f"Total Trades: {total_trades}")
        print(f"Winning Trades: {winning_trades}")
        print(f"Losing Trades: {losing_trades}")
        print(f"Win Rate: {win_rate:.2f}%")
        print(f"Delta Pips: {self.delta_pips:.6f}")



data = CSVData("eurusd", 2022, 8).load()
print(len(data))

my_strategy = MyCustomStrategy(data)

my_strategy.next()


# data.columns = ['Open', 'High', 'Low', 'Close']
# # print(data)
# bt = Backtest(data, MyStrategy)
# stats = bt.run()
