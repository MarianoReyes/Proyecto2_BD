from flask import Flask, request, jsonify

app = Flask(__name__)

# Ejemplo de datos de la tabla
table_data = {
    'row1': {'column1': 'value1', 'column2': 'value2'},
    'row2': {'column1': 'value3', 'column2': 'value4'}
}

# Ruta para obtener una celda específica


@app.route('/get_cell')
def get_cell():
    row_key = request.args.get('row_key')
    column_key = request.args.get('column_key')
    if row_key in table_data and column_key in table_data[row_key]:
        return jsonify({'value': table_data[row_key][column_key]})
    else:
        return jsonify({'error': 'Cell not found'})

# Ruta para poner una celda específica


@app.route('/put_cell', methods=['POST'])
def put_cell():
    row_key = request.form.get('row_key')
    column_key = request.form.get('column_key')
    value = request.form.get('value')
    if row_key not in table_data:
        table_data[row_key] = {}
    table_data[row_key][column_key] = value
    return jsonify({'success': True})

# Ruta para eliminar una celda específica


@app.route('/delete_cell', methods=['POST'])
def delete_cell():
    row_key = request.form.get('row_key')
    column_key = request.form.get('column_key')
    if row_key in table_data and column_key in table_data[row_key]:
        del table_data[row_key][column_key]
        return jsonify({'success': True})
    else:
        return jsonify({'error': 'Cell not found'})

# Ruta para obtener todas las celdas de una fila específica


@app.route('/get_row')
def get_row():
    row_key = request.args.get('row_key')
    if row_key in table_data:
        return jsonify(table_data[row_key])
    else:
        return jsonify({'error': 'Row not found'})

# Ruta para escanear todas las celdas de la tabla


@app.route('/scan_table')
def scan_table():
    return jsonify(table_data)


if __name__ == '__main__':
    app.run()
