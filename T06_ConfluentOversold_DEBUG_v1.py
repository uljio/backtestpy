import talib
import pandas as pd
from backtesting import Strategy, Backtest
import numpy as np

class ConfluentOversold(Strategy):
    # Parameters
    stoch_oversold = 20
    cci_oversold = -100
    profit_target = 0.05
    stop_loss_pct = 0.04
    risk_per_trade = 0.01  # 1% risk
    vol_period = 5
    trail_be = 0.02  # Trail to BE at 2%

    def init(self):
        # Indicators
        self.slowk, self.slowd = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close,
                                        fastk_period=14, slowk_period=3, slowd_period=3)
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low, self.data.Close, timeperiod=20)
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_period)
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)
        
        # State variables
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.previous_low_price = float('inf')
        self.previous_low_obv = float('-inf')
        self.current_low_price = float('inf')
        self.current_low_obv = float('-inf')
        self.initial_capital = self.equity  # Approximate, since equity changes

    def next(self):
        current_low = self.data.Low[-1]
        current_close = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        current_obv = self.obv[-1]

        # Update previous low if no position (track ongoing, but reset on entry)
        if not self.position:
            if current_low < self.previous_low_price:
                self.previous_low_price = current_low
                self.previous_low_obv = current_obv
        else:
            # Update current low post-entry
            if current_low < self.current_low_price:
                self.current_low_price = current_low
                self.current_low_obv = current_obv

        # Entry logic (long only)
        if not self.position and len(self.data) > 20:  # Ensure enough data
            # Conditions
            stoch_oversold_cond = self.slowk[-1] < self.stoch_oversold
            stoch_d_declining = self.slowd[-1] < self.slowd[-2]
            cci_oversold_cond = self.cci[-1] < self.cci_oversold
            vol_declining = current_volume < self.vol_sma[-1]
            
            if stoch_oversold_cond and stoch_d_declining and cci_oversold_cond and vol_declining:
                # Risk management: calculate position size
                risk_amount = self.initial_capital * self.risk_per_trade
                stop_distance = current_close * self.stop_loss_pct
                position_size = risk_amount / stop_distance  # Calculate units based on risk
                position_size_units = max(0, int(round(position_size)))  # Units of asset
                
                if position_size_units > 0:
                    self.buy(size=position_size_units)
                    self.entry_price = current_close
                    self.stop_loss = self.entry_price * (1 - self.stop_loss_pct)
                    self.take_profit = self.entry_price * (1 + self.profit_target)
                    # Set previous low to current low for divergence baseline
                    self.previous_low_price = current_low
                    self.previous_low_obv = current_obv
                    self.current_low_price = current_low
                    self.current_low_obv = current_obv
                    print(f"🌙🚀 ConfluentOversold ENTRY LONG at {current_close:.2f}, size: {position_size_units} units ✨")

        # Exit logic
        if self.position:
            # Trail stop to breakeven if +2%
            if (current_close > self.entry_price * (1 + self.trail_be) and 
                self.stop_loss < self.entry_price):
                self.stop_loss = self.entry_price
                print(f"🌙 Trailing stop to breakeven at {self.stop_loss:.2f} 🔒")

            # Profit target
            if current_close >= self.take_profit:
                self.position.close()
                print(f"🌙💰 TAKE PROFIT at {current_close:.2f} (target: {self.take_profit:.2f}) 🎉")
                # Reset states
                self._reset_states()

            # Stop loss
            elif current_close <= self.stop_loss:
                self.position.close()
                print(f"🌙🛑 STOP LOSS at {current_close:.2f} (stop: {self.stop_loss:.2f}) ⚠️")
                self._reset_states()

            # Bullish OBV divergence: new lower low in price but higher OBV
            elif (self.current_low_price < self.previous_low_price and 
                  self.current_low_obv > self.previous_low_obv):
                self.position.close()
                print(f"🌙📈 BULLISH OBV DIVERGENCE EXIT at {current_close:.2f} (price low: {self.current_low_price:.2f}, OBV: {self.current_low_obv:.0f}) 🌟")
                self._reset_states()

    def _reset_states(self):
        self.entry_price = None
        self.stop_loss = None
        self.take_profit = None
        self.current_low_price = float('inf')
        self.current_low_obv = float('-inf')
        # previous_low persists for next potential entry

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # Data cleaning as per instructions
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    bt = Backtest(data, ConfluentOversold, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(ConfluentOversold, 'ConfluentOversold', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")