"""A high-level API for generating Kusto queries."""
__version__ = "0.4.2"

from . import database as _database_module
from .expression import TableExpr

KustoDatabase = _database_module.KustoDatabase
DatabaseRef = _database_module.DatabaseRef
Cluster = _database_module.Cluster
cluster = _database_module.cluster
table = _database_module.table

# Convenience alias; avoids shadowing the database module name.
db = _database_module.database

__all__ = [
    "KustoDatabase",
    "DatabaseRef",
    "Cluster",
    "cluster",
    "db",
    "table",
    "TableExpr",
]
