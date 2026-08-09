"""
Configuration file for NIFTY 50 Algo Trader
"""

# Trading Parameters
INITIAL_CAPITAL = 100000  # Starting capital in INR
SYMBOL = "^NSEI"  # Yahoo Finance ticker for NIFTY 50

# Strategy Parameters
FAST_SMA = 20          # Fast moving average period
SLOW_SMA = 50          # Slow moving average period
RSI_PERIOD = 14        # RSI calculation period
RSI_OVERBOUGHT = 70    # RSI overbought threshold
RSI_OVERSOLD = 30      # RSI oversold threshold

# Risk Management
MAX_RISK_PERCENT = 2.0        # Max risk per trade (% of capital)
MAX_POSITION_SIZE = 5.0       # Max position size (% of capital)
MAX_DRAWDOWN_PERCENT = 10.0   # Maximum allowed drawdown

# Backtest Parameters
BACKTEST_DAYS = 730  # Number of days to backtest
BACKTEST_INTERVAL = '1d'  # Data interval ('1d', '1h', '5m', etc.)

# Stop Loss & Take Profit
STOP_LOSS_PERCENT = 2.0   # Stop loss as % below entry
TAKE_PROFIT_PERCENT = 5.0  # Take profit as % above entry

# Logging
LOG_FILE = "trading.log"
RESULTS_FILE = "backtest_results.json"
TRADES_CSV = "trades.csv"
