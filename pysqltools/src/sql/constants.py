"""
Constant values for the queries package
"""

KEYWORDS = ["select", "from", "where", "group", "having", "order", "limit"]

TYPE_MAPPING = {
    "object": "varchar",
    "int64": "int",
    "float64": "double",
    "bool": "bool",
    "datetime64": "timestamp",
    "datetime64[ns]": "timestamp",
}
