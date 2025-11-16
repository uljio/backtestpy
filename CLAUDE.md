# CLAUDE.md - Backtesting Repository Guide

**Last Updated:** 2025-11-16
**Purpose:** Comprehensive guide for AI assistants working with this algorithmic trading backtesting framework

---

## Repository Overview

This is a Python backtesting framework for algorithmic trading strategies using the `backtesting.py` library. The repository contains 6 distinct trading strategies designed primarily for cryptocurrency (BTC) and other financial instruments, with automated multi-data testing capabilities.

**Primary Use Case:** Developing, testing, and optimizing trading strategies with systematic risk management and comprehensive performance analysis.

---

## File Structure

### Current Files

```
backtestpy/
├── T03_FundingCrossover_DEBUG_v1.py      # EMA crossover with funding rate integration
├── T06_ConfluentOversold_DEBUG_v1.py     # Multiple oversold indicators confluence
├── T07_OpportunisticMaker_OPT_v2.py      # Market-making strategy with spread analysis
├── T09_NicheCostReversal_DEBUG_v1.py     # Mean reversion using Bollinger-style bands
├── T15_CorrelativeReversion_DEBUG_v2.py  # Z-score based mean reversion
├── T16_HolisticDecomposition_OPT_v3.py   # Multi-dimensional trend/momentum
├── XAUUSD_Strategy_Analysis.docx         # Strategy analysis documentation
└── XAUUSD_Strategy_Analysis_Enhanced.docx
```

### File Naming Convention

**Pattern:** `T##_StrategyName_MODE_v#.py`

- **T## Prefix**: Strategy identifier (T03, T06, T07, T09, T15, T16)
- **StrategyName**: Descriptive name in PascalCase
- **MODE Suffix**: Development stage
  - `DEBUG` = Development/debug version (more logging, initial testing)
  - `OPT` = Optimized version (tuned parameters, production-ready)
- **Version**: `v1`, `v2`, `v3` (incremental versions)

**Examples:**
- `T03_FundingCrossover_DEBUG_v1.py` - Initial debug version
- `T07_OpportunisticMaker_OPT_v2.py` - Optimized version 2

---

## Code Architecture

### Standard Strategy Structure

All strategies follow this **mandatory** pattern:

```python
# 1. IMPORTS
import pandas as pd
import talib
from backtesting import Strategy, Backtest
import numpy as np

# 2. STRATEGY CLASS
class StrategyName(Strategy):
    # Parameters as CLASS VARIABLES (NOT in __init__)
    risk_per_trade = 0.01
    ema_period = 20
    stop_loss_pct = 0.02

    def init(self):
        """Initialize indicators using self.I() wrapper"""
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.entry_price = None

    def next(self):
        """Main trading logic called on each bar"""
        if not self.position:
            # Entry logic
            if entry_conditions:
                size = self._calculate_position_size()
                self.buy(size=size)
        else:
            # Exit logic
            if exit_conditions:
                self.position.close()

    def _calculate_position_size(self):
        """Helper method for position sizing"""
        # Implementation
        pass

# 3. MAIN BLOCK
if __name__ == "__main__":
    # Load and clean data
    # Run backtest
    # Print stats
    # Multi-data testing
```

### Core Methods

#### `init()`
- Initialize **all** indicators using `self.I()` wrapper
- Initialize state variables (entry_price, entry_bar, etc.)
- **NEVER** calculate indicators directly
- Pattern: `self.indicator = self.I(talib.FUNCTION, data, params)`

#### `next()`
- Called on every bar during backtest
- Check position state first: `if not self.position:` vs `elif self.position:`
- Implement entry logic when flat
- Implement exit logic when in position
- Include debug prints with emojis

#### Helper Methods (Optional)
- Name with underscore prefix: `_calculate_position_size()`, `_reset_states()`
- Keep logic modular and reusable
- External data fetching: `fetch_funding_rates()` (T03)

---

## Dependencies

### Required Libraries

```python
import pandas as pd          # Data manipulation
import talib                 # Technical indicators
from backtesting import Strategy, Backtest
import numpy as np          # Numerical operations
import requests             # HTTP requests (for external data)
import sys, os              # Path manipulation
```

### External Framework

All strategies reference an external testing framework:

```python
sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-trading-bots/backtests')
from multi_data_tester import test_on_all_data
```

**Note:** This path is hardcoded. The `multi_data_tester` module is not in this repository.

### Installation

```bash
pip install pandas ta-lib backtesting numpy requests
```

---

## Key Conventions

### 1. Parameter Definition

**✅ CORRECT:**
```python
class MyStrategy(Strategy):
    risk_per_trade = 0.01  # 1% risk per trade
    ema_period = 20        # EMA lookback period
    stop_loss_pct = 0.02   # 2% stop loss
```

**❌ INCORRECT:**
```python
class MyStrategy(Strategy):
    def __init__(self):
        self.risk_per_trade = 0.01  # DON'T DO THIS
```

### 2. Indicator Registration

**✅ CORRECT:**
```python
def init(self):
    self.ema = self.I(talib.EMA, self.data.Close, timeperiod=20)
    self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
```

**❌ INCORRECT:**
```python
def next(self):
    ema = talib.EMA(self.data.Close, timeperiod=20)  # DON'T DO THIS
```

### 3. Data Access Patterns

```python
# Current bar
current_close = self.data.Close[-1]
current_ema = self.ema[-1]

# Previous bar
prev_close = self.data.Close[-2]
prev_ema = self.ema[-2]

# Check data availability
if len(self.data) < 50:
    return  # Not enough data
```

### 4. Position Sizing (Mandatory Pattern)

```python
def _calculate_position_size(self):
    """Risk-based position sizing"""
    equity = self.equity
    risk_amount = equity * self.risk_per_trade
    stop_distance = abs(entry_price - stop_price)
    position_size = risk_amount / stop_distance
    return max(1, int(round(position_size)))
```

### 5. Entry Logic Pattern

```python
if not self.position:
    # Multi-condition confluence
    condition1 = self.data.Close[-1] > self.ema[-1]
    condition2 = self.rsi[-1] > 50
    condition3 = self.data.Volume[-1] > self.vol_sma[-1]

    if condition1 and condition2 and condition3:
        size = self._calculate_position_size()
        self.buy(size=size)
        print(f"🌙 Long entry at {self.data.Close[-1]:.2f} 🚀")
```

### 6. Exit Logic Order (Critical)

```python
elif self.position:
    # 1. STOP LOSS (check first!)
    if self.data.Close[-1] <= self.stop_price:
        self.position.close()
        print(f"🌙🛑 STOP LOSS at {self.data.Close[-1]:.2f} ⚠️")
        return

    # 2. TAKE PROFIT
    if self.data.Close[-1] >= self.tp_price:
        self.position.close()
        print(f"🌙💰 TAKE PROFIT at {self.data.Close[-1]:.2f} 🎉")
        return

    # 3. SIGNAL-BASED EXIT
    if exit_signal:
        self.position.close()
        return

    # 4. TIME-BASED EXIT
    if len(self.data) - self.entry_bar >= self.max_bars:
        self.position.close()
        return
```

### 7. Debug Printing Convention

Use **Moon Dev Style** with emojis consistently:

```python
# Entry signals
print(f"🌙 Long entry at {price:.2f} 🚀")
print(f"🚀 MOON ENTRY LONG at {price:.2f} ✨")

# Exit signals
print(f"🌙💰 TAKE PROFIT at {price:.2f} 🎉")
print(f"🌙🛑 STOP LOSS at {price:.2f} ⚠️")

# Debug/monitoring
print(f"🔍 Monitoring: Vol {vol:.0f} 🌙")
print(f"📊 Z-score={z:.2f} ✨")
```

### 8. State Management

```python
def init(self):
    # Initialize state variables
    self.entry_price = None
    self.entry_bar = None
    self.max_high = None

def next(self):
    if not self.position:
        # ... entry logic ...
        self.entry_price = self.data.Close[-1]
        self.entry_bar = len(self.data)
        self.buy(size=size)

    elif self.position:
        # ... exit logic ...
        if exit_condition:
            self.position.close()
            self.entry_price = None  # Reset state
            self.entry_bar = None
```

---

## Data Handling

### Standard Data Cleaning Pattern

**Copy this pattern exactly for all new strategies:**

```python
# Load data
data = pd.read_csv('path/to/data.csv')

# Step 1: Normalize column names
data.columns = data.columns.str.strip().str.lower()

# Step 2: Remove unnamed columns
data = data.drop(columns=[col for col in data.columns
                          if 'unnamed' in col.lower()])

# Step 3: Rename to standard OHLCV (capitalized!)
data = data.rename(columns={
    'open': 'Open',
    'high': 'High',
    'low': 'Low',
    'close': 'Close',
    'volume': 'Volume'
})

# Step 4: Set datetime index
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime')

# Step 5: Drop NaN values
data = data.dropna()
```

### Primary Test Data

**Default path:** `/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv`

This is hardcoded in all existing strategies.

### NaN Handling

```python
# Check before using values
if np.isnan(self.indicator[-1]) or np.isnan(self.data.Close[-1]):
    return  # Skip this bar

# Check multiple values
if np.isnan([val1, val2, val3]).any():
    return
```

---

## Common Technical Indicators

### Trend Indicators
- **EMA** (Exponential Moving Average): `talib.EMA(close, timeperiod=20)`
- **SMA** (Simple Moving Average): `talib.SMA(close, timeperiod=50)`

### Momentum Indicators
- **RSI** (Relative Strength Index): `talib.RSI(close, timeperiod=14)`
- **CCI** (Commodity Channel Index): `talib.CCI(high, low, close, timeperiod=14)`
- **Stochastic**: `talib.STOCH(high, low, close, ...)`

### Volatility Indicators
- **ATR** (Average True Range): `talib.ATR(high, low, close, timeperiod=14)`
- **STDDEV** (Standard Deviation): `talib.STDDEV(close, timeperiod=20)`

### Volume Indicators
- **OBV** (On-Balance Volume): `talib.OBV(close, volume)`
- **Volume SMA**: `talib.SMA(volume, timeperiod=20)`

### Custom Indicators

```python
# Spread proxy
self.spread = self.I(lambda: (self.data.High - self.data.Low) / self.data.Close)

# Z-score
self.zscore = self.I(lambda: (self.data.Close - self.sma) / self.stddev)
```

---

## Risk Management Standards

### Position Sizing Formula

**Mandatory approach for all strategies:**

```python
equity = self.equity
risk_per_trade = 0.01  # 1% of equity at risk
risk_amount = equity * risk_per_trade
stop_distance = abs(entry_price - stop_loss_price)
position_size = risk_amount / stop_distance
position_size = max(1, int(round(position_size)))  # Ensure minimum size
```

### Common Parameters

| Parameter | Typical Value | Description |
|-----------|---------------|-------------|
| `risk_per_trade` | 0.01 | 1% of equity per trade |
| `stop_loss_pct` | 0.02-0.04 | 2-4% stop loss |
| `profit_target` | 0.04-0.075 | 4-7.5% take profit |
| `cash` | 1,000,000 | Starting capital |
| `commission` | 0.002 | 0.2% commission |

### Stop Loss Patterns

```python
# Fixed percentage stop
stop_price = entry_price * (1 - self.stop_loss_pct)

# ATR-based stop
stop_price = entry_price - (self.atr[-1] * self.sl_mult)

# Trailing stop
if self.position.is_long:
    self.max_high = max(self.max_high, self.data.High[-1])
    new_stop = self.max_high * (1 - self.trail_pct)
    self.stop_price = max(self.stop_price, new_stop)
```

---

## Testing & Backtesting

### Main Block Pattern

**Copy this structure for all strategies:**

```python
if __name__ == "__main__":
    # =================================================================
    # STEP 1: Load and clean data
    # =================================================================
    data_path = '/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv'
    data = pd.read_csv(data_path)

    # Clean data (use standard pattern above)
    # ... cleaning code ...

    # =================================================================
    # STEP 2: Run initial backtest
    # =================================================================
    print("\n🌙 Running initial backtest for stats extraction...")

    bt = Backtest(
        data,
        StrategyName,
        cash=1_000_000,
        commission=0.002
    )

    stats = bt.run()

    # =================================================================
    # STEP 3: Print statistics (Moon Dev's Format)
    # =================================================================
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print(stats._strategy)  # Optional: print strategy params
    print("="*80 + "\n")

    # =================================================================
    # STEP 4: Multi-data testing framework
    # =================================================================
    print("\n🌙 Starting multi-data testing framework...")
    sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-trading-bots/backtests')
    from multi_data_tester import test_on_all_data

    results = test_on_all_data(
        StrategyName,
        'StrategyName',
        verbose=False  # Prevent plotting timeouts
    )
```

### Backtest Configuration

```python
bt = Backtest(
    data,                    # Cleaned DataFrame with OHLCV
    StrategyClass,           # Strategy class (NOT instance)
    cash=1_000_000,          # Starting capital
    commission=0.002,        # 0.2% commission
    exclusive_orders=True    # Cancel pending orders on new signal
)
```

---

## Strategy Types

### 1. Long-Only Strategies
**Examples:** T03, T06, T09

```python
def next(self):
    if not self.position:
        if long_conditions:
            self.buy(size=size)
    elif self.position:
        if exit_conditions:
            self.position.close()
```

### 2. Long/Short Strategies
**Examples:** T07, T15, T16

```python
def next(self):
    if not self.position:
        if long_conditions:
            self.buy(size=size)
        elif short_conditions:
            self.sell(size=size)
    elif self.position.is_long:
        if long_exit_conditions:
            self.position.close()
    elif self.position.is_short:
        if short_exit_conditions:
            self.position.close()
```

### 3. Market Making (T07)
**Unique pattern: Simultaneous limit orders**

```python
# Place limit orders on both sides
self.buy(limit=bid_price, size=size, sl=buy_sl, tp=buy_tp)
self.sell(limit=ask_price, size=size, sl=sell_sl, tp=sell_tp)
```

---

## Development Workflow

### Creating a New Strategy

1. **Choose naming**: Follow `T##_StrategyName_DEBUG_v1.py` convention
2. **Copy structure**: Use existing strategy as template
3. **Define parameters**: Add as class variables
4. **Implement `init()`**: Register indicators with `self.I()`
5. **Implement `next()`**: Entry and exit logic
6. **Add position sizing**: Use risk-based formula
7. **Add debug prints**: Use moon/rocket emojis
8. **Test locally**: Run on BTC-USD-15m.csv
9. **Multi-data test**: Use `test_on_all_data()`
10. **Optimize**: Move to `_OPT_` version when ready

### Modifying Existing Strategy

1. **Read the file first** to understand current logic
2. **Preserve structure** - don't break the pattern
3. **Test changes** on standard dataset
4. **Update version** if significant changes (v1 → v2)
5. **Keep debug prints** for troubleshooting

### Debugging Checklist

- [ ] Are parameters defined as class variables?
- [ ] Are indicators registered with `self.I()` in `init()`?
- [ ] Is position sizing implemented correctly?
- [ ] Are stop losses checked before take profit?
- [ ] Are state variables reset on exit?
- [ ] Are NaN values handled?
- [ ] Are debug prints included?
- [ ] Does data cleaning follow standard pattern?

---

## Strategy Comparison

| Strategy | Type | Entry Signal | Exit Signal | Unique Feature |
|----------|------|--------------|-------------|----------------|
| **T03** | Trend | EMA crossover + volume | SL/TP, time-based | Binance funding rate integration |
| **T06** | Reversal | Stoch + CCI + OBV oversold | SL/TP, divergence | OBV divergence detection |
| **T07** | Market Making | Volume spike + low vol | ATR-based dynamic | Dual limit orders |
| **T09** | Reversal | Price beyond bands | SL/TP, band cross | Bollinger-style bands |
| **T15** | Reversal | Z-score extremes | SL/TP, z-score neutral | Statistical mean reversion |
| **T16** | Trend/Momentum | Multi-EMA + RSI + ATR | Dynamic ATR-based | Multi-dimensional signals |

---

## Common Pitfalls to Avoid

### ❌ Don't Do This

1. **Defining parameters in `__init__`**
   ```python
   def __init__(self):
       self.ema_period = 20  # WRONG!
   ```

2. **Calculating indicators in `next()`**
   ```python
   def next(self):
       ema = talib.EMA(self.data.Close, 20)  # WRONG!
   ```

3. **Forgetting position sizing**
   ```python
   self.buy()  # WRONG - no size specified!
   ```

4. **Checking take profit before stop loss**
   ```python
   if profit_hit:  # WRONG - check stops first!
       # ...
   elif stop_hit:
       # ...
   ```

5. **Not resetting state variables**
   ```python
   self.position.close()
   # self.entry_price = None  # FORGOT TO RESET!
   ```

### ✅ Do This Instead

1. Class-level parameters
2. `self.I()` wrapper for indicators
3. Risk-based position sizing
4. Stop loss checked first
5. Reset states on exit

---

## Quick Reference

### Essential Code Snippets

**Strategy Template:**
```python
class MyStrategy(Strategy):
    # Parameters
    risk_per_trade = 0.01

    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.entry_price = None

    def next(self):
        if not self.position:
            # Entry
            pass
        else:
            # Exit
            pass
```

**Position Sizing:**
```python
size = max(1, int(round((self.equity * 0.01) / stop_distance)))
```

**Data Cleaning:**
```python
data.columns = data.columns.str.strip().str.lower()
data = data.drop(columns=[c for c in data.columns if 'unnamed' in c.lower()])
data = data.rename(columns={'open':'Open', 'high':'High', 'low':'Low',
                            'close':'Close', 'volume':'Volume'})
data['datetime'] = pd.to_datetime(data['datetime'])
data = data.set_index('datetime').dropna()
```

---

## External Dependencies Notes

### Multi-Data Tester Path
```python
sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-trading-bots/backtests')
from multi_data_tester import test_on_all_data
```

**Important:** This external module is referenced but not included in this repository.

### Default Data Path
```
/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv
```

**Important:** These paths are hardcoded. Update if repository is moved or used in different environment.

---

## Git Workflow

### Current Branch
- Working branch: `claude/claude-md-mi20o6fvq2zjrhqs-016bq2RL18RGLxAhhQiJDUWg`
- All commits should go to this branch

### Commit Guidelines
- Use descriptive commit messages
- Include strategy name/number in message
- Example: "Add T17 momentum strategy - DEBUG v1"
- Example: "Optimize T07 position sizing - OPT v3"

### Push Command
```bash
git push -u origin claude/claude-md-mi20o6fvq2zjrhqs-016bq2RL18RGLxAhhQiJDUWg
```

---

## For AI Assistants: Critical Reminders

1. **ALWAYS** read existing strategy files before creating new ones
2. **NEVER** break the established code structure pattern
3. **ALWAYS** use risk-based position sizing
4. **ALWAYS** check stop loss before take profit
5. **ALWAYS** use `self.I()` for indicators
6. **ALWAYS** define parameters as class variables
7. **ALWAYS** include moon/rocket emoji debug prints
8. **ALWAYS** follow the data cleaning pattern exactly
9. **ALWAYS** test on BTC-USD-15m.csv first
10. **ALWAYS** include multi-data testing framework in main block

### When in Doubt
- Copy the structure from an existing strategy
- Maintain consistency with the codebase
- Ask the user before making structural changes
- Test thoroughly before committing

---

## Contact & Support

For issues or questions about this codebase, refer to the strategy documentation or contact the repository maintainer.

**Last Updated:** 2025-11-16
**Maintained by:** Moon Dev (inferred from emoji style and paths)
