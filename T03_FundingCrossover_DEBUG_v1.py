import pandas as pd
import talib
import requests
from backtesting import Strategy, Backtest

class FundingCrossover(Strategy):
    ema_period = 20
    volume_mult = 1.5
    risk_per_trade = 0.01
    trail_percent = 0.02
    tp_percent = 0.04
    max_hold_bars = 8

    def init(self):
        self.i = 0
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.avg_vol = self.I(talib.SMA, self.data.Volume, timeperiod=self.ema_period)
        
        try:
            self.funding = self.data.FundingRate
            self.has_funding = True
            print("🌙 Funding rate data loaded successfully! 🚀")
        except AttributeError:
            self.funding = None
            self.has_funding = False
            print("⚠️ No funding rate data available, skipping funding condition. 🌙")

    def next(self):
        # Update max_high if in position
        if self.position:
            current_high = self.data.High[self.i]
            if hasattr(self, 'max_high'):
                self.max_high = max(self.max_high, current_high)
            else:
                self.max_high = max(self.entry_price, current_high)
            
            trail_stop = self.max_high * (1 - self.trail_percent)
            
            # Trailing stop check using Low
            if self.data.Low[self.i] <= trail_stop:
                self.position.close()
                print(f"🌙 Trailing stop hit at Low {self.data.Low[self.i]:.2f} (trail: {trail_stop:.2f}) 🚀")
                self.i += 1
                return
            
            # Take profit check
            if hasattr(self, 'entry_price') and self.data.Close[self.i] >= self.entry_price * (1 + self.tp_percent):
                self.position.close()
                print(f"🌙 Take profit hit at {self.data.Close[self.i]:.2f} ✨")
                self.i += 1
                return
            
            # Emergency exit if funding turns positive
            if self.has_funding and self.funding[self.i] > 0:
                self.position.close()
                print(f"🌙 Funding turned positive ({self.funding[self.i]:.4f}), emergency exit! 🚨")
                self.i += 1
                return
            
            # Time-based exit (approx 8 hours)
            if hasattr(self, 'entry_bar') and self.i - self.entry_bar >= self.max_hold_bars:
                self.position.close()
                print(f"🌙 Time-based exit after {self.max_hold_bars} hours 🌙")
                self.i += 1
                return

            self.i += 1
            return

        # Entry logic (long only)
        else:
            if self.i < self.ema_period:
                self.i += 1
                return
            
            if self.i < 1:
                self.i += 1
                return
            
            price_cross = (self.data.Close[self.i - 1] < self.ema[self.i - 1] and self.data.Close[self.i] > self.ema[self.i])
            vol_condition = self.data.Volume[self.i] > self.avg_vol[self.i] * self.volume_mult
            
            funding_condition = True
            if self.has_funding and self.i > 0:
                funding_condition = (self.funding[self.i] < 0) and (self.funding[self.i - 1] >= 0)
                print(f"🌙 Funding check: current {self.funding[self.i]:.4f}, prev {self.funding[self.i - 1]:.4f} 📊")
            
            if price_cross and vol_condition and funding_condition:
                # Position sizing based on risk
                price = self.data.Close[self.i]
                risk_amount = self.equity * self.risk_per_trade
                stop_distance = price * self.trail_percent
                pos_size = risk_amount / stop_distance  # in BTC units
                pos_size = int(round(pos_size))
                
                if pos_size > 0:
                    self.buy(size=pos_size)
                    self.entry_price = price
                    self.max_high = price
                    self.entry_bar = self.i
                    funding_msg = f" (funding: {self.funding[self.i]:.4f})" if self.has_funding else ""
                    print(f"🌙 Long entry at {price:.2f}, size {pos_size}, EMA cross confirmed{ funding_msg } 🚀 Volume: {self.data.Volume[self.i]:.2f} > avg {self.avg_vol[self.i]*self.volume_mult:.2f}")
                else:
                    print("⚠️ Calculated position size too small, skipping entry. 🌙")

            self.i += 1

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    def fetch_funding_rates(symbol='BTCUSDT', start_time=None, end_time=None):
        if start_time is None or end_time is None:
            return pd.DataFrame()
        url = 'https://fapi.binance.com/fapi/v1/fundingRate'
        params = {
            'symbol': symbol,
            'startTime': int(start_time.timestamp() * 1000),
            'endTime': int(end_time.timestamp() * 1000),
            'limit': 1000
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data_list = response.json()
            if not data_list:
                return pd.DataFrame()
            df = pd.DataFrame(data_list)
            df['fundingTime'] = pd.to_datetime(df['fundingTime'], unit='ms')
            df = df.set_index('fundingTime')
            df['fundingRate'] = df['fundingRate'].astype(float)
            return df
        except Exception as e:
            print(f"❌ Error fetching funding rates: {e}")
            return pd.DataFrame()

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data['datetime'] = pd.to_datetime(data['datetime'])
    data = data.set_index(data['datetime'])

    # Resample to 1h
    data = data.resample('1H').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last',
        'Volume': 'sum'
    }).dropna()

    # Fetch and merge funding rates
    try:
        start = data.index.min()
        end = data.index.max()
        funding_df = fetch_funding_rates(start_time=start, end_time=end)
        if not funding_df.empty:
            funding_1h = funding_df.reindex(data.index, method='ffill')['fundingRate']
            data['FundingRate'] = funding_1h.fillna(0.0)
            print(f"🌙 Funding rates fetched and merged for {len(funding_df)} periods! 🚀")
        else:
            print("⚠️ No funding data fetched, skipping funding condition. 🌙")
    except Exception as e:
        print(f"❌ Failed to process funding rates: {e}")

    bt = Backtest(data, FundingCrossover, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(FundingCrossover, 'FundingCrossover', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")