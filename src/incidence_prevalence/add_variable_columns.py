import pandas as pd


def add_var_columns(df: pd.DataFrame, prefix: str, suffixes: list[str] = ["_1", "_2"]):
    return sum([df[prefix + suffix] for suffix in suffixes])
