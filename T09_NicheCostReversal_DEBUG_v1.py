import talib
from backtesting import Strategy
import pandas as pd
import sys
import os

class NicheCostReversal(Strategy):
    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.std = self.I(talib.STDDEV, self.data.Close, timeperiod=20)
        self.vol_avg = self.I(talib.SMA, self.data.Volume, timeperiod=10)
        self.trade_bars = 0

    def next(self):
        # Risk management: Reset trade bars when no position
        if not self.position:
            self.trade_bars = 0
            # Entry logic for long position
            if (len(self.data) > 20 and  # Ensure enough data for indicators
                self.data.Close[-1] < (self.ema[-1] - 2 * self.std[-1]) and
                self.rsi[-1] < 30 and
                self.data.Volume[-1] > self.vol_avg[-1]):
                
                entry_price = self.data.Close[-1]
                sl_price = entry_price * 0.96  # 4% stop loss
                tp_price = entry_price * 1.075  # 7.5% profit target
                
                # Position sizing: Risk 1% of equity
                equity = self.equity
                risk_amount = 0.01 * equity
                risk_per_unit = entry_price - sl_price
                size = risk_amount / risk_per_unit
                size = int(round(size))
                
                if size > 0:
                    self.buy(size=size, sl=sl_price, tp=tp_price)
                    self.trade_bars = 1  # Start counting from 1
                    print(f"🌙 Moon Dev NicheCostReversal LONG Entry: {size} units at {entry_price:.2f}, SL {sl_price:.2f}, TP {tp_price:.2f}, Equity {equity:,.2f} ✨🚀")
        else:
            # Increment trade bars
            self.trade_bars += 1
            # Exit logic: Reversion signal or time-based exit
            if (self.data.Close[-1] >= self.ema[-1] or 
                self.rsi[-1] > 70 or 
                self.trade_bars > 480):  # ~5 days on 15m (96 bars/day * 5)
                self.position.close()
                print(f"🌙 Moon Dev NicheCostReversal Exit at bar {self.trade_bars}: Price {self.data.Close[-1]:.2f}, RSI {self.rsi[-1]:.2f}, EMA {self.ema[-1]:.2f} 🚀💫")
                self.trade_bars = 0

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    from backtesting import Backtest

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))
    print(f"🌙 Moon Dev Debug: Loaded data shape {data.shape}, columns: {list(data.columns)} ✨")

    bt = Backtest(data, NicheCostReversal, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print(stats._strategy)
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
    results = test_on_all_data(NicheCostReversal, 'NicheCostReversal', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")