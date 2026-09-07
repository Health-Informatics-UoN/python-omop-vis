import pandas as pd


def analysis_interval_column(
    date_column: pd.Series, analysis_interval: str
) -> pd.Series:
    match analysis_interval:
        case "years":
            return pd.Series(date_column.apply(lambda x: x.year))
        case "month":
            return pd.Series(date_column.apply(lambda x: f"{x.year}-{x.month}"))
        case _:
            return date_column.copy()


def take_date_range(
    df: pd.DataFrame,
    date_column_name: str,
    date_range: tuple[pd.Timestamp, pd.Timestamp],
):
    return df.loc[
        (df[date_column_name] >= min(date_range))
        & (df[date_column_name] <= max(date_range))
    ]
