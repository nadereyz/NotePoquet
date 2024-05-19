from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum
from sqlalchemy.orm import relationship
from flask_login import current_user, LoginManager, login_required, login_user, UserMixin, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging

# Configuración básica de la aplicación Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = '02465b5fb42354857676a27e1446b72ef503ee4e686a6cf4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicialización de la base de datos
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

def init_db(app):
    db.init_app(app)

# Modelo de la base de datos para tareas
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(Enum('Nueva', 'En progreso', 'Finalizada', name="status"), default='Nueva', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship("User", back_populates="tasks")

# Modelo de la base de datos para usuarios
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    workspace_name = db.Column(db.String(100))
    tasks = relationship("Task", back_populates="user")

    def is_active(self):
        return True

# Ruta para mover tareas a "En progreso"
@app.route('/move_to_progress/<int:task_id>', methods=['POST'])
@login_required
def move_to_progress(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == 'Nueva':
        task.status = 'En progreso'
        db.session.commit()
        flash(f'Tarea "{task.title}" ha sido movida a "En progreso".', 'success')
    else:
        flash(f'La tarea "{task.title}" ya está en progreso o finalizada.', 'info')
    return redirect(url_for('workspace'))

# Ruta para iniciar o finalizar tareas
@app.route('/start_or_finish_task/<int:task_id>', methods=['POST'])
@login_required
def start_or_finish_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == 'Nueva':
        return move_to_progress(task_id)
    elif task.status == 'En progreso':
        return finish_task(task_id)
    else:
        flash(f'La tarea "{task.title}" ya está finalizada.', 'info')
        return redirect(url_for('workspace'))

# Ruta para registrar nuevos usuarios
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        try:
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            
            comprobar_usuario = User.query.filter_by(username=username).first()
            if comprobar_usuario:
                flash('El nombre de usuario ya está en uso. Por favor, elige otro.', 'error')
                return redirect(url_for('registrar'))
            
            comprobar_correo = User.query.filter_by(email=email).first()
            if comprobar_correo:
                flash('El correo electrónico ya está en uso. Por favor, utiliza otro.', 'error')
                return redirect(url_for('registrar'))
            
            hashed_password = generate_password_hash(password)
            new_user = User(username=username, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            
            flash('¡Registro exitoso!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            logging.error(f"Error al registrar el usuario: {e}")
            flash('Ocurrió un error al registrar. Por favor, inténtalo de nuevo.', 'error')
            return redirect(url_for('registrar'))
    return render_template('registrar.html')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ruta para añadir nuevas tareas
@app.route('/add_task', methods=['POST'])
@login_required
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    if title and description:
        new_task = Task(title=title, description=description, status="Nueva", user_id=current_user.id)
        db.session.add(new_task)
        db.session.commit()
        flash('Tarea añadida correctamente.', 'success')
    else:
        flash('Título y descripción son necesarios.', 'error')
    return redirect(url_for('workspace'))

# Ruta para el login de usuarios
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Credenciales incorrectas. Por favor, inténtalo de nuevo.', 'error')
    return render_template('login.html')

# Ruta para la página principal
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Ruta para el espacio de trabajo
@app.route('/workspace', methods=['GET', 'POST'])
@login_required
def workspace():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title and description:
            new_task = Task(title=title, description=description, status="Nueva", user_id=current_user.id)
            db.session.add(new_task)
            db.session.commit()
            return redirect(url_for('workspace'))

    workspace_name = current_user.workspace_name
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    return render_template('workspace.html', workspace_name=workspace_name, tasks=tasks)

# Ruta para actualizar tareas
@app.route('/update_task/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    title = request.form.get('title')
    description = request.form.get('description')
    status = request.form.get('status')

    if title:
        task.title = title
    if description:
        task.description = description
    if status:
        task.status = status

    db.session.commit()
    flash('Tarea actualizada correctamente.', 'success')
    return redirect(url_for('workspace'))

# Ruta para eliminar tareas
@app.route('/delete_task/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Tarea eliminada correctamente.', 'success')
    return redirect(url_for('workspace'))

# Ruta para iniciar tareas
@app.route('/start_task/<int:task_id>', methods=['POST'])
@login_required
def start_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == 'Nueva':
        task.status = 'En progreso'
        db.session.commit()
        flash(f'Tarea "{task.title}" ha sido iniciada correctamente.', 'success')
    else:
        flash(f'La tarea "{task.title}" ya está en progreso.', 'info')
    return redirect(url_for('workspace'))

# Ruta para finalizar tareas
@app.route('/finish_task/<int:task_id>', methods=['POST'])
@login_required
def finish_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.status == 'En progreso':
        task.status = 'Finalizada'
        db.session.commit()
        flash(f'Tarea "{task.title}" ha sido finalizada.', 'success')
    else:
        flash(f'La tarea "{task.title}" ya está finalizada.', 'info')
    return redirect(url_for('workspace'))

# Ruta para crear un nuevo espacio de trabajo
@app.route('/crear_workspace', methods=['GET', 'POST'])
@login_required
def crear_workspace():
    if request.method == 'POST':
        workspace_name = request.form.get('workspace_name')
        if workspace_name:
            current_user.workspace_name = workspace_name  
            db.session.commit()
            flash('Espacio de trabajo creado correctamente.', 'success')
            return redirect(url_for('workspace'))
        else:
            flash('Debe ingresar un nombre para el espacio de trabajo.', 'error')
    return render_template('crear_workspace.html')

# Ruta para recuperar contraseña (aún no implementada)
@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

# Ruta para cerrar sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión correctamente.', 'success')
    return redirect(url_for('login'))

# Inicialización de la base de datos
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
