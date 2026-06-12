from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from functools import wraps

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'renta'
mysql = MySQL(app)
app.secret_key = '123456'

# Decorador para verificar sesión activa
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('Index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def Index():
    return render_template('index.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM usuario WHERE usuario = %s AND contraseña = %s', (usuario, contraseña))
        user = cursor.fetchone()
        if user:
            session['logged_in'] = True
            session['usuario'] = user[1]  
            return redirect(url_for('menu'))
        else:
            return render_template(
            'index.html',
            error='Usuario o contraseña incorrectos')    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('usuario', None)
    return redirect(url_for('Index'))

@app.route('/menu', methods=['GET', 'POST'])
def menu():
    if 'logged_in' in session:
        return render_template('menu.html')
    else:
        return redirect(url_for('Index'))

#-- Funciones para agregar libros, clientes, rentas y Categorías---------------------------------------------
@app.route('/add_libro', methods=['GET', 'POST'])
@login_required
def add_libro():
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        titulo = request.form['titulo']
        autor = request.form['autor']
        categorias = request.form['categorias']
        
        cur.execute("INSERT INTO libros (titulo, autor, categorias) VALUES (%s, %s, %s)", (titulo, autor, categorias))
        mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM categorias")
    categorias = cur.fetchall()
    return render_template('add_libro.html', categorias=categorias)

@app.route('/add_cliente', methods=['GET', 'POST'])
@login_required
def add_cliente():
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO clientes (nombre, telefono, correo) VALUES (%s, %s, %s)", (nombre, telefono, correo))
        mysql.connection.commit()
    return render_template('add_cliente.html')

@app.route('/add_renta', methods=['GET', 'POST'])
@login_required
def add_renta():
    if request.method == 'POST':
        cliente = request.form['cliente']
        libro = request.form['libro']
        cantidad = request.form['cantidad']
        fecha_renta = request.form['fecha_renta']
        fecha_devolucion = request.form['fecha_devolucion']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO renta (cliente, libro, cantidad, fecha_renta, fecha_devolucion) VALUES (%s, %s, %s, %s, %s)", (cliente, libro, cantidad, fecha_renta, fecha_devolucion))
        mysql.connection.commit()
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()
    return render_template('add_renta.html', clientes=clientes, libros=libros)

@app.route('/add_categoria', methods=['GET', 'POST'])
@login_required
def add_categoria():
    if request.method == 'POST':
        nombre = request.form['nombre']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO categorias (nombre_categoria) VALUES (%s)", (nombre,))
        mysql.connection.commit()
    return render_template('add_categoria.html')


#-- Funciones para mostrar libros, clientes y rentas-------------------------------------------------------------
@app.route('/rentas')
@login_required
def view_renta():
    cur = mysql.connection.cursor()
    cur.execute("SELECT t3.id_renta,t1.nombre, t2.titulo, t3.cantidad, t3.fecha_renta, t3.fecha_devolucion " \
    "FROM clientes t1 JOIN renta t3 ON t1.id_cliente = t3.cliente JOIN libros t2 ON t3.libro = t2.id_libro")
    rentas = cur.fetchall()
    return render_template('rentas.html', rentas=rentas)

@app.route('/libros')
@login_required
def view_libros():
    cur = mysql.connection.cursor()
    cur.execute("SELECT t1.id_libro, t1.titulo, t1.autor, t2.nombre_categoria FROM libros t1 JOIN categorias t2 ON t1.categorias = t2.id_categoria")
    libros = cur.fetchall()
    return render_template('libros.html', libros=libros)

@app.route('/clientes')
@login_required
def view_clientes():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    return render_template('clientes.html', clientes=clientes)

#-- Funciones para editar y eliminar libros, clientes y rentas --------------------------------------------------------
#-- Editar y eliminar libros --
@app.route('/edit_libro/<int:id>', methods=['GET'])
@login_required
def get_libro(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM libros WHERE id_libro=%s", (id,))
    libro = cur.fetchone()
    cur.execute("SELECT * FROM categorias")
    categorias = cur.fetchall()
    return render_template('edit_libro.html', libro=libro, categorias=categorias)

@app.route('/update_libro/<int:id>', methods=['POST'])
@login_required
def update_libro(id):
    if request.method == 'POST':
        titulo = request.form['titulo']
        autor = request.form['autor']
        categorias = request.form['categorias']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE libros
            SET titulo=%s, autor=%s, categorias=%s
            WHERE id_libro=%s
        """, (titulo, autor, categorias, id))
        mysql.connection.commit()
    return redirect(url_for('view_libros'))

@app.route('/delete_libro/<int:id>')
@login_required
def delete_libro(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM libros WHERE id_libro=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('view_libros'))

#-- Editar y eliminar clientes --
@app.route('/edit_cliente/<int:id>', methods=['GET'])
@login_required
def get_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM clientes WHERE id_cliente=%s", (id,))
    clientes = cur.fetchone()
    return render_template('edit_cliente.html', clientes=clientes)

@app.route('/update_cliente/<int:id>', methods=['POST'])
@login_required
def update_cliente(id):
    if request.method == 'POST':
        nombre = request.form['nombre']
        telefono = request.form['telefono']
        correo = request.form['correo']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE clientes
            SET nombre=%s, telefono=%s, correo=%s
            WHERE id_cliente=%s
        """, (nombre, telefono, correo, id))
        mysql.connection.commit()
    return redirect(url_for('view_clientes'))

@app.route('/delete_cliente/<int:id>')
@login_required
def delete_cliente(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM clientes WHERE id_cliente=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('view_clientes'))

#-- Editar y eliminar rentas --
@app.route('/edit_renta/<int:id>', methods=['GET'])
@login_required
def get_renta(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM renta WHERE id_renta=%s", (id,))
    renta = cur.fetchone()
    cur.execute("SELECT * FROM clientes")
    clientes = cur.fetchall()
    cur.execute("SELECT * FROM libros")
    libros = cur.fetchall()
    return render_template('edit_renta.html', renta=renta, clientes=clientes, libros=libros
    )

@app.route('/update_renta/<int:id>', methods=['POST'])
@login_required
def update_renta(id):
    if request.method == 'POST':
        cliente = request.form['cliente']
        libro = request.form['libro']
        cantidad = request.form['cantidad']
        fecha_renta = request.form['fecha_renta']
        fecha_devolucion = request.form['fecha_devolucion']
        cur = mysql.connection.cursor()
        cur.execute("""
            UPDATE renta
            SET cliente=%s, libro=%s, cantidad=%s, fecha_renta=%s, fecha_devolucion=%s
            WHERE id_renta=%s
        """, (cliente, libro, cantidad, fecha_renta, fecha_devolucion, id))
        mysql.connection.commit()
    cur = mysql.connection.cursor()
    return redirect(url_for('view_renta'))

@app.route('/delete_renta/<int:id>')
@login_required
def delete_renta(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM renta WHERE id_renta=%s", (id,))
    mysql.connection.commit()
    return redirect(url_for('view_renta'))



if __name__ == '__main__':
    app.run(port=3000, debug=True)