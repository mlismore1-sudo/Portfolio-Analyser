import pandas as pd

from utils.market_data import get_price_history


def calculate_asset_allocation(df: pd.DataFrame) -> pd.DataFrame:
    total = df["gbp_value"].sum()
    out = (
        df.groupby("asset_class", dropna=False)["gbp_value"]
        .sum()
        .reset_index()
        .sort_values("gbp_value", ascending=False)
    )
    out["weight_pct"] = (out["gbp_value"] / total) * 100
    return out


def calculate_region_allocation(df: pd.DataFrame) -> pd.DataFrame:
    total = df["gbp_value"].sum()
    out = (
        df.groupby("region", dropna=False)["gbp_value"]
        .sum()
        .reset_index()
        .sort_values("gbp_value", ascending=False)
    )
    out["weight_pct"] = (out["gbp_value"] / total) * 100
    return out


def calculate_portfolio_trailing_returns(df: pd.DataFrame) -> pd.DataFrame:
    matched = df[df["match_status"] == "Matched"].copy()
    if matched.empty:
        return pd.DataFrame({
            "period": ["1Y", "3Y", "5Y"],
            "portfolio_return_pct": [None, None, None]
        })

    total_value = matched["gbp_value"].sum()
    matched["weight"] = matched["gbp_value"] / total_value

    results = []
    for years, label in [(1, "1Y"), (3, "3Y"), (5, "5Y")]:
        weighted_return = 0.0
        valid_weight = 0.0

        for _, row in matched.iterrows():
            ticker = row["matched_ticker"]
            weight = row["weight"]

            series = get_price_history(ticker, years=years)
            if series.empty or len(series) < 2:
                continue

            ret = (series.iloc[-1] / series.iloc[0]) - 1
            weighted_return += ret * weight
            valid_weight += weight

        portfolio_return = (weighted_return / valid_weight) if valid_weight > 0 else None
        results.append(
            {"period": label, "portfolio_return_pct": portfolio_return * 100 if portfolio_return is not None else None}
        )

    return pd.DataFrame(results)
