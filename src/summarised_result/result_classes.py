from dataclasses import dataclass

from pandas import DataFrame

from src.summarised_result.parse_settings import SummarisedResultSettings
from src.summarised_result.reshape_tables import (
    reshape_estimate_values,
    reshape_group_additional,
)


class SummarisedResult:
    def __init__(self, data: DataFrame) -> None:
        self.data = data

    def make_settings(self) -> list[SummarisedResultSettings]:
        return [
            SummarisedResultSettings.from_table(
                self.data.loc[self.data["result_id"] == x]
            )
            for x in self.data.result_id.unique()
        ]
