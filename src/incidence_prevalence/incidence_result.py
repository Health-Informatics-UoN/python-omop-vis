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

    def plot_incidence_population(
        self,
        x="incidence_start_date",
        y="denominator_count",
    ) -> Axes:
        plot = sns.barplot(data=self.results, x=x, y=y, hue=y, legend=False, palette=["dimgray"])
        plot.set(xlabel=f"Date ({self.results["analysis_interval"].iloc[0]})")
        if y in DISPLAY_NAMES:
            plot.set(ylabel=DISPLAY_NAMES[y])
        plot.grid(True, axis="both")
        return plot
