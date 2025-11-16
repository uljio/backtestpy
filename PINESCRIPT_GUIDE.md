# PineScript Strategy Conversion Guide

This document explains how to use the converted PineScript strategies in TradingView.

## Overview

All 6 Python backtesting strategies have been converted to PineScript v5 for use in TradingView. The strategies maintain the same core logic, risk management, and entry/exit conditions as their Python counterparts.

## Converted Strategies

| Strategy | File | Type | Description |
|----------|------|------|-------------|
| **T03** | `T03_FundingCrossover.pine` | Trend | EMA crossover with volume confirmation |
| **T06** | `T06_ConfluentOversold.pine` | Reversal | Multi-indicator oversold confluence |
| **T07** | `T07_OpportunisticMaker.pine` | Market Making | Dual limit orders during liquidity events |
| **T09** | `T09_NicheCostReversal.pine` | Reversal | Bollinger-style mean reversion |
| **T15** | `T15_CorrelativeReversion.pine` | Reversal | Z-score statistical mean reversion |
| **T16** | `T16_HolisticDecomposition.pine` | Trend/Momentum | Multi-dimensional EMA + RSI strategy |

## How to Use in TradingView

### Step 1: Open TradingView
1. Go to https://www.tradingview.com
2. Open the chart for your desired instrument (e.g., BTC/USD, ETH/USD)
3. Set the timeframe (strategies were tested on 15m, but can be used on other timeframes)

### Step 2: Open Pine Editor
1. Click on "Pine Editor" at the bottom of the screen
2. Click "Open" → "New blank indicator"

### Step 3: Load Strategy
1. Copy the entire contents of any `.pine` file from this repository
2. Paste into the Pine Editor
3. Click "Save" and give it a name
4. Click "Add to Chart"

### Step 4: Configure Parameters
Each strategy has configurable input parameters that can be adjusted:
- Click the gear icon next to the strategy name on the chart
- Adjust parameters in the "Inputs" tab
- Click "OK" to apply changes

### Step 5: View Results
- The "Strategy Tester" tab at the bottom shows:
  - Net Profit
  - Total Trades
  - Win Rate
  - Drawdown
  - Sharpe Ratio
  - And more...

## Key Differences from Python Version

### 1. Funding Rate Data (T03)
**Python:** Fetched from Binance API
**PineScript:** Not available in standard TradingView
**Solution:** The funding rate condition has been removed. To use funding rates, you need to:
- Use Binance data feed in TradingView
- Or manually add funding rate as an external indicator

### 2. Position Sizing
**Python:** Uses `size` in units of the asset
**PineScript:** Uses `qty` parameter in strategy.entry()
- Both calculate position size based on risk percentage
- PineScript automatically handles position sizing if you use `default_qty_type=strategy.cash`

### 3. Multi-Data Testing
**Python:** Automatically tests on 25+ data sources
**PineScript:** You need to manually test on different instruments
**Tip:** Use TradingView's "Deep Backtesting" feature (premium) for longer historical data

### 4. Commission
**Python:** 0.2% (0.002)
**PineScript:** 0.2% (commission_value=0.2)
- Both strategies use the same commission structure

## Strategy-Specific Notes

### T03 - Funding Crossover
- Uses EMA crossover + volume spike
- Trailing stop implementation
- Time-based exit after 8 hours (bars)
- **Best for:** Trending crypto markets

### T06 - Confluent Oversold
- Multiple oversold indicators (Stochastic, CCI, Volume)
- OBV divergence detection
- Breakeven trailing
- **Best for:** Range-bound markets with clear oversold bounces

### T07 - Opportunistic Maker
- Places both long and short limit orders simultaneously
- Uses ADX for ranging market filter
- ATR-based dynamic stops
- **Best for:** Low volatility, ranging markets
- **Note:** May have many simultaneous positions

### T09 - Niche Cost Reversal
- Bollinger-style bands with EMA + StdDev
- RSI oversold confirmation
- Mean reversion exit at EMA
- **Best for:** Volatile markets with strong mean reversion

### T15 - Correlative Reversion
- Pure Z-score statistical approach
- Both long and short
- Symmetric entry/exit levels
- **Best for:** Assets with strong mean-reverting characteristics
- **Note:** Includes Z-score plot in separate panel

### T16 - Holistic Decomposition
- Multi-dimensional: EMA trend + RSI momentum + Volume + ATR
- 3:1 risk-reward ratio
- Both long and short based on trend alignment
- **Best for:** Trending markets (BTC, ETH, volatile assets)

## Risk Management

All strategies implement the same risk management principles:

### Position Sizing Formula
```
risk_amount = equity × risk_per_trade
stop_distance = entry_price × stop_loss_percentage (or ATR-based)
position_size = risk_amount / stop_distance
```

### Default Risk Parameters
- **Risk per trade:** 1% (0.01) of equity
- **Stop loss:** 2-4% or 1.5-2.0 × ATR
- **Take profit:** 4-7.5% or 2-3 × ATR
- **Initial capital:** $1,000,000

### Adjusting for Your Account
If your account is smaller (e.g., $10,000), adjust:
1. Set `initial_capital=10000` in the strategy declaration
2. Keep risk_per_trade at 0.01 (1%) for proper risk management
3. Test thoroughly before live trading

## Backtesting Best Practices

### 1. Use Sufficient Historical Data
- Minimum: 6 months of data
- Recommended: 2+ years for robust statistics
- TradingView Premium: Access to more historical data

### 2. Test on Multiple Instruments
Each strategy performs differently on:
- **Crypto:** BTC, ETH, SOL (high volatility)
- **Forex:** EUR/USD, GBP/USD (lower volatility)
- **Stocks:** AAPL, TSLA, NVDA (medium volatility)
- **Indices:** SPX, NDX (trending behavior)

### 3. Test on Multiple Timeframes
- Original: 15-minute (15m)
- Also test: 5m, 1h, 4h, 1D
- Higher timeframes = fewer trades, more reliable signals
- Lower timeframes = more trades, more noise

### 4. Watch for Overfitting
- If performance is "too good to be true," it probably is
- Check maximum drawdown (should be < 20-30%)
- Check win rate (50-60% is realistic for mean reversion, 40-50% for trend following)
- Verify profit factor > 1.5

### 5. Commission & Slippage
- Default: 0.2% commission
- Add slippage in Strategy Properties → "Slippage" (1-3 ticks recommended)
- For crypto: Consider 0.4% total costs (0.2% entry + 0.2% exit)

## Parameter Optimization

### Using TradingView's Strategy Optimizer
1. Right-click on the strategy in the chart
2. Select "Strategy Tester" → "Optimization"
3. Select parameters to optimize
4. Choose optimization criteria (Net Profit, Sharpe Ratio, etc.)
5. Run optimization

### Recommended Parameters to Optimize
- **T03:** ema_period, volume_mult, trail_percent
- **T06:** stoch_oversold, cci_oversold, profit_target
- **T07:** vol_mult, adx_threshold, sl_mult
- **T09:** std_mult, rsi_oversold, max_hold_bars
- **T15:** lookback, entry_z, exit_z
- **T16:** ema_short_period, rsi_long_threshold, rr_ratio

### Warning: Avoid Over-Optimization
- Don't optimize too many parameters at once (max 2-3)
- Use walk-forward analysis
- Verify optimized parameters on out-of-sample data

## Visual Features

All strategies include:
- **Labels:** Entry and exit markers with emojis (🌙🚀💰🛑)
- **Plots:** Key indicators (EMAs, bands, etc.) on the chart
- **Colors:**
  - Green = Long entry
  - Red = Short entry/Stop loss
  - Blue = Take profit
  - Orange = Time exit
  - Purple = Special exits (divergence, maker orders)

## Troubleshooting

### Issue: No trades appearing
**Solutions:**
- Check if there's sufficient historical data
- Verify parameters aren't too restrictive
- Check if initial_capital is set correctly
- Ensure the instrument has volume data

### Issue: Too many trades
**Solutions:**
- Increase entry thresholds (e.g., higher RSI, Z-score)
- Add more confluence conditions
- Increase minimum bars between trades

### Issue: Poor performance
**Solutions:**
- Test on different timeframes
- Optimize parameters for the specific instrument
- Check if the market regime matches the strategy type
- Verify commission/slippage settings are realistic

### Issue: Strategy won't compile
**Solutions:**
- Ensure you're using PineScript v5 (check `//@version=5` at top)
- Check for syntax errors in Pine Editor
- Verify all brackets and parentheses are closed
- Clear the editor and re-paste the code

## Comparison with Python Results

Python backtests used:
- **Data:** BTC-USD 15-minute bars
- **Period:** Multiple years of historical data
- **Framework:** backtesting.py library
- **Multi-data testing:** 25+ instruments

PineScript backtests should show similar patterns but may differ due to:
- Different historical data sources
- TradingView's bar replay vs. tick-by-tick
- Funding rate availability (T03)
- Exchange-specific data quirks

**Recommendation:** Compare results on the same date range using BTC/USD 15m data.

## Next Steps

1. **Paper Trading:** Test strategies in TradingView's paper trading mode before live trading
2. **Live Testing:** Start with small position sizes
3. **Monitor Performance:** Track actual vs. backtested results
4. **Iterate:** Adjust parameters based on live performance
5. **Combine Strategies:** Consider portfolio approach using multiple strategies

## Support & Resources

- **PineScript Documentation:** https://www.tradingview.com/pine-script-docs/
- **TradingView Community:** https://www.tradingview.com/scripts/
- **Strategy Testing Tutorial:** https://www.tradingview.com/support/solutions/43000481029/

## Disclaimer

These strategies are for educational and research purposes only. Past performance does not guarantee future results. Always:
- Test thoroughly on historical data
- Use proper risk management
- Start with paper trading
- Never risk more than you can afford to lose
- Consult with a financial advisor before live trading

---

**Last Updated:** 2025-11-16
**Converted by:** Claude AI Assistant
**Original Python Strategies by:** Moon Dev
