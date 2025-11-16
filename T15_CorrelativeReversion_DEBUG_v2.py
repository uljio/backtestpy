import talib
from backtesting import Strategy, Backtest
import pandas as pd
import numpy as np

class CorrelativeReversion(Strategy):
    lookback = 60
    entry_z = 2.0
    exit_z = 0.5
    stop_z = 3.0
    risk_per_trade = 0.01
    stop_pct = 0.02

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.lookback)
        self.stdev = self.I(talib.STDDEV, self.data.Close, timeperiod=self.lookback)
        self.entry_bar = None

    def next(self):
        if len(self.data) < self.lookback:
            return

        current_price = self.data.Close[-1]
        mean = self.sma[-1]
        stdev = self.stdev[-1]

        if np.isnan(mean) or np.isnan(stdev) or stdev == 0:
            return

        z = (current_price - mean) / stdev

        print(f"🌙 CorrelativeReversion Debug: Z-score={z:.2f}, Price={current_price:.2f}, Mean={mean:.2f}, Std={stdev:.2f} at {self.data.index[-1]} ✨")

        # Risk Management: Check stops
        if self.position:
            if self.position.is_long and z < -self.stop_z:
                self.position.close()
                print(f"🚨 STOP LOSS LONG: Z={z:.2f} at {current_price:.2f} 🌙")
                return
            elif self.position.is_short and z > self.stop_z:
                self.position.close()
                print(f"🚨 STOP LOSS SHORT: Z={z:.2f} at {current_price:.2f} 🌙")
                return
            elif abs(z) < self.exit_z:
                self.position.close()
                print(f"✅ REVERSION EXIT: Z={z:.2f} at {current_price:.2f} 🌙")
                return

        # Entry Logic
        if not self.position:
            equity = self.equity
            risk_amount = equity * self.risk_per_trade
            risk_distance = current_price * self.stop_pct

            if risk_distance > 0:
                size = risk_amount / risk_distance
                size = max(0.0001, int(round(size)))  # Ensure minimum size, round to int units

                if z > self.entry_z:
                    # Overbought: Short
                    self.sell(size=size)
                    self.entry_bar = len(self.data)
                    print(f"🔴 ENTERING SHORT: Size={size:.4f}, Price={current_price:.2f}, Z={z:.2f}, Risk={risk_amount:.2f} 🚀")
                elif z < -self.entry_z:
                    # Oversold: Long
                    self.buy(size=size)
                    self.entry_bar = len(self.data)
                    print(f"🟢 ENTERING LONG: Size={size:.4f}, Price={current_price:.2f}, Z={z:.2f}, Risk={risk_amount:.2f} 🚀")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    bt = Backtest(data, CorrelativeReversion, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")

    # THEN: Run multi-data testing
    sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-trading-bots/backtests')
    from multi_data_tester import test_on_all_data

    print("\n" + "="*80)
    print("🚀 MOON DEV'S MULTI-DATA BACKTEST - Testing on 25+ Data Sources!")
    print("="*80)

    # Test this strategy on all configured data sources
    # This will test on: BTC, ETH, SOL (multiple timeframes), AAPL, TSLA, ES, NQ, GOOG, NVDA
    # IMPORTANT: verbose=False to prevent plotting (causes timeouts in parallel processing!)
    results = test_on_all_data(CorrelativeReversion, 'CorrelativeReversion', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")