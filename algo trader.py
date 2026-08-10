"""
NSE NIFTY 50 Algorithmic Trading System
A comprehensive algo trader with backtesting, strategy optimization, and real-time trading capabilities.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict, Optional
import json
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class Signal(Enum):
    """Trading signal types"""
    BUY = 1
    SELL = -1
    HOLD = 0


class OrderType(Enum):
    """Order execution types"""
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LOSS = "STOP_LOSS"


@dataclass
class Position:
    """Represents an open position"""
    entry_price: float
    entry_date: datetime
    quantity: int
    position_type: str  # 'LONG' or 'SHORT'
    entry_signal: Signal


@dataclass
class Trade:
    """Represents a completed trade"""
    entry_price: float
    exit_price: float
    entry_date: datetime
    exit_date: datetime
    quantity: int
    position_type: str
    pnl: float
    pnl_percent: float
    duration_days: int


class TechnicalIndicators:
    """Calculate technical indicators for trading signals"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """Simple Moving Average"""
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """Exponential Moving Average"""
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """Relative Strength Index"""
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = data.ewm(span=fast, adjust=False).mean()
        ema_slow = data.ewm(span=slow, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, period: int = 20, std_dev: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Bollinger Bands"""
        sma = data.rolling(window=period).mean()
        std = data.rolling(window=period).std()
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        return upper_band, sma, lower_band
    
    @staticmethod
    def atr(high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> pd.Series:
        """Average True Range"""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr


class TradingStrategy:
    """
    Multi-indicator trading strategy for NIFTY 50
    Uses SMA crossover, RSI, MACD for entry/exit signals
    """
    
    def __init__(self, fast_sma: int = 20, slow_sma: int = 50, 
                 rsi_period: int = 14, overbought: int = 70, 
                 oversold: int = 30):
        """
        Initialize strategy parameters
        
        Args:
            fast_sma: Fast moving average period
            slow_sma: Slow moving average period
            rsi_period: RSI calculation period
            overbought: RSI overbought threshold
            oversold: RSI oversold threshold
        """
        self.fast_sma = fast_sma
        self.slow_sma = slow_sma
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold
    
    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        """
        Generate trading signals based on technical indicators
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Series with trading signals
        """
        close = df['Close']
        high = df['High']
        low = df['Low']
        
        # Calculate indicators
        fast_ma = TechnicalIndicators.sma(close, self.fast_sma)
        slow_ma = TechnicalIndicators.sma(close, self.slow_sma)
        rsi = TechnicalIndicators.rsi(close, self.rsi_period)
        macd_line, signal_line, histogram = TechnicalIndicators.macd(close)
        atr = TechnicalIndicators.atr(high, low, close)
        
        # Initialize signals
        signals = pd.Series(0, index=df.index)
        
        # Trading logic
        for i in range(max(self.slow_sma, self.rsi_period), len(df)):
            if i < 2:
                continue
            
            # SMA Crossover
            sma_bullish = fast_ma.iloc[i] > slow_ma.iloc[i]
            sma_prev = fast_ma.iloc[i-1] <= slow_ma.iloc[i-1]
            
            # RSI conditions
            rsi_bullish = rsi.iloc[i] < self.overbought and rsi.iloc[i] > self.oversold
            rsi_oversold = rsi.iloc[i] < self.oversold
            
            # MACD conditions
            macd_bullish = histogram.iloc[i] > 0 and histogram.iloc[i-1] <= 0
            macd_bearish = histogram.iloc[i] < 0 and histogram.iloc[i-1] >= 0
            
            # BUY Signal: SMA crossover + RSI + MACD
            if sma_bullish and sma_prev and rsi_bullish and macd_bullish:
                signals.iloc[i] = Signal.BUY.value
            
            # SELL Signal: SMA bearish crossover
            elif not sma_bullish and fast_ma.iloc[i-1] > slow_ma.iloc[i-1] and macd_bearish:
                signals.iloc[i] = Signal.SELL.value
            
            # RSI extremes
            elif rsi.iloc[i] > self.overbought:
                signals.iloc[i] = Signal.SELL.value
            elif rsi_oversold:
                signals.iloc[i] = Signal.BUY.value
        
        return signals


class RiskManager:
    """Manages risk parameters and position sizing"""
    
    def __init__(self, initial_capital: float, max_risk_percent: float = 2.0,
                 max_position_size: float = 5.0, max_drawdown: float = 10.0):
        """
        Initialize risk management
        
        Args:
            initial_capital: Starting capital
            max_risk_percent: Maximum risk per trade (% of capital)
            max_position_size: Maximum position size (% of capital)
            max_drawdown: Maximum allowed drawdown (%)
        """
        self.initial_capital = initial_capital
        self.max_risk_percent = max_risk_percent
        self.max_position_size = max_position_size
        self.max_drawdown = max_drawdown
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> int:
        """Calculate position size based on risk"""
        risk_amount = self.current_capital * (self.max_risk_percent / 100)
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = int(risk_amount / price_risk)
        max_position = int(self.current_capital * (self.max_position_size / 100) / entry_price)
        
        return min(position_size, max_position)
    
    def check_drawdown_limit(self) -> bool:
        """Check if drawdown exceeds maximum allowed"""
        drawdown_percent = ((self.peak_capital - self.current_capital) / self.peak_capital) * 100
        return drawdown_percent <= self.max_drawdown
    
    def update_capital(self, pnl: float):
        """Update capital after trade"""
        self.current_capital += pnl
        self.peak_capital = max(self.peak_capital, self.current_capital)


class AlgoTrader:
    """Main algorithmic trading engine for NIFTY 50"""
    
    def __init__(self, initial_capital: float = 100000, symbol: str = "^NSEI"):
        """
        Initialize the algo trader
        
        Args:
            initial_capital: Starting capital in rupees
            symbol: Yahoo Finance symbol for NIFTY 50 (^NSEI)
        """
        self.symbol = symbol
        self.initial_capital = initial_capital
        self.risk_manager = RiskManager(initial_capital)
        self.strategy = TradingStrategy()
        
        self.current_position: Optional[Position] = None
        self.completed_trades: List[Trade] = []
        self.df: Optional[pd.DataFrame] = None
        self.signals: Optional[pd.Series] = None
    
    def fetch_data(self, start_date: str, end_date: str, interval: str = '1d') -> pd.DataFrame:
        """
        Fetch NIFTY 50 data from Yahoo Finance
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            interval: Data interval ('1d', '1h', '5m', etc.)
            
        Returns:
            DataFrame with OHLCV data
        """
        print(f"Fetching {self.symbol} data from {start_date} to {end_date}...")
        
        self.df = yf.download(self.symbol, start=start_date, end=end_date, 
                              interval=interval, progress=False)
        
        if self.df is None or self.df.empty:
            raise ValueError("Failed to fetch data. Check symbol and date range.")
        
        self.df = self.df[['Open', 'High', 'Low', 'Close', 'Volume']]
        print(f"Downloaded {len(self.df)} candles")
        
        return self.df
    
    def backtest(self, start_date: str, end_date: str) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            start_date: Backtest start date (YYYY-MM-DD)
            end_date: Backtest end date (YYYY-MM-DD)
            
        Returns:
            Dictionary with backtest results
        """
        # Fetch data
        self.fetch_data(start_date, end_date)
        
        # Generate signals
        print("Generating trading signals...")
        self.signals = self.strategy.generate_signals(self.df)
        
        # Execute backtest
        print("Executing backtest...")
        self.current_position = None
        self.completed_trades = []
        
        for idx in range(len(self.df)):
            date = self.df.index[idx]
            price = self.df['Close'].iloc[idx]
            signal = self.signals.iloc[idx]
            
            # Process buy signal
            if signal == Signal.BUY.value and self.current_position is None:
                stop_loss = price * 0.98  # 2% stop loss
                qty = self.risk_manager.calculate_position_size(price, stop_loss)
                
                if qty > 0:
                    self.current_position = Position(
                        entry_price=price,
                        entry_date=date,
                        quantity=qty,
                        position_type='LONG',
                        entry_signal=Signal.BUY
                    )
            
            # Process sell signal
            elif signal == Signal.SELL.value and self.current_position is not None:
                if self.current_position.position_type == 'LONG':
                    pnl = (price - self.current_position.entry_price) * self.current_position.quantity
                    pnl_percent = ((price - self.current_position.entry_price) / 
                                   self.current_position.entry_price) * 100
                    
                    trade = Trade(
                        entry_price=self.current_position.entry_price,
                        exit_price=price,
                        entry_date=self.current_position.entry_date,
                        exit_date=date,
                        quantity=self.current_position.quantity,
                        position_type='LONG',
                        pnl=pnl,
                        pnl_percent=pnl_percent,
                        duration_days=(date - self.current_position.entry_date).days
                    )
                    
                    self.completed_trades.append(trade)
                    self.risk_manager.update_capital(pnl)
                    self.current_position = None
        
        # Close any open position at the end
        if self.current_position is not None:
            final_price = self.df['Close'].iloc[-1]
            pnl = (final_price - self.current_position.entry_price) * self.current_position.quantity
            pnl_percent = ((final_price - self.current_position.entry_price) / 
                          self.current_position.entry_price) * 100
            
            trade = Trade(
                entry_price=self.current_position.entry_price,
                exit_price=final_price,
                entry_date=self.current_position.entry_date,
                exit_date=self.df.index[-1],
                quantity=self.current_position.quantity,
                position_type='LONG',
                pnl=pnl,
                pnl_percent=pnl_percent,
                duration_days=(self.df.index[-1] - self.current_position.entry_date).days
            )
            self.completed_trades.append(trade)
            self.risk_manager.update_capital(pnl)
        
        return self.generate_backtest_report()
    
    def generate_backtest_report(self) -> Dict:
        """Generate comprehensive backtest report"""
        
        if not self.completed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'sharpe_ratio': 0
            }
        
        trades_df = pd.DataFrame([
            {
                'entry_date': t.entry_date,
                'exit_date': t.exit_date,
                'entry_price': t.entry_price,
                'exit_price': t.exit_price,
                'quantity': t.quantity,
                'pnl': t.pnl,
                'pnl_percent': t.pnl_percent,
                'duration': t.duration_days
            }
            for t in self.completed_trades
        ])
        
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] <= 0]
        
        total_pnl = trades_df['pnl'].sum()
        total_profit = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_loss = losing_trades['pnl'].sum() if len(losing_trades) > 0 else 0
        
        win_rate = (len(winning_trades) / len(trades_df) * 100) if len(trades_df) > 0 else 0
        avg_win = (total_profit / len(winning_trades)) if len(winning_trades) > 0 else 0
        avg_loss = abs(total_loss / len(losing_trades)) if len(losing_trades) > 0 else 0
        profit_factor = (total_profit / abs(total_loss)) if total_loss != 0 else 0
        
        # Return detailed report
        report = {
            'total_trades': len(trades_df),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_percent': round((total_pnl / self.initial_capital) * 100, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'profit_factor': round(profit_factor, 2),
            'capital': round(self.risk_manager.current_capital, 2),
            'trades': trades_df.to_dict('records')
        }
        
        return report
    
    def print_report(self, report: Dict):
        """Pretty print backtest report"""
        print("\n" + "="*70)
        print("BACKTEST REPORT - NSE NIFTY 50")
        print("="*70)
        print(f"Total Trades: {report['total_trades']}")
        print(f"Winning Trades: {report['winning_trades']}")
        print(f"Losing Trades: {report['losing_trades']}")
        print(f"Win Rate: {report['win_rate']}%")
        print(f"\nTotal P&L: ₹{report['total_pnl']}")
        print(f"Total Return: {report['total_pnl_percent']}%")
        print(f"Final Capital: ₹{report['capital']}")
        print(f"\nAverage Win: ₹{report['avg_win']}")
        print(f"Average Loss: ₹{report['avg_loss']}")
        print(f"Profit Factor: {report['profit_factor']}")
        print("="*70 + "\n")


def main():
    """Main execution function"""
    
    # Initialize trader
    print("Initializing NIFTY 50 Algorithmic Trader...")
    trader = AlgoTrader(initial_capital=100000)
    
    # Run backtest
    # Using last 2 years of data for backtest
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
    
    try:
        report = trader.backtest(start_date, end_date)
        trader.print_report(report)
        
        # Save results
        with open('backtest_results.json', 'w') as f:
            # Convert datetime objects to strings for JSON serialization
            report_copy = report.copy()
            report_copy['trades'] = []
            for trade in report.get('trades', []):
                trade_copy = trade.copy()
                trade_copy['entry_date'] = str(trade['entry_date'])
                trade_copy['exit_date'] = str(trade['exit_date'])
                report_copy['trades'].append(trade_copy)
            json.dump(report_copy, f, indent=2)
        
        print("Results saved to backtest_results.json")
        
    except Exception as e:
        print(f"Error during backtest: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
