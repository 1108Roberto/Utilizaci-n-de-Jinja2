from flask import Flask, render_template, request, redirect, url_for, flash
import redis
import json

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Configurar la conexión a Redis
client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

@app.route('/')
def index():
    keys = client.keys('receta:*')
    recetas = []
    for key in keys:
        receta_str = client.get(key)
        receta = json.loads(receta_str)
        receta['id'] = key.split(':')[1]  # Extrae el ID de la receta
        recetas.append(receta)
    return render_template('index.html', recetas=recetas)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        id = client.incr('receta_id')  # Incrementa el ID para crear un nuevo ID único
        nombre = request.form['nombre']
        ingredientes = request.form['ingredientes']
        pasos = request.form['pasos']
        receta = {
            'nombre': nombre,
            'ingredientes': ingredientes,
            'pasos': pasos
        }
        client.set(f'receta:{id}', json.dumps(receta))
        flash('Receta agregada exitosamente.')
        return redirect(url_for('index'))
    return render_template('agregar.html')

@app.route('/actualizar/<id>', methods=['GET', 'POST'])
def actualizar(id):
    receta_str = client.get(f'receta:{id}')
    if not receta_str:
        flash('Receta no encontrada.')
        return redirect(url_for('index'))

    receta = json.loads(receta_str)

    if request.method == 'POST':
        receta['nombre'] = request.form['nombre']
        receta['ingredientes'] = request.form['ingredientes']
        receta['pasos'] = request.form['pasos']
        client.set(f'receta:{id}', json.dumps(receta))
        flash('Receta actualizada exitosamente.')
        return redirect(url_for('index'))

    return render_template('actualizar.html', receta=receta)

@app.route('/eliminar/<id>', methods=['POST'])
def eliminar(id):
    result = client.delete(f'receta:{id}')
    if result:
        flash('Receta eliminada exitosamente.')
    else:
        flash('Receta no encontrada.')
    return redirect(url_for('index'))

@app.route('/buscar', methods=['GET', 'POST'])
def buscar():
    receta = None
    if request.method == 'POST':
        id = request.form['id']
        receta_str = client.get(f'receta:{id}')
        if receta_str:
            receta = json.loads(receta_str)
        else:
            flash('Receta no encontrada.')
    return render_template('buscar.html', receta=receta)

if __name__ == '__main__':
    app.run(debug=True)
