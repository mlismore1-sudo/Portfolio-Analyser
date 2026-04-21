from datetime import date, timedelta

import pandas as pd
import yfinance as yf


def get_price_history(ticker: str, years: int = 5) -> pd.Series:
    end_date = date.today()
    start_date = end_date - timedelta(days=365 * years + 10)

    data = yf.download(
        ticker,
        start=start_date,
        end=end_date,
        auto_adjust=True,
        progress=False
    )

    if data.empty:
        return pd.Series(dtype=float)

    series = data["Close"].copy()
    series.name = ticker
    return series
