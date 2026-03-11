from app import app, db
from sqlalchemy import text

with app.app_context():
    try:
        # Manually add the email column to the user table
        db.session.execute(text('ALTER TABLE user ADD COLUMN email VARCHAR(120)'))
        db.session.commit()
        print("Successfully added email column to User table.")
    except Exception as e:
        print(f"Error: {e}")