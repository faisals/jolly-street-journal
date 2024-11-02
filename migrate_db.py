from app import app, db

def migrate_database():
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables with updated schema...")
        db.create_all()
        print("Database migration completed successfully.")

if __name__ == "__main__":
    migrate_database()
