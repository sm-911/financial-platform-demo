import pandas as pd
import numpy as np
from pathlib import Path
import datetime

# Generate synthetic OHLCV data for demonstration
rows = 200
end_date = datetime.date.today()
dates = pd.date_range(end=end_date, periods=rows, freq='B')  # business days
np.random.seed(0)
prices = np.cumsum(np.random.randn(rows)) + 150  # start around 150
opens = prices + np.random.randn(rows) * 0.5
highs = opens + np.abs(np.random.randn(rows)) * 0.5
lows = opens - np.abs(np.random.randn(rows)) * 0.5
closes = opens + np.random.randn(rows) * 0.2
adj_closes = closes  # simple case
volumes = np.random.randint(1_000_000, 5_000_000, size=rows)

df = pd.DataFrame({
    'Date': dates,
    'Open': opens,
    'High': highs,
    'Low': lows,
    'Close': closes,
    'Adj Close': adj_closes,
    'Volume': volumes
})
# Ensure columns order
cols = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
output_path = Path(__file__).resolve().parent / 'data' / 'sample' / 'AAPL.csv'
output_path.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(output_path, index=False, columns=cols)
print(f"Sample CSV written to {output_path}")
