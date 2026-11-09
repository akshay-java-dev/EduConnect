
from sqlalchemy import inspect, text
from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():

    inspector = inspect(db.engine)

    columns = [
        column["name"]
        for column in inspector.get_columns("exam")
    ]

    if "subject_id" not in columns:

        with db.engine.begin() as connection:

            connection.execute(
                text(
                    "ALTER TABLE exam "
                    "ADD COLUMN subject_id INTEGER "
                    "REFERENCES subject(id)"
                )
            )

        print("SUCCESS: Exam subject column added!")

    else:

        print("SUCCESS: Exam subject column already exists!")
