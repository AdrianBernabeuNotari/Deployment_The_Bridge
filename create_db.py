# .py para crear la base de datos
from app import app, db

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("Si sale esto ha funcionado")