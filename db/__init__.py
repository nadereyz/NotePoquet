from flask_sqlalchemy import SQLAlchemy

# Inicializa el objeto SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Función para inicializar la base de datos con la aplicación Flask."""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mydatabase.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
