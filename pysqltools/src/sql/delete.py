from pysqltools.src.sql.query import Query
import pandas as pd
from pysqltools.src.log import PabLog
import typing as t

lg = PabLog(__name__)

def __get_data_points(df:pd.DataFrame) -> str:
    """
    Private function to get the dataframe fields as a SQL string
    """
    cols = df.columns
    data_points_str = ""
    for _, row in df.iterrows():
        conditions = [
            Query("{{ninja_column}} = {{ninja_value}}").format(
                ninja_column=col,
                ninja_value=row[col],
            ).sql
            for col in cols
        ]
        statement = "OR ( " + " AND ".join(conditions) + ") "
        data_points_str += statement
    data_points_str = data_points_str[2:]
    return data_points_str

def delete_from_dataframe(
    df: pd.DataFrame,
    table: str,
    batch_size: t.Optional[int] = None,
    subset: t.Optional[list[str]] = None

) -> t.Union[Query, t.Generator[Query, t.Any, t.Any]]:
    """
    ## delete_from_dataframe
    -------
    ### Parameters:
    -------

    - df (pd.DataFrame): The dataframe that will be used to set the condition of which table rows will be deleted
    - table (str): The target table (and schema if needed) to delete rows from
    - batch_size [Optional] (int): If a batch size is added, the function will return a generator iterating batch of
    the specified size with delete queries
    - subset [Optional] (list[str]): Subset of columns of the dataframe to use on the delete conditions

    -------
    ### Output:
    -------
    If the batch_size is not specified, the function will return a Query object with an SQL Ready to delete all the rows
    on the table that currently are on the dataframe

    If the batch_size is specified, the function will return a Generator that will yield Query objects containing the deletion of 
    {batch_size} rows

    """
    if not df.empty:
        if batch_size is None:
            return Query(f"""DELETE FROM {table} WHERE {data_points_str}""")
        previous_iteration = 0
        while previous_iteration < len(df):
            df_batch = df.iloc[previous_iteration : previous_iteration + batch_size]
            data_points_str = __get_data_points(df_batch)
            yield Query(f"""DELETE FROM {table} WHERE {data_points_str}""")
