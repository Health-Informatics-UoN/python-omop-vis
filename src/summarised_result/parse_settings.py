from dataclasses import dataclass
from typing import Any

import pandas as pd

NON_VARIABLE_NAMES = [
    "result_type",
    "package_name",
    "package_version",
    "group",
    "additional",
    "min_cell_count",
]


@dataclass
class SemanticVersion:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, semver_string: str):
        try:
            major, minor, patch = [int(x) for x in semver_string.split(".")]
            return cls(major, minor, patch)
        except TypeError:
            raise TypeError(
                "One of the values in the semantic version string could not be parsed as an integer"
            )


@dataclass
class EstimateDescription:
    name: str
    r_type: str
    value: Any


def first_matching_row_val(df: pd.DataFrame, query: str, val_col: str):
    return df.query(query)[val_col].iloc[0]


def first_matching_estimate_val(
    df: pd.DataFrame,
    field: str,
):
    return first_matching_row_val(df, f"estimate_name == '{field}'", "estimate_value")


@dataclass
class SummarisedResultSettings:
    result_id: int
    result_type: str
    package_name: str
    package_version: SemanticVersion
    groups: list[str]
    strata: list[str] | None
    additional: list[str] | None
    min_cell_count: int
    variables: list[EstimateDescription]

    @classmethod
    def from_table(cls, result_table: pd.DataFrame):
        return cls(
            result_id=result_table.result_id.iloc[0],
            result_type=first_matching_estimate_val(result_table, "result_type"),
            package_name=first_matching_estimate_val(result_table, "package_name"),
            package_version=SemanticVersion.from_string(
                first_matching_estimate_val(result_table, "package_version")
            ),
            groups=[
                x.strip()
                for x in first_matching_estimate_val(result_table, "group").split("&&&")
            ],
            strata=None,
            additional=[
                x.strip()
                for x in first_matching_estimate_val(result_table, "additional").split(
                    "&&&"
                )
            ],
            min_cell_count=int(
                first_matching_estimate_val(result_table, "min_cell_count")
            ),
            variables=list(
                result_table.loc[
                    (~result_table["estimate_name"].isin(NON_VARIABLE_NAMES))
                    & (result_table["variable_name"] == "settings")
                ].apply(
                    lambda x: EstimateDescription(
                        name=x["estimate_name"],
                        r_type=x["estimate_type"],
                        value=x["estimate_value"],
                    ),
                    axis=1,
                )
            ),
        )
