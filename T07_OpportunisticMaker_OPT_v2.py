import pandas as pd
import numpy as np
import talib
from backtesting import Strategy, Backtest

def calc_spread(high, low, close):
    """Calculate spread proxy: (High - Low) / Close"""
    return (high - low) / close

class OpportunisticMaker(Strategy):
    vol_mult = 1.5  # 🌙 Reduced from 2.0 for more frequent but still significant volume spikes
    atr_period = 14
    atr_threshold = 0.005  # 🌙 Tightened from 0.01 for stricter low volatility filter (0.5% of price)
    spread_mult = 1.1  # 🌙 Reduced from 1.2 to catch earlier spread widening without overfiltering
    limit_offset_mult = 0.5  # 🌙 New: ATR multiple for limit offset to place orders closer for better fill rates
    sl_mult = 1.0  # 🌙 New: ATR multiple for stop loss (adaptive to volatility)
    tp_mult = 2.0  # 🌙 New: ATR multiple for take profit (improved 1:2 R:R for higher returns)
    risk_pct = 0.005  # 🌙 Changed to risk-based sizing: 0.5% equity risk per side (better risk management)
    max_concurrent = 5
    vol_sma_period = 20
    spread_sma_period = 20
    adx_period = 14  # 🌙 New: For ADX to filter ranging markets
    adx_threshold = 25  # 🌙 New: Only trade if ADX < 25 (ranging market regime filter)
    min_bars = 50

    def init(self):
        print("🌙 Initializing Optimized OpportunisticMaker Strategy ✨")
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)  # 🌙 Added ADX for market regime filter
        self.vol_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_sma_period)
        self.spread_proxy = self.I(calc_spread, self.data.High, self.data.Low, self.data.Close)
        self.avg_spread = self.I(talib.SMA, self.spread_proxy, timeperiod=self.spread_sma_period)
        print("🚀 Indicators loaded: ATR, ADX, Volume SMA, Spread Proxy 🌙")  # 🌙 Updated print for new indicator

    def next(self):
        if len(self.data) < self.min_bars:
            return

        curr_price = self.data.Close[-1]
        current_vol = self.data.Volume[-1]
        avg_vol = self.vol_sma[-1]
        curr_atr = self.atr[-1]
        curr_adx = self.adx[-1]  # 🌙 New: ADX value
        curr_spread = self.spread_proxy[-1]
        avg_sp = self.avg_spread[-1]

        # Check for NaNs
        if np.isnan([current_vol, avg_vol, curr_atr, curr_adx, curr_spread, avg_sp]).any():
            return

        # 🌙 Optimized Entry conditions: Added ranging market filter, tightened thresholds for better setups
        vol_spike = current_vol > self.vol_mult * avg_vol
        low_vol = (curr_atr / curr_price) < self.atr_threshold
        widening_spread = curr_spread > self.spread_mult * avg_sp
        ranging_market = curr_adx < self.adx_threshold  # 🌙 New: Only enter in low ADX (ranging) conditions to avoid trends

        if len(self.trades) >= self.max_concurrent:
            print(f"⚠️ Max concurrent trades reached: {len(self.trades)}/ {self.max_concurrent} 💼")
            return

        if vol_spike and low_vol and widening_spread and ranging_market:  # 🌙 Added ranging_market to filter for favorable maker conditions
            print(f"🌙 Liquidity demand detected! Vol spike: {vol_spike}, Low vol: {low_vol}, Spread: {curr_spread:.4f} vs avg {avg_sp:.4f}, Ranging: {ranging_market} 🚀")

            # 🌙 Optimized Position sizing: Risk-based using ATR-derived SL distance for consistent risk per trade
            sl_dist = self.sl_mult * curr_atr
            risk_amount = self.equity * self.risk_pct
            size_per_side = risk_amount / sl_dist  # 🌙 Size = risk / SL_distance (volatility-adjusted, ignores price for relative risk)
            size_per_side = round(size_per_side / curr_price, 4)  # 🌙 Normalize to fraction of price, round for precision

            if size_per_side <= 0:
                print("⚠️ Invalid size calculated, skipping entry 📉")
                return

            # 🌙 Dynamic limit prices: Use ATR-based offset instead of fixed tick for adaptability
            limit_offset = self.limit_offset_mult * curr_atr
            bid_price = curr_price - limit_offset
            ask_price = curr_price + limit_offset

            # 🌙 Dynamic SL and TP: ATR-based for better risk:reward in varying volatility
            tp_dist = self.tp_mult * curr_atr

            # Place bid (long limit order)
            self.buy(
                limit=bid_price,
                size=size_per_side,
                sl=bid_price - sl_dist,
                tp=bid_price + tp_dist
            )
            print(f"📈 Placed BID (long) limit at {bid_price:.2f}, size: {size_per_side:.4f} BTC, SL: {sl_dist:.2f}, TP: {tp_dist:.2f} 🌙")

            # Place ask (short limit order)
            self.sell(
                limit=ask_price,
                size=size_per_side,
                sl=ask_price + sl_dist,
                tp=ask_price - tp_dist
            )
            print(f"📉 Placed ASK (short) limit at {ask_price:.2f}, size: {size_per_side:.4f} BTC, SL: {sl_dist:.2f}, TP: {tp_dist:.2f} ✨")

            print(f"💰 Risk per side: {risk_amount:.2f} USD, Total setup risk: ~{risk_amount*2:.2f} USD 🚀")
        else:
            # Optional debug (enhanced with ADX)
            if current_vol > avg_vol:
                print(f"🔍 Monitoring: Vol {current_vol:.0f} (avg {avg_vol:.0f}), ATR {curr_atr:.2f} ({(curr_atr/curr_price)*100:.2f}%), Spread {curr_spread:.4f}, ADX {curr_adx:.1f} 🌙")

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
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data.columns = [col.capitalize() for col in data.columns]
    data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']

    bt = Backtest(data, OpportunisticMaker, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(OpportunisticMaker, 'OpportunisticMaker', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")