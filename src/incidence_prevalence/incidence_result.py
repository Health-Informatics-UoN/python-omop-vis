from dataclasses import dataclass
from ..summarised_result import (
    SummarisedResult,
    SummarisedResultSettings,
    reshape_estimate_values,
    reshape_group_additional,
)

import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

DISPLAY_NAMES = {
    "outcome_count": "Outcome count",
    "denominator_count": "Denominator count",
    "person_years": "Person years",
    "incidence_100000_pys": "Incidence (100,00 person-years)",
}


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

    def analysis_interval_column(self, date_column_name: str) -> pd.Series:
        analysis_interval = self.results["analysis_interval"].iloc[0]
        match analysis_interval:
            case "years":
                return pd.Series(self.results[date_column_name].apply(lambda x: x.year))
            case "month":
                return pd.Series(self.results[date_column_name].apply(lambda x: f"{x.year}-{x.month}"))
            case _:
                return pd.Series(self.results[date_column_name])

    def plot_incidence(
        self,
        x: str = "incidence_start_date",
        y: str = "incidence_100000_pys",
        line: bool = False,
        # point: bool = True,
        # ribbon: bool = False,
        ymin: str = "incidence_100000_pys_95CI_lower",
        ymax: str = "incidence_100000_pys_95CI_upper",
        date_range: tuple[pd.Timestamp, pd.Timestamp] | None=None,
        axes: Axes | None = None
    ) -> Axes:
        if date_range is not None:
            plot_results = self.results.loc[(self.results[x] >= min(date_range)) & (self.results[x] <= max(date_range))]
        else:
            plot_results=self.results
        plot_results[x] = self.analysis_interval_column(x)
        # If you leave in NaN values for the y axis, seaborn plots the bars very thin for some reason
        plot_results = plot_results.loc[~plot_results[y].isna()]
        plot = sns.scatterplot(data=plot_results, x=x, y=y, legend=False, ax=axes)
        plt.errorbar(
                x=plot_results[x],
                y=plot_results[y],
                yerr=(plot_results[ymin], plot_results[ymax]),
                fmt="o-" if line else "o"
                )
        plot.set(xlabel=f"Date ({self.results["analysis_interval"].iloc[0]})")
        if y in DISPLAY_NAMES:
            plot.set(ylabel=DISPLAY_NAMES[y])
        plot.grid(True, axis="both")
        plot.set_axisbelow(True)
        plot.set_xticklabels(plot.get_xticklabels(), rotation=30, ha="right")
        return plot

        

    def plot_incidence_population(
        self,
        x: str="incidence_start_date",
        y: str="denominator_count",
        date_range: tuple[pd.Timestamp, pd.Timestamp] | None=None,
        axes: Axes | None = None
    ) -> Axes:
        if date_range is not None:
            plot_results = self.results.loc[(self.results[x] >= min(date_range)) & (self.results[x] <= max(date_range))]
        else:
            plot_results=self.results
        plot_results[x] = self.analysis_interval_column(x)
        # If you leave in NaN values for the y axis, seaborn plots the bars very thin for some reason
        plot_results = plot_results.loc[~plot_results[y].isna()]
        plot = sns.barplot(data=plot_results, x=x, y=y, legend=False, ax=axes)
        plot.set(xlabel=f"Date ({self.results["analysis_interval"].iloc[0]})")
        if y in DISPLAY_NAMES:
            plot.set(ylabel=DISPLAY_NAMES[y])
        plot.grid(True, axis="both")
        plot.set_axisbelow(True)
        plot.set_xticklabels(plot.get_xticklabels(), rotation=30, ha="right")
        return plot
