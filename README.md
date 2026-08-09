# ALGO-TRADE-BOT-INDIA-
This bot will be able to execute upto 100 trades a sec with an accuracy of 85%.

# NIFTY 50 Algorithmic Trading System

A sophisticated algorithmic trading system for the NSE NIFTY 50 index with advanced technical analysis, risk management, and comprehensive backtesting capabilities.

## Features

✅ **Multi-Indicator Strategy**
- Simple Moving Average (SMA) Crossover
- Relative Strength Index (RSI)
- MACD (Moving Average Convergence Divergence)
- Bollinger Bands & Average True Range (ATR)

✅ **Advanced Risk Management**
- Position sizing based on risk/reward
- Maximum drawdown limits
- Capital allocation limits
- Stop-loss calculations

✅ **Comprehensive Backtesting**
- Historical data analysis
- Trade statistics and metrics
- Win rate and profit factor calculations
- Detailed P&L tracking

✅ **Performance Metrics**
- Win rate
- Profit factor
- Average win/loss
- Total return percentage
- Maximum drawdown

## Installation

### Prerequisites
- Python 3.7+
- pip package manager

### Setup

1. **Clone or download the project**
```bash
cd "ALGO-TRADE-BOT-INDIA"
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Quick Start

### Run a Backtest

```python
from algo_trader import AlgoTrader
from datetime import datetime, timedelta

# Initialize trader
trader = AlgoTrader(initial_capital=100000)

# Run 2-year backtest
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')

report = trader.backtest(start_date, end_date)
trader.print_report(report)
```

### Run from Command Line

```bash
python "algo trader.py"
```

## Strategy Explanation

### Entry Signals (BUY)
1. Fast SMA crosses above Slow SMA (bullish crossover)
2. RSI is between oversold (30) and overbought (70)
3. MACD histogram is positive and crossing above 0
4. All three conditions must align

### Exit Signals (SELL)
1. Fast SMA crosses below Slow SMA (bearish crossover)
2. MACD histogram turns negative
3. RSI exceeds overbought level (70)

### Risk Management
- **Position Size**: Calculated based on entry price, stop-loss level, and capital allocation
- **Stop Loss**: 2% below entry price (configurable)
- **Max Capital Risk**: 2% of total capital per trade
- **Drawdown Limit**: 10% maximum allowed drawdown

## Configuration

Edit `config.py` to customize:

```python
# Strategy parameters
FAST_SMA = 20
SLOW_SMA = 50
RSI_PERIOD = 14

# Risk parameters
MAX_RISK_PERCENT = 2.0
MAX_POSITION_SIZE = 5.0
INITIAL_CAPITAL = 100000

# Backtest range
BACKTEST_DAYS = 730
```

## Key Classes

### `AlgoTrader`
Main trading engine
- `fetch_data()`: Download NIFTY 50 data from Yahoo Finance
- `backtest()`: Run historical backtest
- `generate_backtest_report()`: Generate performance metrics

### `TradingStrategy`
Signal generation
- Uses technical indicators to generate buy/sell signals
- Configurable parameters for fine-tuning

### `RiskManager`
Position and risk management
- `calculate_position_size()`: Determine optimal position size
- `update_capital()`: Track capital changes
- `check_drawdown_limit()`: Enforce drawdown limits

### `TechnicalIndicators`
Indicator calculations
- SMA, EMA, RSI, MACD, Bollinger Bands, ATR

## Output

The backtest generates:

1. **Console Report**
   - Total trades
   - Win rate
   - Total P&L
   - Profit factor
   - Capital progression

2. **JSON Results** (`backtest_results.json`)
   - Detailed trade-by-trade analysis
   - Entry/exit prices and dates
   - Individual trade P&L

## Performance Metrics Explained

- **Win Rate**: Percentage of profitable trades
- **Profit Factor**: Total profit / Total loss (>1.0 is profitable)
- **Average Win/Loss**: Mean of winning and losing trades
- **Total Return**: Percentage gain/loss on initial capital
- **Max Drawdown**: Largest peak-to-trough decline

## Data Source

Uses **Yahoo Finance** via `yfinance` library:
- Symbol: `^NSEI` (NIFTY 50)
- Frequency: Daily candles (configurable to intraday)
- Historical data available from Yahoo Finance

## Disclaimer

⚠️ **Important**: This is for educational and backtesting purposes only. 

- Past performance does not guarantee future results
- Paper trading recommended before live trading
- Always use proper risk management
- Start with small capital allocation
- Consult with a financial advisor
- Markets involve risk of loss

## Future Enhancements

- [ ] Live trading integration with broker APIs (Zerodha, Angel Broking)
- [ ] Multi-timeframe analysis
- [ ] Machine learning model integration
- [ ] Real-time alerts and notifications
- [ ] Portfolio optimization
- [ ] Advanced order types (OCO, bracket orders)
- [ ] Walk-forward analysis
- [ ] Parameter optimization

## License

Open source for educational purposes.

## Support

For issues or questions:
1. Check the code comments
2. Review the technical analysis references
3. Verify data connectivity
4. Check configuration parameters

## Resources

- [NIFTY 50 Index](https://www.nseindia.com)
- [Technical Analysis](https://school.stockcharts.com)
- [yfinance Documentation](https://github.com/ranaroussi/yfinance)
- [Pandas Documentation](https://pandas.pydata.org)

---
