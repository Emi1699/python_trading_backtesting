import pandas as pd

class CSVData:

    def __init__(self, pair, year, month="all"):
        self.pair = pair
        self.year = year
        self.month = month
        self.data_path = f"csv_data/{self.pair}/{self.pair.upper()}_M1_{self.year}.csv"

    def load(self):
        column_names = ['DateTime', 'open', 'high', 'low', 'close', 'Volume']
        # Read the CSV with DateTime as index directly
        data = pd.read_csv(self.data_path, sep=';', names=column_names, index_col='DateTime', parse_dates=['DateTime'])
        # Filter for the specific month if required
        if self.month != "all":
            data = data[data.index.month == self.month]
        return data[['open', 'high', 'low', 'close']]
