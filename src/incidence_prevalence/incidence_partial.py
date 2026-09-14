from typing import Self
from partialstats import Partial
import pandas as pd
from scipy import stats

from add_variable_columns import add_var_columns

def inc_rate_ci_exact(q, ev, pt) -> float:
    """
    Use the exact method to estimate 95% CI
    """
    return ((stats.chi2.ppf(
            q,
            df=2*ev
            ) / 2) / pt) * 100000

def add_inc_rate_ci_exact(df: pd.DataFrame) -> None:
    df["incidence_100000_pys_95CI_lower"] = df.apply(lambda x: inc_rate_ci_exact(0.025, x["outcome_count"], x["person_years"]), axis=1)
    df["incidence_100000_pys_95CI_upper"] = df.apply(lambda x: inc_rate_ci_exact(0.975, x["outcome_count"] + 1, x["person_years"]), axis=1)

class IncidencePartial(Partial):
    df: pd.DataFrame
    def __init__(self, df: pd.DataFrame) -> None:
        for colname in ["outcome_count", "person_years", "incidence_start_date", "incidence_end_date"]:
             if colname not in df.columns:
                 raise IndexError(f"Incidence partial results must have a {colname} column")
        self.df = df

    def dropped_derived_columns(self):
        return self.df.drop(
            ["incidence_100000_pys", "incidence_100000_pys_95CI_lower", "incidence_100000_pys_95CI_upper"], axis=1
        )

    def __add__(self, other: Self) -> Self:
        var_columns = ["outcome_count", "denominator_count", "person_days", "person_years"]
        df = self.dropped_derived_columns()
        columns = [x for x in df.columns if x not in var_columns]
        joined = (
            df
                .join(
                    other.dropped_derived_columns()
                        .set_index(columns), on = columns, lsuffix="_1", rsuffix="_2"
                )
        )
        for var in var_columns:
            joined[var] = add_var_columns(joined, var)
        joined.drop(
                [
                    *[var + "_1" for var in var_columns],
                    *[var + "_2" for var in var_columns]
                ], axis=1
            )
        return IncidencePartial(
            df=joined
        )

    def finalise(self):
        self.df["incidence_100000_pys_95CI_lower"] = self.df.apply(
            lambda x: inc_rate_ci_exact(
                0.025, x["outcome_count"], x["person_years"]), axis=1
        )
        self.df["incidence_100000_pys_95CI_upper"] = self.df.apply(
            lambda x: inc_rate_ci_exact(
                0.975, x["outcome_count"] + 1, x["person_years"]), axis=1
        )
        self.df["incidence_100000_pys"] = (self.df["outcome_count"]/self.df["person_years"]) * 100_000
        return self.df
    

