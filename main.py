import time
from collections import defaultdict
import tkinter as tk
from tkinter import ttk
import json
import random
import string
import pandas as pd

# Configurar opciones de visualización para mostrar toda la data
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)

# Data inicial
def generar_usuario(row_key):
    return {
        row_key: {
            "info_personal": {
                "nombre": "".join(
                    random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5)
                ),
                "edad": random.randint(18, 99),
            },
            "contacto": {
                "email": "".join(random.choices(string.ascii_lowercase, k=5))
                + "@example.com",
                "telefono": "555" + str(random.randint(10000, 99999)),
            },
        }
    }


def generar_compra(row_key):
    return {
        row_key: {
            "producto": {
                "nombre": "".join(random.choices(string.ascii_uppercase, k=3)),
                "precio": random.uniform(10, 100),
            },
            "transaccion": {
                "fecha": f"2023-04-{random.randint(1, 16)}",
                "cantidad": random.randint(1, 11),
            },
        }
    }


class HBase:
    def __init__(self):
        self.tables = {}

    def create(self, table_name, column_families):
        if table_name not in self.tables:
            cf_dict = {}
            for cf in column_families:
                cf_dict[cf] = set()
            self.tables[table_name] = {
                "column_families": cf_dict,
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

    def enable(self, table_name):
        if table_name in self.tables:
            self.tables[table_name]["enabled"] = True
            return f"Tabla '{table_name}' habilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def is_enabled(self, table_name):
        return self.tables.get(table_name, {}).get("enabled", False)

    def alter(
        self, table_name, column_family, action, *columns, new_column_family=None
    ):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
                if column_family in self.tables[table_name]["column_families"]:
                    if action == "modify":
                        if new_column_family is not None:
                            self.tables[table_name]["column_families"][
                                new_column_family
                            ] = self.tables[table_name]["column_families"].pop(
                                column_family
                            )
                            for row_key in self.tables[table_name]["rows"]:
                                for (cf, column) in list(
                                    self.tables[table_name]["rows"][row_key].keys()
                                ):
                                    if cf == column_family:
                                        value, timestamp = self.tables[table_name][
                                            "rows"
                                        ][row_key].pop((cf, column))
                                        self.tables[table_name]["rows"][row_key][
                                            (new_column_family, column)
                                        ] = {
                                            "value": value,
                                            "timestamp": timestamp,
                                        }
                            return f"La familia de columnas '{column_family}' ha sido modificada a '{new_column_family}' en la tabla '{table_name}'."
                        else:
                            return f"El nuevo nombre de la familia de columnas no puede ser None."
                    elif action == "delete":
                        del self.tables[table_name]["column_families"][column_family]
                        for row_key in self.tables[table_name]["rows"]:
                            for (cf, column) in list(
                                self.tables[table_name]["rows"][row_key].keys()
                            ):
                                if cf == column_family:
                                    del self.tables[table_name]["rows"][row_key][
                                        (cf, column)
                                    ]
                        return f"La familia de columnas '{column_family}' ha sido eliminada de la tabla '{table_name}'."
                    else:
                        return f"La acción '{action}' no es válida. Utilice 'modify' o 'delete'."
                else:
                    return f"La familia de columnas '{column_family}' no existe en la tabla '{table_name}'."
            else:
                return f"La tabla '{table_name}' está deshabilitada."
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
            if self.tables[table_name]["enabled"] == True:
                if (
                    column_family in self.tables[table_name]["column_families"]
                    and column is not None
                ):
                    timestamp = int(time.time() * 1000)
                    self.tables[table_name]["rows"][row_key][
                        (column_family, column)
                    ] = {
                        "value": value,
                        "timestamp": timestamp,
                    }
                    return f"Valor '{value}' añadido/actualizado en la tabla '{table_name}', row_key '{row_key}', columna '{column_family}:{column}'."
                else:
                    return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def get(self, table_name, row_key, column_family=None, column=None):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
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
                    return (
                        f"El row_key '{row_key}' no existe en la tabla '{table_name}'."
                    )
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def scan(
        self, table_name, start_row=None, end_row=None, column_family=None, column=None
    ):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
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
                            value, timestamp = rows[row_key].get(
                                (column_family, column),
                                ("No se encontró el valor.", None),
                            )
                            scanned_rows[row_key] = {
                                (column_family, column): {
                                    "value": value,
                                    "timestamp": timestamp,
                                }
                            }
                        else:
                            return f"La columna '{column_family}:{column}' no existe en la tabla '{table_name}'."
                return pd.DataFrame(scanned_rows).transpose()
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def delete(self, table_name, row_key, column_family=None, column=None):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
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
                    return (
                        f"El row_key '{row_key}' no existe en la tabla '{table_name}'."
                    )
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def delete_all(self, table_name):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
                self.tables[table_name]["rows"].clear()
                return (
                    f"Todos los datos en la tabla '{table_name}' han sido eliminados."
                )
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def count(self, table_name):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
                return len(self.tables[table_name]["rows"])
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def truncate(self, table_name):
        messages = []
        messages.append(f"1: Ver si la tabla '{table_name}' existe.")
        if table_name in self.tables:
            messages.append(f"2: Ver si la tabla '{table_name}' esta habilitada.")
            if self.tables[table_name]["enabled"] == True:
                column_families = self.tables[table_name]["column_families"]
                messages.append(f"3: deshabilitando tabla '{table_name}'.")
                self.disable(table_name)
                messages.append(f"4: dropeando la tabla '{table_name}'.")
                self.drop(table_name)
                messages.append(
                    f"5: Recreando la tabla '{table_name}' con las mismas column families."
                )
                self.create(table_name, column_families)
                messages.append(f"6. La tabla '{table_name}' ha sido truncada.")
            else:
                messages.append(f"La tabla '{table_name}' está deshabilitada.")
        else:
            messages.append(f"La tabla '{table_name}' no existe.")
        return messages

    # Puntos extra
    def check_column_families(self, table_name, data):
        table_cfs = set(self.tables[table_name]["column_families"].keys())
        input_cfs = {
            cf for row in data.values() for cf in row.keys() if cf != "row_key"
        }

        if not input_cfs.issubset(table_cfs):
            invalid_cfs = input_cfs.difference(table_cfs)
            return (
                False,
                f"Las siguientes familias de columnas no existen en la tabla '{table_name}': {', '.join(invalid_cfs)}",
            )
        return True, ""

    def update_many(self, table_name, data):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
                cf_check, cf_error = self.check_column_families(table_name, data)
                if not cf_check:
                    return cf_error

                for row_key, row in data.items():
                    for cf, columns in row.items():
                        if cf != "row_key":
                            for column, value in columns.items():
                                self.put(table_name, row_key, cf, column, value)
                return f"Datos actualizados en la tabla '{table_name}'."
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."

    def insert_many(self, table_name, data):
        if table_name in self.tables:
            if self.tables[table_name]["enabled"] == True:
                cf_check, cf_error = self.check_column_families(table_name, data)
                if not cf_check:
                    return cf_error

                for row_key, row in data.items():
                    for cf, columns in row.items():
                        if cf != "row_key":
                            for column, value in columns.items():
                                self.put(table_name, row_key, cf, column, value)
                return f"Datos insertados en la tabla '{table_name}'."
            else:
                return f"La tabla '{table_name}' está deshabilitada."
        else:
            return f"La tabla '{table_name}' no existe."


class HBaseGUI:
    def __init__(self, hbase_instance):
        self.hbase = hbase_instance
        self.root = tk.Tk()
        self.root.title("HBase GUI")

        # Configura el margen en los lados izquierdo y derecho
        self.root.pack_propagate(0)
        self.root.geometry("1500x700")
        self.root.minsize(1500, 700)
        self.root.maxsize(1500, 700)

        # Crea un objeto ttk.Style y selecciona el tema "clam"
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configura el estilo para el widget Entry
        self.style.configure(
            "TEntry", foreground="black", background="white", font=("Arial", 12)
        )

        # Configura el estilo para el botón Ejecutar comando
        self.style.configure(
            "TButton", foreground="white", background="#007bff", font=("Arial", 12)
        )

        self.text_box = ttk.Entry(self.root, width=50, style="TEntry")
        self.text_box.pack(padx=20, pady=20)

        self.submit_button = ttk.Button(
            self.root,
            text="Ejecutar comando",
            command=self.execute_command,
            style="TButton",
        )
        self.submit_button.pack(padx=20, pady=20)

        # Crea un widget Text y lo configura para que tenga scrollbars
        self.result_text = tk.Text(
            self.root, font=("Arial", 12), wrap="word", height=10
        )
        self.result_text.pack(expand=True, fill="both", padx=20)
        self.result_text.configure(state="disabled")

        self.scrollbar = tk.Scrollbar(self.root)
        self.scrollbar.pack(side="right", fill="y", anchor="e")

        self.result_text.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.result_text.yview)

        self.root.mainloop()

    def execute_command(self):
        command = self.text_box.get()
        result = self.run_command(command)

        self.result_text.configure(state="normal")

        if isinstance(result, list):
            for message in result:
                self.result_text.insert(
                    "end", ">>> " + command + "\n" + str(message) + "\n\n"
                )
        else:
            self.result_text.insert(
                "end", ">>> " + command + "\n" + str(result) + "\n\n"
            )

        self.result_text.see("end")
        self.result_text.configure(state="disabled")

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
        elif tokens[0].lower() == "enable":
            table_name = tokens[1]
            return self.hbase.enable(table_name)
        elif tokens[0].lower() == "is_enabled":
            table_name = tokens[1]
            return str(self.hbase.is_enabled(table_name))
        elif tokens[0].lower() == "alter":
            table_name = tokens[1]
            action = tokens[2].lower()
            column_family = tokens[3]

            if action == "modify":
                new_column_family = tokens[4]
                columns = tokens[5:]
                return self.hbase.alter(
                    table_name,
                    column_family,
                    action,
                    *columns,
                    new_column_family=new_column_family,
                )
            elif action == "delete":
                return self.hbase.alter(table_name, column_family, action)
            else:
                return "Invalid action. Use 'modify' or 'delete'."
        elif tokens[0].lower() == "drop":
            table_name = tokens[1]
            return self.hbase.drop(table_name)
        elif tokens[0].lower() == "drop_all":
            return self.hbase.drop_all()
        elif tokens[0].lower() == "describe":
            table_name = tokens[1]
            if self.hbase.is_enabled(table_name):
                status = "La tabla esta Habilitada\n\n"
            else:
                status = "La tabla esta Deshabilitada\n\n"
            families = "Las column_families son:\n" + ", ".join(
                self.hbase.describe(table_name)
            )
            return status + families
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
        elif tokens[0].lower() == "delete":
            table_name = tokens[1]
            row_key = tokens[2]
            column_family = tokens[3] if len(tokens) > 3 else None
            column = tokens[4] if len(tokens) > 4 else None
            return self.hbase.delete(table_name, row_key, column_family, column)
        elif tokens[0].lower() == "delete_all":
            table_name = tokens[1]
            return self.hbase.delete_all(table_name)
        elif tokens[0].lower() == "count":
            table_name = tokens[1]
            return self.hbase.count(table_name)
        elif tokens[0].lower() == "truncate":
            table_name = tokens[1]
            return self.hbase.truncate(table_name)
        elif tokens[0].lower() == "insert_many":
            table_name = tokens[1]
            archivo = tokens[2]
            with open(archivo, "r") as f:
                data = json.load(f)
            return self.hbase.insert_many(table_name, data)
        elif tokens[0].lower() == "update_many":
            table_name = tokens[1]
            archivo = tokens[2]
            with open(archivo, "r") as f:
                data = json.load(f)
            return self.hbase.update_many(table_name, data)

        else:
            return "Comando desconocido."


# Instancia la clase HBase y la clase HBaseGUI
hbase = HBase()

# Crea una tabla de usuarios y compras con sus respectivas familias de columnas
hbase.create("usuarios", ["info_personal", "contacto"])
hbase.create("compras", ["producto", "transaccion"])

# Genera datos de usuarios y compras y agrega a la instancia de HBase
for i in range(10):
    usuario = generar_usuario(f"usuario_{i}")
    hbase.insert_many("usuarios", usuario)

    compra = generar_compra(f"compra_{i}")
    hbase.insert_many("compras", compra)


# Simular HFiles
hfiles = {
    "usuarios": hbase.scan("usuarios"),
    "compras": hbase.scan("compras"),
}

# Modificaciones en HBase (para ejemplificar cambios en HFiles)
hbase.put("compras", "compra_20", "producto", "nombre", "ABC")
hbase.put("compras", "compra_20", "producto", "precio", "50.0")
hbase.put("compras", "compra_20", "transaccion", "fecha", "2023-04-16")
hbase.put("compras", "compra_20", "transaccion", "cantidad", "3")

# Actualizar HFiles
hfiles["usuarios"] = hbase.scan("usuarios")
hfiles["compras"] = hbase.scan("compras")

# Verificar que los HFiles se han actualizado
print(hfiles)

hbase_gui = HBaseGUI(hbase)
