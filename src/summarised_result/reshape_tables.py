import pandas as pd

def reshape_group_additional(
        table: pd.DataFrame,
        split_string: str = " &&& "
        ) -> pd.DataFrame:

    group_add_columns = ["group_name", "group_level", "additional_name", "additional_level"]
    # The group_name, group_level, additional_name, and additional_level columns are actually lists
    for col_name in group_add_columns:
        table[col_name] = table[col_name].str.split(split_string)

    # exploding with the associated columns in a list means you explode them simultaneously, keeping things we want together
    exploded=table.explode(["group_name", "group_level"])
    exploded=exploded.explode(["additional_name", "additional_level"]).reset_index()

    # Then we have to do separate pivots on the group and additional levels
    group = exploded[["group_name", "group_level"]].pivot(columns="group_name", values="group_level")
    additional = exploded[["additional_name", "additional_level"]].pivot(columns="additional_name", values="additional_level")

    # Then we can get the columns and values we want by joining the pivots together and taking the first non-NaN value for each column
    group_and_additional = group.join(
            additional
            ).join(
                    exploded["index"]
                    ).set_index("index").groupby(level=0).first()

    return table.join(group_and_additional).drop(group_add_columns, axis=1)
