import hfile

# Definir la estructura de columnas y filas
columns = [
    {"family": "cf1", "qualifier": "col1", "timestamp": 123456, "value": b"val1"},
    {"family": "cf1", "qualifier": "col2", "timestamp": 234567, "value": b"val2"},
    {"family": "cf2", "qualifier": "col1", "timestamp": 345678, "value": b"val3"},
    {"family": "cf2", "qualifier": "col2", "timestamp": 456789, "value": b"val4"},
]

rows = [
    {"key": b"row1", "columns": columns[0:2]},
    {"key": b"row1", "columns": columns[2:]},
    {"key": b"row2", "columns": columns},
]

# Crear el HFile y escribir en él
with hfile.create("test.hfile") as writer:
    for row in sorted(rows, key=lambda x: x["key"]):
        key = row["key"]
        for col in sorted(row["columns"], key=lambda x: (x["family"], x["qualifier"], x["timestamp"])):
            family = col["family"].encode()
            qualifier = col["qualifier"].encode()
            timestamp = col["timestamp"]
            value = col["value"]
            writer.append(key, family, qualifier, timestamp, value)
