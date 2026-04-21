import pandas as pd


COLUMN_ALIASES = {
    "identifier": ["ticker", "isin", "sedol", "security code", "instrument"],
    "description": ["description", "holding", "security name", "name"],
    "gbp_value": ["gbp value", "market value", "value", "market value gbp", "gbp_market_value"],
}


def find_matching_column(columns, aliases):
    lower_map = {c.lower().strip(): c for c in columns}
    for alias in aliases:
        if alias in lower_map:
            return lower_map[alias]
    return None


def detect_identifier_type(row):
    raw = str(row["identifier"]).strip()
    if len(raw) == 12 and raw[:2].isalpha():
        return "ISIN"
    if len(raw) == 7 and raw.isalnum():
        return "SEDOL"
    return "Ticker"


def parse_uploaded_holdings(uploaded_file):
    df = pd.read_csv(uploaded_file)

    identifier_col = find_matching_column(df.columns, COLUMN_ALIASES["identifier"])
    description_col = find_matching_column(df.columns, COLUMN_ALIASES["description"])
    value_col = find_matching_column(df.columns, COLUMN_ALIASES["gbp_value"])

    missing = []
    if not identifier_col:
        missing.append("identifier")
    if not description_col:
        missing.append("description")
    if not value_col:
        missing.append("gbp_value")

    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    parsed = df[[identifier_col, description_col, value_col]].copy()
    parsed.columns = ["identifier", "description", "gbp_value"]

    parsed["identifier"] = parsed["identifier"].astype(str).str.strip()
    parsed["description"] = parsed["description"].astype(str).str.strip()
    parsed["gbp_value"] = (
        parsed["gbp_value"]
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("£", "", regex=False)
        .astype(float)
    )

    parsed["identifier_type"] = parsed.apply(detect_identifier_type, axis=1)
    return parsed
