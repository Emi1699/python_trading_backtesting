from strategy import MyCustomStrategy
import data

if __name__=="__main__":
    an = 2022
    luna = 2 # pune un numar de la 1 la 12 sau "all"
    stop_loss_pips = 6
    reward_to_risk_ratio = 4

    data = CSVData("eurusd", an, luna).load()
    my_strategy = MyCustomStrategy(data, stop_loss_pips, reward_to_risk_ratio)

    my_strategy.run_strategy()
