from dataclasses import dataclass

import pandas as pd
from matplotlib.axes import Axes

from src.incidence_prevalence.analysis_interval import (
    analysis_interval_column,
    take_date_range,
)

from ..summarised_result import (
    SummarisedResult,
    SummarisedResultSettings,
    reshape_estimate_values,
    reshape_group_additional,
)
from .plots import bar_i_p, scatter_i_p


@dataclass
class PrevalenceResult:
    settings: list[SummarisedResultSettings]
    prevalence_result_id: int
    results: pd.DataFrame

    @classmethod
    def from_summarised_result(cls, data: SummarisedResult):
        settings = data.make_settings()
        prevalence_result_id = next(
            (x.result_id for x in settings if x.result_type == "prevalence"), None
        )
        if prevalence_result_id is None:
            raise ValueError("There is no prevalence result in this data")
        res = reshape_estimate_values(
            reshape_group_additional(
                data.data.loc[
                    (data.data.result_id == prevalence_result_id)
                    & ~(data.data.variable_name == "settings")
                ]
            )
        )

        cls.reconcile_types(res)

        return cls(
            settings=data.make_settings(),
            prevalence_result_id=prevalence_result_id,
            results=res,
        )

    @staticmethod
    def reconcile_types(df: pd.DataFrame) -> None:
        df["denominator_count"] = pd.to_numeric(
            df["denominator_count"], errors="coerce", downcast="unsigned"
        )
        df["outcome_count"] = pd.to_numeric(
            df["outcome_count"], errors="coerce", downcast="unsigned"
        )

        df["prevalence"] = pd.to_numeric(df["prevalence"], errors="coerce")
        df["prevalence_95CI_lower"] = pd.to_numeric(
            df["prevalence_95CI_lower"], errors="coerce"
        )
        df["prevalence_95CI_upper"] = pd.to_numeric(
            df["prevalence_95CI_upper"], errors="coerce"
        )

        df["prevalence_start_date"] = pd.to_datetime(df["prevalence_start_date"])
        df["prevalence_end_date"] = pd.to_datetime(df["prevalence_end_date"])

    def plot_prevalence(
        self,
        x: str = "prevalence_start_date",
        y: str = "prevalence",
        line: bool = False,
        # point: bool = True,
        # ribbon: bool = False,
        ymin: str = "prevalence_95CI_lower",
        ymax: str = "prevalence_95CI_upper",
        date_range: tuple[pd.Timestamp, pd.Timestamp] | None = None,
        axes: Axes | None = None,
    ) -> Axes:
        if date_range is not None:
            plot_results = take_date_range(self.results, x, date_range)
        else:
            plot_results = self.results.copy()
        plot_results["x"] = analysis_interval_column(
            plot_results[x], plot_results["analysis_interval"].iloc[0]
        )
        return scatter_i_p(
            plot_results,
            "x",
            y,
            line,
            ymin,
            ymax,
            plot_results["analysis_interval"].iloc[0],
            axes,
        )

    def plot_prevalence_population(
        self,
        x: str = "prevalence_start_date",
        y: str = "denominator_count",
        date_range: tuple[pd.Timestamp, pd.Timestamp] | None = None,
        axes: Axes | None = None,
    ) -> Axes:
        if date_range is not None:
            plot_results = take_date_range(self.results, x, date_range)
        else:
            plot_results = self.results.copy()
        plot_results["x"] = analysis_interval_column(
            plot_results[x], plot_results["analysis_interval"].iloc[0]
        )
        return bar_i_p(
            plot_results, "x", y, plot_results["analysis_interval"].iloc[0], axes
        )
