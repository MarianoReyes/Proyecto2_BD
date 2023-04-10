from flask import Flask, render_template, request, redirect
import pickle

import pickle

app = Flask(__name__)

# Cargar HFile desde el disco
with open("hfile.pickle", "rb") as f:
    hfile = pickle.load(f)

# Ruta para la página de inicio
with open("hfile.pickle", "wb") as f:
    pickle.dump(hfile, f)


@app.route("/")
def index():
    rows = hfile.items()
    return render_template("index.html", rows=rows)

# Ruta para editar una fila específica


@app.route("/edit/<row_key>/<column_family>/<timestamp>", methods=["GET", "POST"])
def edit(row_key, column_family, timestamp):
    row = hfile[row_key]
    value = row[column_family][int(timestamp)]

    if request.method == "POST":
        # Actualizar el valor de la columna
        new_value = request.form["value"]
        row[column_family][int(timestamp)] = new_value

        # Guardar HFile en disco
        with open("hfile.pickle", "wb") as f:
            pickle.dump(hfile, f)

        return redirect("/")

    return render_template("edit.html", row_key=row_key, column_family=column_family, timestamp=timestamp, value=value)
