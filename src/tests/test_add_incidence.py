import pytest
import pandas as pd

from incidence_prevalence.incidence_partial import IncidencePartial

@pytest.fixture
def first_df():
    return pd.DataFrame(
            {
                "outcome_count": [1],
                "denominator_count": [1],
                "person_days": [365],
                "person_years": [1],
                "incidence_start_date": [""],
                "incidence_end_date": [""]
                }
            )

@pytest.fixture
def second_df():
    return pd.DataFrame(
            {
                "outcome_count": [2],
                "denominator_count": [2],
                "person_days": [365*2],
                "person_years": [2],
                "incidence_start_date": [""],
                "incidence_end_date": [""]
                }
            )

def test_add_works(first_df, second_df):
    partial_1 = IncidencePartial(first_df)
    partial_2 = IncidencePartial(second_df)

    overall_partial = partial_1 + partial_2

    assert overall_partial.df["outcome_count"].iloc[0] == 3
    assert overall_partial.df["denominator_count"].iloc[0] == 3
    assert overall_partial.df["person_days"].iloc[0] == 365*3
    assert overall_partial.df["person_years"].iloc[0] == 3

def test_finalise_works(first_df, second_df):
    partial_1 = IncidencePartial(first_df)
    partial_2 = IncidencePartial(second_df)

    overall_partial = partial_1 + partial_2

    df = overall_partial.finalise()

    assert "incidence_100000_pys" in df.columns
    assert "incidence_100000_pys_95CI_upper" in df.columns
    assert "incidence_100000_pys_95CI_lower" in df.columns

