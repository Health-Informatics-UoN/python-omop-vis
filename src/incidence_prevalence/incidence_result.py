from dataclasses import dataclass
from summarised_result import (
    SummarisedResult,
    SummarisedResultSettings,
    reshape_estimate_values,
    reshape_group_additional,
)

from pandas import DataFrame


@dataclass
class IncidenceResult:
    settings: list[SummarisedResultSettings]
    results: DataFrame

    @classmethod
    def from_summarised_result(cls, data: SummarisedResult):
        table = data.data
        return cls(
            settings=data.make_settings(),
            results=reshape_estimate_values(
                reshape_group_additional(
                    table.loc[
                        (table.result_id == 1) & ~(table.variable_name == "settings")
                    ]
                )
            ),
        )
