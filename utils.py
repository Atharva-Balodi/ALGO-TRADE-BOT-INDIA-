"""
Utility functions for the NIFTY 50 Algo Trader
"""

import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class TradeLogger:
    """Logs and manages trade history"""
    
    def __init__(self, filename: str = "trades.csv"):
        self.filename = filename
        self.trades: List[Dict] = []
    
    def add_trade(self, trade_dict: Dict):
        """Add a completed trade to log"""
        self.trades.append(trade_dict)
    
    def save_to_csv(self):
        """Save trades to CSV file"""
        if not self.trades:
            print("No trades to save.")
            return
        
        df = pd.DataFrame(self.trades)
        df.to_csv(self.filename, index=False)
        print(f"Trades saved to {self.filename}")
    
    def save_to_json(self):
        """Save trades to JSON file"""
        if not self.trades:
            print("No trades to save.")
            return
        
        json_file = self.filename.replace('.csv', '.json')
        with open(json_file, 'w') as f:
            json.dump(self.trades, f, indent=2, default=str)
        print(f"Trades saved to {json_file}")


class PerformanceAnalyzer:
    """Analyzes trading performance"""
    
    @staticmethod
    def calculate_metrics(trades_df: pd.DataFrame) -> Dict:
        """
        Calculate comprehensive performance metrics
        
        Args:
            trades_df: DataFrame with trade data
            
        Returns:
            Dictionary with performance metrics
        """
        if trades_df.empty:
            return {}
        
        winning = trades_df[trades_df['pnl'] > 0]
        losing = trades_df[trades_df['pnl'] <= 0]
        
        total_profit = winning['pnl'].sum() if len(winning) > 0 else 0
        total_loss = abs(losing['pnl'].sum()) if len(losing) > 0 else 0
        
        metrics = {
            'total_trades': len(trades_df),
            'winning_trades': len(winning),
            'losing_trades': len(losing),
            'win_rate': (len(winning) / len(trades_df) * 100) if len(trades_df) > 0 else 0,
            'avg_win': (total_profit / len(winning)) if len(winning) > 0 else 0,
            'avg_loss': (total_loss / len(losing)) if len(losing) > 0 else 0,
            'profit_factor': (total_profit / total_loss) if total_loss != 0 else 0,
            'total_pnl': trades_df['pnl'].sum(),
            'max_win': winning['pnl'].max() if len(winning) > 0 else 0,
            'max_loss': losing['pnl'].min() if len(losing) > 0 else 0,
        }
        
        return metrics
    
    @staticmethod
    def print_metrics(metrics: Dict):
        """Pretty print performance metrics"""
        print("\nPERFORMANCE METRICS")
        print("-" * 50)
        print(f"Total Trades: {metrics.get('total_trades', 0)}")
        print(f"Winning Trades: {metrics.get('winning_trades', 0)}")
        print(f"Losing Trades: {metrics.get('losing_trades', 0)}")
        print(f"Win Rate: {metrics.get('win_rate', 0):.2f}%")
        print(f"Average Win: ₹{metrics.get('avg_win', 0):.2f}")
        print(f"Average Loss: ₹{metrics.get('avg_loss', 0):.2f}")
        print(f"Profit Factor: {metrics.get('profit_factor', 0):.2f}")
        print(f"Total P&L: ₹{metrics.get('total_pnl', 0):.2f}")
        print("-" * 50)


class StrategyOptimizer:
    """Optimizes strategy parameters"""
    
    @staticmethod
    def parameter_sweep(
        trader: 'AlgoTrader',
        fast_sma_range: List[int],
        slow_sma_range: List[int],
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        Sweep through parameter combinations and find optimal settings
        
        Args:
            trader: AlgoTrader instance
            fast_sma_range: Range of fast SMA values
            slow_sma_range: Range of slow SMA values
            start_date: Backtest start date
            end_date: Backtest end date
            
        Returns:
            DataFrame with results for each parameter combination
        """
        results = []
        total_combos = len(fast_sma_range) * len(slow_sma_range)
        current = 0
        
        for fast in fast_sma_range:
            for slow in slow_sma_range:
                if fast >= slow:
                    continue
                
                current += 1
                print(f"Testing {current}/{total_combos}: Fast SMA={fast}, Slow SMA={slow}")
                
                try:
                    from algo_trader import TradingStrategy
                    trader.strategy = TradingStrategy(fast_sma=fast, slow_sma=slow)
                    report = trader.backtest(start_date, end_date)
                    
                    results.append({
                        'fast_sma': fast,
                        'slow_sma': slow,
                        'total_trades': report['total_trades'],
                        'win_rate': report['win_rate'],
                        'total_pnl': report['total_pnl'],
                        'profit_factor': report['profit_factor'],
                        'return_percent': report['total_pnl_percent']
                    })
                except Exception as e:
                    print(f"Error: {e}")
        
        return pd.DataFrame(results)


class DataValidator:
    """Validates trading data"""
    
    @staticmethod
    def check_data_quality(df: pd.DataFrame) -> Dict[str, bool]:
        """
        Check quality of OHLCV data
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Dictionary with validation results
        """
        checks = {
            'has_ohlcv': all(col in df.columns for col in ['Open', 'High', 'Low', 'Close', 'Volume']),
            'no_missing': not df.isnull().any().any(),
            'valid_ohlc': (df['High'] >= df['Low']).all() and (df['High'] >= df['Close']).all() and (df['High'] >= df['Open']).all(),
            'positive_volume': (df['Volume'] > 0).all(),
            'valid_index': not df.index.isnull().any()
        }
        
        return checks
    
    @staticmethod
    def print_validation_report(checks: Dict[str, bool]):
        """Print data validation report"""
        print("\nDATA QUALITY VALIDATION")
        print("-" * 50)
        for check, passed in checks.items():
            status = "✓ PASS" if passed else "✗ FAIL"
            print(f"{check:20} {status}")
        print("-" * 50)


class ReportGenerator:
    """Generates trading reports"""
    
    @staticmethod
    def generate_html_report(report: Dict, filename: str = "backtest_report.html"):
        """
        Generate HTML report of backtest results
        
        Args:
            report: Backtest report dictionary
            filename: Output HTML filename
        """
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NIFTY 50 Backtest Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .header {{ background-color: #1f77b4; color: white; padding: 20px; border-radius: 5px; }}
                .metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0; }}
                .metric-box {{ background-color: white; padding: 15px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric-label {{ font-size: 12px; color: #666; text-transform: uppercase; }}
                .metric-value {{ font-size: 24px; font-weight: bold; color: #1f77b4; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background-color: white; }}
                th {{ background-color: #f0f0f0; padding: 10px; text-align: left; }}
                td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
                tr:hover {{ background-color: #f9f9f9; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NIFTY 50 Algorithmic Trading - Backtest Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-label">Total Trades</div>
                    <div class="metric-value">{report.get('total_trades', 0)}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{report.get('win_rate', 0):.2f}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Total P&L</div>
                    <div class="metric-value">₹{report.get('total_pnl', 0):.0f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Return</div>
                    <div class="metric-value">{report.get('total_pnl_percent', 0):.2f}%</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Profit Factor</div>
                    <div class="metric-value">{report.get('profit_factor', 0):.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Final Capital</div>
                    <div class="metric-value">₹{report.get('capital', 0):.0f}</div>
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(filename, 'w') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {filename}")


# Export utilities
__all__ = [
    'TradeLogger',
    'PerformanceAnalyzer',
    'StrategyOptimizer',
    'DataValidator',
    'ReportGenerator'
]
