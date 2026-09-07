from dataclasses import dataclass

import pandas as pd
from matplotlib.axes import Axes

from .analysis_interval import (
    analysis_interval_column,
    take_date_range,
)

from summarised_result import (
    SummarisedResult,
    SummarisedResultSettings,
    reshape_estimate_values,
    reshape_group_additional,
)
from .plots import bar_i_p, scatter_i_p


@dataclass
class IncidenceResult:
    settings: list[SummarisedResultSettings]
    incidence_result_id: int
    results: pd.DataFrame

    @classmethod
    def from_summarised_result(cls, data: SummarisedResult):
        settings = data.make_settings()
        incidence_result_id = next(
            (x.result_id for x in settings if x.result_type == "incidence"), None
        )
        if incidence_result_id is None:
            raise ValueError("There is no incidence result in this data")
        res = reshape_estimate_values(
            reshape_group_additional(
                data.data.loc[
                    (data.data.result_id == incidence_result_id)
                    & ~(data.data.variable_name == "settings")
                ]
            )
        )

        cls.reconcile_types(res)

        return cls(
            settings=data.make_settings(),
            incidence_result_id=incidence_result_id,
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

        df["incidence_100000_pys"] = pd.to_numeric(
            df["incidence_100000_pys"], errors="coerce"
        )
        df["incidence_100000_pys_95CI_lower"] = pd.to_numeric(
            df["incidence_100000_pys_95CI_lower"], errors="coerce"
        )
        df["incidence_100000_pys_95CI_upper"] = pd.to_numeric(
            df["incidence_100000_pys_95CI_upper"], errors="coerce"
        )

        df["person_days"] = pd.to_numeric(
            df["person_days"], errors="coerce", downcast="unsigned"
        )
        df["person_years"] = pd.to_numeric(df["person_years"])

        df["incidence_start_date"] = pd.to_datetime(df["incidence_start_date"])
        df["incidence_end_date"] = pd.to_datetime(df["incidence_end_date"])

    def plot_incidence(
        self,
        x: str = "incidence_start_date",
        y: str = "incidence_100000_pys",
        line: bool = False,
        # point: bool = True,
        # ribbon: bool = False,
        ymin: str = "incidence_100000_pys_95CI_lower",
        ymax: str = "incidence_100000_pys_95CI_upper",
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

    def plot_incidence_population(
        self,
        x: str = "incidence_start_date",
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
