import talib
import pandas as pd
from backtesting import Backtest, Strategy
import numpy as np

# 🌙 MOON DEV'S OPTIMIZED HOLISTIC DECOMPOSITION STRATEGY 🚀
# OPTIMIZATIONS APPLIED:
# 1. ENTRY: Switched to EMA(50) for trend (faster response than SMA). Added EMA(200) for long-term trend filter (only long in uptrend, short in downtrend).
#    Tightened RSI to >55 for longs, <45 for shorts (avoids neutral momentum). Increased volume multiplier to 1.5x (filters low-quality entries).
#    Added symmetric short entries for bearish alignment (captures downtrends in volatile assets like BTC).
# 2. EXIT: Fixed ATR to entry-time value (stored self.entry_atr) for consistent SL/TP. Removed signal-based exits (prevents cutting winners short).
#    Tightened SL to 1.5x ATR (better risk control). Increased RR to 3:1 (higher reward potential). No trailing yet (keeps simple).
# 3. RISK: sl_mult=1.5 for dynamic stops. Position sizing uses updated stop_distance. Min size=1 to avoid zero positions.
# 4. INDICATORS: EMA for trend responsiveness. Multi-timeframe proxy via EMA(200). No curve-fitting: standard periods (50/200 common for trend).
# 5. REGIME: EMA short > long for longs (uptrend only), opposite for shorts (avoids choppy markets).
# These changes aim for higher win rate + better RR to target 50% returns while managing drawdowns.

class HolisticDecomposition(Strategy):
    # Optimized Parameters for decomposition dimensions
    ema_short_period = 50  # Short-term trend (was SMA 20)
    ema_long_period = 200  # Long-term trend filter (new)
    rsi_period = 14  # Momentum dimension
    vol_period = 20  # Volume participation
    atr_period = 14  # Volatility for risk (stop/target)
    risk_per_trade = 0.01  # 1% risk
    sl_mult = 1.5  # SL multiplier (tightened from 2)
    rr_ratio = 3  # Risk-reward 1:3 (improved from 2)
    rsi_long_threshold = 55  # Tightened for longs (was 50)
    rsi_short_threshold = 45  # Symmetric for shorts
    vol_multiplier = 1.5  # Increased from 1.2 for better filters
    
    def init(self):
        # 🌙 Calculate core indicators using TA-Lib via self.I()
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume
        
        # Dimensional Indicators (optimized)
        self.ema_short = self.I(talib.EMA, close, timeperiod=self.ema_short_period)  # Trend proxy (faster EMA)
        self.ema_long = self.I(talib.EMA, close, timeperiod=self.ema_long_period)  # Long-term filter (new)
        self.rsi = self.I(talib.RSI, close, timeperiod=self.rsi_period)  # Momentum
        self.avg_vol = self.I(talib.SMA, volume, timeperiod=self.vol_period)  # Participation
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=self.atr_period)  # Volatility
        
        # Store entry ATR for fixed exits
        self.entry_atr = np.nan
        
        print("🌙 Optimized HolisticDecomposition initialized! Dimensions: EMA Trend (50/200), RSI, Volume, ATR ✨")
    
    def next(self):
        # Current values for synthesis
        current_price = self.data.Close[-1]
        current_rsi = self.rsi[-1]
        current_vol = self.data.Volume[-1]
        current_avg_vol = self.avg_vol[-1]
        current_atr = self.atr[-1]
        current_ema_short = self.ema_short[-1]
        current_ema_long = self.ema_long[-1]
        
        # Position sizing: Risk 1% of equity
        equity = self._broker._cash  # Use broker cash for accurate equity (includes positions)
        risk_amount = equity * self.risk_per_trade
        
        # Entry Rules: Multi-dimensional alignment (long/short symmetric)
        if not self.position:
            stop_distance = self.sl_mult * current_atr
            position_size = max(1, int(round(risk_amount / stop_distance)))  # Min size 1
            
            # Long: Uptrend alignment
            if (current_price > current_ema_short and 
                current_ema_short > current_ema_long and 
                current_rsi > self.rsi_long_threshold and 
                current_vol > self.vol_multiplier * current_avg_vol):
                
                self.buy(size=position_size)
                self.entry_atr = current_atr
                print(f"🚀 MOON ENTRY LONG at {current_price:.2f} | Size: {position_size} | RSI: {current_rsi:.1f} | Vol: {current_vol:.0f} ✨")
            
            # Short: Downtrend alignment (new)
            elif (current_price < current_ema_short and 
                  current_ema_short < current_ema_long and 
                  current_rsi < self.rsi_short_threshold and 
                  current_vol > self.vol_multiplier * current_avg_vol):
                
                self.sell(size=position_size)
                self.entry_atr = current_atr
                print(f"🔻 MOON ENTRY SHORT at {current_price:.2f} | Size: {position_size} | RSI: {current_rsi:.1f} | Vol: {current_vol:.0f} ✨")
        
        # Exit Rules: Fixed TP/SL only (no signal exits to let winners run)
        elif self.position:
            if np.isnan(self.entry_atr):
                self.entry_atr = self.atr[-1]  # Fallback (rare)
            
            entry_price = self.trades[-1].entry_price
            sl_dist = self.sl_mult * self.entry_atr
            tp_dist = self.rr_ratio * sl_dist
            
            if self.position.size > 0:  # Long position
                sl_price = entry_price - sl_dist
                tp_price = entry_price + tp_dist
                
                if current_price <= sl_price:
                    self.position.close()
                    print(f"🛑 MOON STOP LOSS LONG at {current_price:.2f} | Risk Managed 🚀")
                elif current_price >= tp_price:
                    self.position.close()
                    print(f"🎯 MOON TAKE PROFIT LONG at {current_price:.2f} | RR {self.rr_ratio}:1 🌙")
            
            else:  # Short position
                sl_price = entry_price + sl_dist
                tp_price = entry_price - tp_dist
                
                if current_price >= sl_price:
                    self.position.close()
                    print(f"🛑 MOON STOP LOSS SHORT at {current_price:.2f} | Risk Managed 🚀")
                elif current_price <= tp_price:
                    self.position.close()
                    print(f"🎯 MOON TAKE PROFIT SHORT at {current_price:.2f} | RR {self.rr_ratio}:1 🌙")

# Data cleaning function (as per rules)
def clean_data(data):
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    # Map to required columns (assuming input has 'datetime', 'open', etc.)
    data = data.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low', 
        'close': 'Close', 'volume': 'Volume'
    })
    return data

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
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index('datetime')
    data = clean_data(data)  # Apply cleaning
    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']  # Ensure proper casing

    bt = Backtest(data, HolisticDecomposition, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(HolisticDecomposition, 'HolisticDecomposition', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")