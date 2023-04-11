import time
from collections import defaultdict
import tkinter as tk
from tkinter import messagebox


class HBase:
    def __init__(self):
        self.tables = {}

    def create(self, table_name, column_families):
        if table_name not in self.tables:
            self.tables[table_name] = {
                "column_families": column_families,
                "rows": defaultdict(dict),
                "enabled": True,
            }
            return f"Tabla '{table_name}' creada."
        else:
            return f"La tabla '{table_name}' ya existe."

    def list_tables(self):
        return list(self.tables.keys())

    def disable(self, table_name):
        if table_name in self.tables:
            self.tables[table_name]["enabled"] = False
            return f"Tabla '{table_name}' deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def is_enabled(self, table_name):
        return self.tables.get(table_name, {}).get("enabled", False)

    def alter(self, table_name, new_column_families):
        if table_name in self.tables:
            self.tables[table_name]["column_families"] = new_column_families
            return f"La tabla '{table_name}' ha sido modificada."
        else:
            return f"La tabla '{table_name}' no existe."

    def drop(self, table_name):
        if table_name in self.tables:
            del self.tables[table_name]
            return f"Tabla '{table_name}' eliminada."
        else:
            return f"La tabla '{table_name}' no existe."

    def drop_all(self):
        self.tables.clear()
        return "Todas las tablas han sido eliminadas."

    def describe(self, table_name):
        if table_name in self.tables:
            return self.tables[table_name]["column_families"]
        else:
            return f"La tabla '{table_name}' no existe."

    def put(self, table_name, row_key, column_family, column, value):
        if table_name in self.tables:
            if column_family in self.tables[table_name]["column_families"]:
                timestamp = int(time.time() * 1000)
                self.tables[table_name]["rows"][row_key][(column_family, column)] = {
                    "value": value,
                    "timestamp": timestamp,
                }
                return f"Valor añadido/actualizado en la tabla '{table_name}', row_key '{row_key}', columna '{column_family}:{column}'."
            else:
                return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
        else:
            return f"La tabla '{table_name}' no existe."

    def get(self, table_name, row_key, column_family=None, column=None):
        if table_name in self.tables:
            rows = self.tables[table_name]["rows"]
            if row_key in rows:
                if column_family is None and column is None:
                    return rows[row_key]
                elif (
                    column_family in self.tables[table_name]["column_families"]
                    and column is not None
                ):
                    return rows[row_key].get(
                        (column_family, column), "No se encontró el valor."
                    )
                else:
                    return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
            else:
                return f"El row_key '{row_key}' no existe en la tabla '{table_name}'."
        else:
            return f"La tabla '{table_name}' no existe."

    def scan(
        self, table_name, start_row=None, end_row=None, column_family=None, column=None
    ):
        if table_name in self.tables:
            rows = self.tables[table_name]["rows"]
            if start_row is None:
                start_row = min(rows.keys())
            if end_row is None:
                end_row = max(rows.keys())

            scanned_rows = {}
            for row_key in sorted(rows.keys()):
                if start_row <= row_key <= end_row:
                    if column_family is None and column is None:
                        scanned_rows[row_key] = rows[row_key]
                    elif (
                        column_family in self.tables[table_name]["column_families"]
                        and column is not None
                    ):
                        value = rows[row_key].get(
                            (column_family, column), "No se encontró el valor."
                        )
                        scanned_rows[row_key] = {(column_family, column): value}
                    else:
                        return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
            return scanned_rows
        else:
            return f"La tabla '{table_name}' no existe."

    def delete(self, table_name, row_key, column_family=None, column=None):
        if table_name in self.tables:
            rows = self.tables[table_name]["rows"]
            if row_key in rows:
                if column_family is None and column is None:
                    del rows[row_key]
                    return f"El row_key '{row_key}' ha sido eliminado de la tabla '{table_name}'."
                elif (
                    column_family in self.tables[table_name]["column_families"]
                    and column is not None
                ):
                    if (column_family, column) in rows[row_key]:
                        del rows[row_key][(column_family, column)]
                        return f"El valor de la columna '{column_family}:{column}' ha sido eliminado en el row_key '{row_key}' de la tabla '{table_name}'."
                    else:
                        return f"No se encontró el valor de la columna '{column_family}:{column}' en el row_key '{row_key}' de la tabla '{table_name}'."
                else:
                    return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
            else:
                return f"El row_key '{row_key}' no existe en la tabla '{table_name}'."
        else:
            return f"La tabla '{table_name}' no existe."

    def delete_all(self, table_name):
        if table_name in self.tables:
            self.tables[table_name]["rows"].clear()
            return f"Todos los datos en la tabla '{table_name}' han sido eliminados."
        else:
            return f"La tabla '{table_name}' no existe."

    def count(self, table_name):
        if table_name in self.tables:
            return len(self.tables[table_name]["rows"])
        else:
            return f"La tabla '{table_name}' no existe."

    def truncate(self, table_name):
        if table_name in self.tables:
            column_families = self.tables[table_name]["column_families"]
            self.disable(table_name)
            self.drop(table_name)
            self.create(table_name, column_families)
            return f"La tabla '{table_name}' ha sido truncada."
        else:
            return f"La tabla '{table_name}' no existe."

    # Puntos extra
    def update_many(self, table_name, data):
        if table_name in self.tables:
            for row_key, columns in data.items():
                for (column_family, column), value in columns.items():
                    self.put(table_name, row_key, column_family, column, value)
            return f"Los datos de la tabla '{table_name}' se han actualizado."
        else:
            return f"La tabla '{table_name}' no existe."

    def insert_many(self, table_name, data):
        if table_name in self.tables:
            for row_key, columns in data.items():
                for (column_family, column), value in columns.items():
                    if (column_family, column) not in self.tables[table_name]["rows"][
                        row_key
                    ]:
                        self.put(table_name, row_key, column_family, column, value)
            return f"Los datos se han insertado en la tabla '{table_name}'."
        else:
            return f"La tabla '{table_name}' no existe."


class HBaseGUI:
    def __init__(self, hbase_instance):
        self.hbase = hbase_instance
        self.root = tk.Tk()
        self.root.title("HBase GUI")

        self.text_box = tk.Entry(self.root, width=50)
        self.text_box.pack()

        self.submit_button = tk.Button(
            self.root, text="Ejecutar comando", command=self.execute_command
        )
        self.submit_button.pack()

        self.root.mainloop()

    def execute_command(self):
        command = self.text_box.get()
        result = self.run_command(command)
        messagebox.showinfo("Resultado", result)

    def run_command(self, command):
        tokens = command.split(" ")

        if tokens[0].lower() == "create":
            table_name = tokens[1]
            column_families = tokens[2:]
            return self.hbase.create(table_name, column_families)
        elif tokens[0].lower() == "list_tables":
            return ", ".join(self.hbase.list_tables())
        elif tokens[0].lower() == "disable":
            table_name = tokens[1]
            return self.hbase.disable(table_name)
        elif tokens[0].lower() == "is_enabled":
            table_name = tokens[1]
            return str(self.hbase.is_enabled(table_name))
        elif tokens[0].lower() == "alter":
            table_name = tokens[1]
            new_column_families = tokens[2:]
            return self.hbase.alter(table_name, new_column_families)
        elif tokens[0].lower() == "drop":
            table_name = tokens[1]
            return self.hbase.drop(table_name)
        elif tokens[0].lower() == "drop_all":
            return self.hbase.drop_all()
        elif tokens[0].lower() == "describe":
            table_name = tokens[1]
            return ", ".join(self.hbase.describe(table_name))
        elif tokens[0].lower() == "put":
            table_name = tokens[1]
            row_key = tokens[2]
            column_family = tokens[3]
            column = tokens[4]
            value = tokens[5]
            return self.hbase.put(table_name, row_key, column_family, column, value)
        elif tokens[0].lower() == "get":
            table_name = tokens[1]
            row_key = tokens[2]
            column_family = tokens[3] if len(tokens) > 3 else None
            column = tokens[4] if len(tokens) > 4 else None
            return self.hbase.get(table_name, row_key, column_family, column)
        elif tokens[0].lower() == "scan":
            table_name = tokens[1]
            start_row = tokens[2] if len(tokens) > 2 else None
            end_row = tokens[3] if len(tokens) > 3 else None
            column_family = tokens[4] if len(tokens) > 4 else None
            column = tokens[5] if len(tokens) > 5 else None
            return self.hbase.scan(
                table_name, start_row, end_row, column_family, column
            )
        elif tokens[0].lower() == "insert_many":
            table_name = tokens[1]
            data = json.loads(
                " ".join(tokens[2:])
            )  # Asume que los datos se proporcionan en formato JSON
            return self.hbase.insert_many(table_name, data)
        elif tokens[0].lower() == "update_many":
            table_name = tokens[1]
            data = json.loads(
                " ".join(tokens[2:])
            )  # Asume que los datos se proporcionan en formato JSON
            return self.hbase.update_many(table_name, data)
        else:
            return "Comando desconocido."


# Instancia la clase HBase y la clase HBaseGUI
hbase = HBase()
hbase_gui = HBaseGUI(hbase)
