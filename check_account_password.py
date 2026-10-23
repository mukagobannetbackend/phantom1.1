
import getpass
import os

import psycopg
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

# Load environment variables if a .env file exists.
load_dotenv()

# Ask for the Render database URL without displaying it.
database_url = getpass.getpass(
    "Paste your CURRENT Render External Database URL (hidden): "
)

if not database_url.strip():
    print("No database URL supplied.")
    raise SystemExit(1)

# Connect to PostgreSQL and read the current account's hash.
try:
    with psycopg.connect(database_url.strip()) as conn:
        with conn.cursor() as cur:
            cur.execute(
                '''
                SELECT password_hash
                FROM "user"
                WHERE lower(email) = lower(%s)
            ''',
                ("samkagarara@gmail.com",),
            )
            row = cur.fetchone()

    if row is None:
        print("ACCOUNT NOT FOUND in the current user table.")
        raise SystemExit(1)

    password = getpass.getpass(
        "Enter the password you want to test (hidden): "
    )

    if check_password_hash(row[0], password):
        print("PASSWORD MATCH")
    else:
        print("PASSWORD DOES NOT MATCH")

except psycopg.Error:
    print(
        "DATABASE CONNECTION OR QUERY FAILED. "
        "Check the database URL and connection settings."
    )
