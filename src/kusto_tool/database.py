"""Classes for building Kusto query text."""
import os
from collections.abc import KeysView

import jinja2 as jj

from kusto_tool.expression import TableExpr, quote


def list_to_kusto(lst):
    """Convert a Python iterable to a Kusto ``dynamic([ ... ])`` literal.

    Parameters
    ----------
    lst : Iterable[Any]
        Any iterable of values to be rendered as a Kusto list literal.

    Returns
    -------
    str
        A ``dynamic([ ... ])`` KQL literal with one item per line.
    """
    list_str = [quote(i) for i in list(lst)]
    return "dynamic([\n\t" + ",\n\t".join(list_str) + "\n])"


def dict_to_datatable(dictionary: dict) -> str:
    """Render a ``datatable`` statement from a simple dictionary.

    Parameters
    ----------
    dictionary : dict
        Mapping of key -> value to embed into a two-column datatable.

    Returns
    -------
    str
        A ``datatable(key: string, value: string)`` KQL statement.
    """
    dict_str = "\n\t".join([f"'{k}', '{v}'," for k, v in dictionary.items()])
    template = """datatable(key: string, value: string)[
    {{ dict_str }}
]"""
    stmt = jj.Template(template).render(dict_str=dict_str)
    return stmt


def maybe_read_file(query):
    """Return file contents if ``query`` is a file path, otherwise return input.

    Parameters
    ----------
    query : str
        Either a path to a file or a query string.

    Returns
    -------
    str
        The file contents if ``query`` is a file path, otherwise ``query``.
    """
    if os.path.isfile(query):
        logger.info("Reading file {}.", query)
        with open(query, "r", encoding="utf-8") as query_file:
            return query_file.read()
    return query


def render_template_query(query, *args, **kwargs) -> str:
    """Render a Jinja2 template with optional parameters.

    Parameters
    ----------
    query : str
        A query string or file path. If a file path, its contents are read.
    *args, **kwargs
        Jinja2 template parameters. Iterable values in kwargs are converted
        to Kusto ``dynamic([ ... ])`` list literals.

    Returns
    -------
    str
        Rendered query text.
    """
    # Any list arguments need to be converted to Kusto list strings
    query = maybe_read_file(query)
    converted_kwargs = {
        k: list_to_kusto(v) if isinstance(v, (list, tuple, set, KeysView)) else v
        for k, v in kwargs.items()
    }
    return jj.Template(query).render(*args, **converted_kwargs)


def render_set(query, table, folder, docstring, *args, replace=False, **kwargs) -> str:
    """Render a ``.set-or-[append|replace]`` control command.

    Parameters
    ----------
    query : str
        Source query or file path.
    table : str
        Target table name.
    folder : str
        Target folder name.
    docstring : str
        Docstring metadata for the table.
    replace : bool, default False
        If True, render ``.set-or-replace``; otherwise ``.set-or-append``.
    *args, **kwargs
        Template parameters passed to the query renderer.

    Returns
    -------
    str
        Rendered control command text.
    """
    query = maybe_read_file(query)
    query_rendered = render_template_query(query, *args, **kwargs)
    command = "replace" if replace else "append"
    set_append_template = """.set-or-{{ command }} {{ table }}
with (
folder = "{{ folder }}",
docstring = "{{ docstring }}",
)
<|
{{ query_string }}
"""
    command_rendered = render_template_query(
        set_append_template,
        command=command,
        table=table,
        folder=folder,
        docstring=docstring,
        query_string=query_rendered,
    )
    return command_rendered


class KustoDatabase:
    """A lightweight database context for query rendering.

    This class does not connect to Azure Data Explorer. It only provides
    a namespace for rendering table references with ``cluster`` and
    ``database`` prefixes.
    """

    def __init__(self, cluster, database):
        """A class representing a Kusto database.

        Parameters
        ----------
        cluster: str
            The cluster name.
        database: str
            The database name.
        """
        self.cluster = cluster
        self.database = database

    def table(self, name, columns=None, inspect=False):
        """A tabular expression.

        Parameters
        ----------
        name: str
            The name of the table in the database.
        columns: dict or list
            Either:
            1. A dictionary where keys are column names and values are
            data type names, or
            2. A list of Column instances.
        inspect: bool, default False
            Not supported in query-only mode. Always raises if True.

        Returns
        -------
        TableExpr
            A table expression instance.
        """
        if inspect:
            raise RuntimeError("inspect=True is not supported in query-only mode.")
        return TableExpr(name, database=self, columns=columns)

    def table_ref(self, name: str) -> str:
        """Render a fully-qualified table reference string.

        Parameters
        ----------
        name : str
            Table name.

        Returns
        -------
        str
            ``cluster('...').database('...').['Table']`` reference.
        """
        return f"cluster('{self.cluster}').database('{self.database}').['{name}']"

    def __str__(self):
        return f"{str(self.cluster)}.database('{self.database}')"


class Cluster:
    """Cluster context used for rendering table references.

    This is a lightweight object that only stores the cluster name and
    provides a ``database()`` factory for building table references.
    """

    def __init__(self, name):
        self.name = name

    def database(self, name):
        """Create an instance representing a database in the cluster.

        Parameters
        ----------
        name: str
            The name of the Kusto database in the cluster.

        Returns
        -------
        KustoDatabase
            an instance representing the Kusto database.
        """
        return KustoDatabase(self.name, name)

    def __str__(self):
        return f"cluster('{self.name}')"


def cluster(name):
    """Convenience function to construct a Cluster instance.
    Makes the query look more like KQL.
    """
    return Cluster(name)


def table(name, columns=None):
    """Construct a table expression without a cluster/database context.

    Parameters
    ----------
    name : str
        Table name.
    columns : dict or list, optional
        Optional column schema. When omitted, columns are treated as unknown
        and should be referenced by string or via ``col("Name")``.
    """
    return TableExpr(name, database=None, columns=columns)


def q(name):
    """Construct a table expression from a raw table name.

    This is the preferred constructor for schema-free, text-only usage.
    """
    return TableExpr(name, database=None, columns=None)


def query(name):
    """Construct a table expression from a raw table name.

    Alias for :func:`q` for readability.
    """
    return q(name)


def database(name, cluster_name=None):
    """Convenience function to construct a KustoDatabase instance.

    Parameters
    ----------
    name: str
        Database name.
    cluster_name: str, default None
        Optional cluster name to include in the rendered table ref.
    """
    if cluster_name is None:
        return DatabaseRef(name)
    return KustoDatabase(cluster_name, name)


class DatabaseRef:
    """A database-only context for query rendering.

    This renders ``database('Name').['Table']`` without a cluster prefix.
    """

    def __init__(self, name: str):
        self.database = name

    def table(self, name, columns=None, inspect=False):
        """Create a table expression in this database context.

        Parameters
        ----------
        name : str
            Table name.
        columns : dict or list, optional
            Optional column schema.
        inspect : bool, default False
            Not supported in query-only mode.
        """
        if inspect:
            raise RuntimeError("inspect=True is not supported in query-only mode.")
        return TableExpr(name, database=self, columns=columns)

    def table_ref(self, name: str) -> str:
        return f"database('{self.database}').['{name}']"

    def __str__(self):
        return f"database('{self.database}')"
