import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from matplotlib.axes import Axes

DISPLAY_NAMES = {
    "outcome_count": "Outcome count",
    "denominator_count": "Denominator count",
    "person_years": "Person years",
    "incidence_100000_pys": "Incidence (100,000 person-years)",
    "prevalence": "Prevalence",
}


def scatter_i_p(
    plot_results: pd.DataFrame,
    x: str,
    y: str,
    line: bool,
    # point: bool = True,
    # ribbon: bool = False,
    ymin: str,
    ymax: str,
    analysis_interval: str | None,
    axes: Axes | None,
) -> Axes:
    plot = sns.scatterplot(data=plot_results, x=x, y=y, legend=False, ax=axes)
    plt.errorbar(
        x=plot_results[x],
        y=plot_results[y],
        yerr=(plot_results[ymin], plot_results[ymax]),
        fmt="o-" if line else "o",
    )
    if analysis_interval is not None:
        plot.set(xlabel=f"Date ({analysis_interval})")
    if y in DISPLAY_NAMES:
        plot.set(ylabel=DISPLAY_NAMES[y])
    plot.grid(True, axis="both")
    plot.set_axisbelow(True)
    plot.set_xticklabels(plot.get_xticklabels(), rotation=30, ha="right")
    return plot


def bar_i_p(
    plot_results: pd.DataFrame,
    x: str,
    y: str,
    analysis_interval: str | None,
    axes: Axes | None = None,
) -> Axes:
    # If you leave in NaN values for the y axis, seaborn plots the bars very thin for some reason
    plot_results = plot_results.loc[~plot_results[y].isna()]
    plot = sns.barplot(data=plot_results, x=x, y=y, legend=False, ax=axes)
    if analysis_interval is not None:
        plot.set(xlabel=f"Date ({analysis_interval})")
    if y in DISPLAY_NAMES:
        plot.set(ylabel=DISPLAY_NAMES[y])
    plot.grid(True, axis="both")
    plot.set_axisbelow(True)
    plot.set_xticklabels(plot.get_xticklabels(), rotation=30, ha="right")
    return plot
