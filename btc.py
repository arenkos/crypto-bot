import time
import ccxt
import pandas as pd
import numpy as np
from datetime import datetime
import math
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
SYMBOL = "BTC/USDT"
SYMBOL_NAME = "BTC"
MAX_LEVERAGE = 50
MAX_STOP_PERCENTAGE = 50
START_DATE = datetime(2022, 7, 15, 3, 0, 0)
INITIAL_BALANCE = 100.0
ATR_PERIOD = 10
ATR_MULTIPLIER = 3

# API CONNECT
exchange = ccxt.binance({
    "apiKey": 'G2dI1suDiH3bCKo1lpx1Ho4cdTjmWh9eQEUSajcshC1rcQ0T1yATZnKukHiqo6IN',
    "secret": 'ow4J1QLRTXhzuhtBcFNOUSPq2uRYhrkqHaLri0zdAiMhoDCfJgEfXz0mSwvgpnPx',

    'options': {
        'defaultType': 'future'
    },
    'enableRateLimit': True
})

# Define timeframes to test
TIMEFRAMES = {
    "1m": 1440,
    "3m": 480,
    "5m": 288,
    "15m": 96,
    "30m": 48,
    "1h": 24,
    "2h": 12,
    "4h": 6,
    "1d": 1
}


class SupertrendCalculator:
    @staticmethod
    def calculate_atr(high_array, low_array, close_array, period=14):
        """Calculate Average True Range without using TA-Lib"""
        tr = np.zeros_like(close_array)
        tr[0] = np.nan

        for i in range(1, len(close_array)):
            high_low = high_array[i] - low_array[i]
            high_close = np.abs(high_array[i] - close_array[i - 1])
            low_close = np.abs(low_array[i] - close_array[i - 1])
            tr[i] = np.max([high_low, high_close, low_close])

        atr = np.zeros_like(close_array)
        atr[:period] = np.nan
        atr[period] = np.mean(tr[1:period + 1])

        for i in range(period + 1, len(close_array)):
            atr[i] = (atr[i - 1] * (period - 1) + tr[i]) / period

        return atr

    @staticmethod
    def calculate(close_array, high_array, low_array, atr_period=10, atr_multiplier=3):
        """Calculate Supertrend values for given price data"""
        try:
            # Replace TA-Lib ATR with our custom implementation
            atr = SupertrendCalculator.calculate_atr(high_array, low_array, close_array, atr_period)
        except Exception as e:
            print(f"[ERROR] {e}")
            return []

        previous_final_upperband = 0
        previous_final_lowerband = 0
        previous_close = 0
        previous_supertrend = 0
        supertrend = []

        for i in range(len(close_array)):
            if np.isnan(close_array[i]):
                supertrend.append(np.nan)
                continue

            highc = high_array[i]
            lowc = low_array[i]
            closec = close_array[i]
            atrc = atr[i] if not math.isnan(atr[i]) else 0

            # Calculate basic bands
            basic_upperband = (highc + lowc) / 2 + atr_multiplier * atrc
            basic_lowerband = (highc + lowc) / 2 - atr_multiplier * atrc

            # Calculate final bands
            if basic_upperband < previous_final_upperband or previous_close > previous_final_upperband:
                final_upperband = basic_upperband
            else:
                final_upperband = previous_final_upperband

            if basic_lowerband > previous_final_lowerband or previous_close < previous_final_lowerband:
                final_lowerband = basic_lowerband
            else:
                final_lowerband = previous_final_lowerband

            # Calculate supertrend
            if previous_supertrend == previous_final_upperband and closec <= final_upperband:
                current_supertrend = final_upperband
            elif previous_supertrend == previous_final_upperband and closec >= final_upperband:
                current_supertrend = final_lowerband
            elif previous_supertrend == previous_final_lowerband and closec >= final_lowerband:
                current_supertrend = final_lowerband
            elif previous_supertrend == previous_final_lowerband and closec <= final_lowerband:
                current_supertrend = final_upperband
            else:
                # Initialize case
                current_supertrend = final_lowerband if closec > (highc + lowc) / 2 else final_upperband

            supertrend.append(current_supertrend)

            # Update previous values
            previous_close = closec
            previous_final_upperband = final_upperband
            previous_final_lowerband = final_lowerband
            previous_supertrend = current_supertrend

        return supertrend


class DataManager:
    @staticmethod
    def fetch_historical_data():
        """Fetch historical data for all timeframes"""
        start_timestamp = int(START_DATE.timestamp() * 1000)
        dataframes = {}

        # Create daily chunks for fetching data to avoid rate limits
        days = 365
        print("Fetching historical data...")

        for timeframe, limit in TIMEFRAMES.items():
            print(f"Fetching {timeframe} data...")
            chunks = []
            current_timestamp = start_timestamp

            for day in range(days):
                try:
                    bars = exchange.fetch_ohlcv(SYMBOL, timeframe=timeframe, since=current_timestamp, limit=limit)
                    if bars:
                        chunk_df = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
                        chunks.append(chunk_df)
                    current_timestamp += 86400000  # Add one day in milliseconds

                    # Add a small delay to avoid hitting rate limits
                    if day % 10 == 0:
                        time.sleep(1)

                except Exception as e:
                    print(f"Error fetching {timeframe} data for day {day}: {e}")
                    time.sleep(5)  # Wait longer on error

            if chunks:
                dataframes[timeframe] = pd.concat(chunks, ignore_index=True)

        # Fetch weekly data with a single request
        try:
            bars = exchange.fetch_ohlcv(SYMBOL, timeframe="1w", since=None, limit=52)
            dataframes["1w"] = pd.DataFrame(bars, columns=["timestamp", "open", "high", "low", "close", "volume"])
        except Exception as e:
            print(f"Error fetching 1w data: {e}")

        return dataframes


class BacktestEngine:
    def __init__(self, df, timeframe):
        self.df = df
        self.timeframe = timeframe
        self.results = []

        # Convert price columns to float
        self.df["open"] = self.df["open"].astype(float)
        self.df["high"] = self.df["high"].astype(float)
        self.df["low"] = self.df["low"].astype(float)
        self.df["close"] = self.df["close"].astype(float)

        # Calculate Supertrend
        close_array = self.df["close"].values
        high_array = self.df["high"].values
        low_array = self.df["low"].values

        self.supertrend = SupertrendCalculator.calculate(
            close_array, high_array, low_array,
            atr_period=ATR_PERIOD, atr_multiplier=ATR_MULTIPLIER
        )

    def run_backtest(self, leverage, take_profit_pct):
        """Run backtest with specific parameters"""
        lim = len(self.df)
        if lim < 4:  # Need at least 4 candles to start
            return None

        balance = INITIAL_BALANCE
        successful_trades = 0
        unsuccessful_trades = 0
        total_trades = 0
        liquidated = False

        # Start from the 4th candle to have enough history
        i = 3
        while i < lim:
            # Check for Supertrend signal
            current_close = self.df["close"].iloc[i - 2]
            previous_close = self.df["close"].iloc[i - 3]
            current_supertrend = self.supertrend[i - 2] if i - 2 < len(self.supertrend) else None
            previous_supertrend = self.supertrend[i - 3] if i - 3 < len(self.supertrend) else None

            # Skip if we don't have valid Supertrend values
            if current_supertrend is None or previous_supertrend is None:
                i += 1
                continue

            signal = None
            # Long signal - price crosses above Supertrend
            if current_close > current_supertrend and previous_close < previous_supertrend:
                signal = "LONG"
            # Short signal - price crosses below Supertrend
            elif current_close < current_supertrend and previous_close > previous_supertrend:
                signal = "SHORT"

            if signal:
                total_trades += 1
                entry_price = self.df["open"].iloc[i]
                exit_index = None
                exit_price = None
                profit_loss = 0
                is_successful = False
                reason = None

                # Loop through future candles to find exit point
                j = i
                while j < lim:
                    current_price_high = self.df["high"].iloc[j]
                    current_price_low = self.df["low"].iloc[j]

                    # Check for Supertrend exit signal
                    if j >= 2:  # Need at least 2 candles of history
                        exit_close = self.df["close"].iloc[j - 2]
                        exit_prev_close = self.df["close"].iloc[j - 3]
                        exit_supertrend = self.supertrend[j - 2] if j - 2 < len(self.supertrend) else None
                        exit_prev_supertrend = self.supertrend[j - 3] if j - 3 < len(self.supertrend) else None

                        # Check for opposite signal
                        if signal == "LONG" and exit_supertrend is not None and exit_prev_supertrend is not None:
                            if exit_close < exit_supertrend and exit_prev_close > exit_prev_supertrend:
                                exit_index = j
                                exit_price = self.df["open"].iloc[j]
                                profit_loss = (exit_price - entry_price) / entry_price * 100 * leverage
                                reason = "SIGNAL"
                                break
                        elif signal == "SHORT" and exit_supertrend is not None and exit_prev_supertrend is not None:
                            if exit_close > exit_supertrend and exit_prev_close < exit_prev_supertrend:
                                exit_index = j
                                exit_price = self.df["open"].iloc[j]
                                profit_loss = (entry_price - exit_price) / entry_price * 100 * leverage
                                reason = "SIGNAL"
                                break

                    # Check for take profit
                    if signal == "LONG" and (current_price_high - entry_price) / entry_price * 100 >= take_profit_pct:
                        exit_index = j
                        exit_price = entry_price * (1 + take_profit_pct / 100)
                        profit_loss = take_profit_pct * leverage
                        reason = "TP"
                        break
                    elif signal == "SHORT" and (entry_price - current_price_low) / entry_price * 100 >= take_profit_pct:
                        exit_index = j
                        exit_price = entry_price * (1 - take_profit_pct / 100)
                        profit_loss = take_profit_pct * leverage
                        reason = "TP"
                        break

                    # Check for liquidation
                    if signal == "LONG" and (current_price_low - entry_price) / entry_price * 100 <= -90 / leverage:
                        exit_index = j
                        exit_price = entry_price * (1 - 90 / leverage / 100)
                        balance = 0
                        liquidated = True
                        reason = "LIQUIDATION"
                        break
                    elif signal == "SHORT" and (current_price_high - entry_price) / entry_price * 100 >= 90 / leverage:
                        exit_index = j
                        exit_price = entry_price * (1 + 90 / leverage / 100)
                        balance = 0
                        liquidated = True
                        reason = "LIQUIDATION"
                        break

                    j += 1

                    # If we reach the end of data without an exit
                    if j == lim:
                        exit_index = lim - 1
                        exit_price = self.df["close"].iloc[-1]
                        if signal == "LONG":
                            profit_loss = (exit_price - entry_price) / entry_price * 100 * leverage
                        else:
                            profit_loss = (entry_price - exit_price) / entry_price * 100 * leverage
                        reason = "END_OF_DATA"
                        break

                # Update balance and counters
                if not liquidated:
                    balance = balance * (1 + profit_loss / 100)

                if profit_loss > 0:
                    successful_trades += 1
                    is_successful = True
                else:
                    unsuccessful_trades += 1

                # Move to the candle after exit
                if exit_index is not None:
                    i = exit_index + 1
                else:
                    i += 1

                # Break if liquidated
                if liquidated:
                    break
            else:
                i += 1

        return {
            "timeframe": self.timeframe,
            "leverage": leverage,
            "take_profit": take_profit_pct,
            "final_balance": balance,
            "successful_trades": successful_trades,
            "unsuccessful_trades": unsuccessful_trades,
            "total_trades": total_trades,
            "win_rate": successful_trades / total_trades if total_trades > 0 else 0,
            "liquidated": liquidated
        }

    def optimize(self):
        """Find optimal parameters"""
        best_result = None
        best_balance = 0

        # Test different leverage and take profit combinations
        for leverage in range(1, MAX_LEVERAGE + 1):
            # Start with higher take profit for higher leverage to manage risk
            min_tp = max(0.5, 0.5 * leverage / 10)

            for take_profit in np.arange(min_tp, MAX_STOP_PERCENTAGE + 0.5, 0.5):
                # Skip extreme combinations that are likely to lead to liquidation
                if leverage > 20 and take_profit < 5:
                    continue

                result = self.run_backtest(leverage, take_profit)

                if result:
                    if result["final_balance"] > best_balance:
                        best_balance = result["final_balance"]
                        best_result = result

                    # Early stopping if liquidated and high leverage
                    if result["liquidated"] and leverage > 10:
                        break

        return best_result


def main():
    # Fetch historical data
    data_manager = DataManager()
    dataframes = data_manager.fetch_historical_data()

    # Run backtest for each timeframe
    results = []

    for timeframe, df in dataframes.items():
        print(f"\nOptimizing for {timeframe} timeframe...")
        backtest = BacktestEngine(df, timeframe)
        result = backtest.optimize()
        if result:
            results.append(result)
            print(f"Best parameters: Leverage = {result['leverage']}, TP = {result['take_profit']}%")
            print(f"Final balance: ${result['final_balance']:.2f}")
            print(f"Win rate: {result['win_rate'] * 100:.1f}%")

    # Sort results by final balance
    results.sort(key=lambda x: x['final_balance'], reverse=True)

    # Save results to file
    with open(f"{SYMBOL_NAME}_optimization_results.txt", "w") as f:
        f.write(f"Optimization Results for {SYMBOL_NAME}\n")
        f.write("=" * 50 + "\n\n")

        for result in results:
            f.write(f"Timeframe: {result['timeframe']}\n")
            f.write(f"Leverage: {result['leverage']}\n")
            f.write(f"Take Profit: {result['take_profit']}%\n")
            f.write(f"Final Balance: ${result['final_balance']:.2f}\n")
            f.write(f"Successful Trades: {result['successful_trades']}\n")
            f.write(f"Unsuccessful Trades: {result['unsuccessful_trades']}\n")
            f.write(f"Win Rate: {result['win_rate'] * 100:.1f}%\n")
            f.write("=" * 50 + "\n\n")

    print(f"\nResults saved to {SYMBOL_NAME}_optimization_results.txt")

    # Print summary of best strategy
    if results:
        best = results[0]
        print("\nBest Overall Strategy:")
        print(f"Timeframe: {best['timeframe']}")
        print(f"Leverage: {best['leverage']}")
        print(f"Take Profit: {best['take_profit']}%")
        print(f"Final Balance: ${best['final_balance']:.2f}")
        print(f"Win Rate: {best['win_rate'] * 100:.1f}%")


if __name__ == "__main__":
    main()