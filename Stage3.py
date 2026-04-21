from pathlib import Path
import pandas as pd


MASTER_PATH = Path("data/instrument_master_sample.csv")


def resolve_identifiers(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    if MASTER_PATH.exists():
        master = pd.read_csv(MASTER_PATH)
        master["identifier"] = master["identifier"].astype(str).str.strip()

        out = out.merge(
            master,
            on="identifier",
            how="left",
            suffixes=("", "_master")
        )
    else:
        out["matched_ticker"] = out.apply(
            lambda x: x["identifier"] if x["identifier_type"] == "Ticker" else None,
            axis=1
        )
        out["asset_class"] = None
        out["region"] = None

    out["match_status"] = out["matched_ticker"].apply(
        lambda x: "Matched" if pd.notna(x) and str(x).strip() != "" else "Unresolved"
    )

    out["asset_class"] = out["asset_class"].fillna("Unclassified")
    out["region"] = out["region"].fillna("Unclassified")

    return out
