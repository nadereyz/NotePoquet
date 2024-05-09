from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from db import db, init_db
from sqlalchemy import Enum


app = Flask(__name__)



app.config['SECRET_KEY'] = '02465b5fb42354857676a27e1446b72ef503ee4e686a6cf4'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
init_db(app)



class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    status = db.Column(Enum('Nueva', 'En progreso', 'Finalizada', name="status"), default='Nueva', nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        new_user = User(username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registrar.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['usuario']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            return redirect(url_for('home'))
        else:
            return render_template('login.html', error='Usuario o contraseña incorrectos.')
    return render_template('login.html')


@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/workspace', methods=['GET', 'POST'])
def workspace():
    workspace_name = 'Nombre Default del Workspace'
    if request.method == 'POST':
        workspace_name = request.form.get('workspace_name', workspace_name)
    tasks = Task.query.all()
    return render_template('workspace.html', workspace_name=workspace_name, tasks=tasks)


@app.route('/workspace/<workspace_name>')
def workspace_name(workspace_name):
    return render_template('workspace.html', workspace_name=workspace_name)

@app.route('/add_task', methods=['GET', 'POST'])
def add_task():
    title = request.form.get('title')
    description = request.form.get('description')
    if title and description:
        new_task = Task(title=title, description=description, status="Nueva")
        db.session.add(new_task)
        db.session.commit()
    return redirect(url_for('workspace'))

@app.route('/update_task/<int:task_id>', methods=['GET', 'POST'])
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
    return redirect(url_for('workspace'))
    
@app.route('/delete_task/<int:task_id>', methods=['GET', 'POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('workspace'))

@app.route('/start_task/<int:task_id>', methods=['GET', 'POST'])
def start_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.status == 'Nueva':
        task.status = 'En progreso'
        db.session.commit()
        flash(f'Tarea "{task.title}" ha sido iniciada.', 'success')
    else:
        flash(f'La tarea "{task.title}" ya está en progreso.', 'info')
    
    return redirect(url_for('workspace'))
    
@app.route('/finish_task/<int:task_id>', methods=['GET', 'POST'])
def finish_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    if task.status == 'En progreso':
        task.status = 'Finalizada'
        db.session.commit()
        flash(f'Tarea "{task.title}" ha sido finalizada.', 'success')
    else:
        flash(f'La tarea "{task.title}" ya está finalizada.', 'info')
    
    return redirect(url_for('workspace'))


@app.route('/crear_workspace', methods=['GET', 'POST'])
def crear_workspace():
    if request.method == 'POST':
        workspace_name = request.form['workspace_name']
        return redirect(url_for('workspace_name', workspace_name=workspace_name))
    return render_template('crear_workspace.html')

@app.route('/recuperar')
def recuperar():
    return render_template('recuperar.html')

@app.route('/trabajo')
def trabajo():
    df = pd.DataFrame({
        'Tarea': ['Tarea 1', 'Tarea 2', 'Tarea 3', 'Tarea 4'],
        'Fecha de entrega': ['2024-04-11', '2024-04-12', '2024-04-13', '2024-04-14'],
        'Completada': [False, False, True, False]
    })
    tareas_no_completadas = df[df['Completada'] == False]
    return render_template('trabajo.html', tareas_no_completadas=tareas_no_completadas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)