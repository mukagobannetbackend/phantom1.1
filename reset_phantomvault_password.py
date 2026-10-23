
import getpass
import psycopg
from werkzeug.security import generate_password_hash, check_password_hash

EMAIL = "samkagarara@gmail.com"
EXPECTED_ID = 2

def main():
    database_url = getpass.getpass(
        "Current Render External Database URL (hidden): "
    ).strip()

    if not database_url:
        print("No database URL supplied. Nothing changed.")
        return

    new_password = getpass.getpass(
        "Enter your NEW password (hidden): "
    )
    confirm_password = getpass.getpass(
        "Confirm your NEW password (hidden): "
    )

    if new_password != confirm_password:
        print("Passwords do not match. Nothing changed.")
        return

    if len(new_password) < 12:
        print("Use at least 12 characters. Nothing changed.")
        return

    new_hash = generate_password_hash(new_password)

    try:
        with psycopg.connect(database_url) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    '''
                    SELECT id, email
                    FROM "user"
                    WHERE lower(email) = lower(%s)
                    ''',
                    (EMAIL,),
                )
                account = cur.fetchone()

                if account is None:
                    print("Account not found. Nothing changed.")
                    return

                account_id, account_email = account

                if account_id != EXPECTED_ID:
                    print(
                        f"Safety check failed: expected account ID "
                        f"{EXPECTED_ID}, found {account_id}. Nothing changed."
                    )
                    return

                print(f"Account found: ID {account_id}, {account_email}")
                approval = input(
                    "Type RESET to update ONLY this account's password: "
                )

                if approval != "RESET":
                    print("Cancelled. Nothing changed.")
                    return

                cur.execute(
                    '''
                    UPDATE "user"
                    SET password_hash = %s
                    WHERE id = %s
                      AND lower(email) = lower(%s)
                    ''',
                    (new_hash, EXPECTED_ID, EMAIL),
                )

                if cur.rowcount != 1:
                    conn.rollback()
                    print(
                        "Safety check failed during update. "
                        "Changes rolled back."
                    )
                    return

                conn.commit()

                if check_password_hash(new_hash, new_password):
                    print(
                        "PASSWORD RESET SUCCESSFUL. "
                        "Account ID and trade records were not changed."
                    )
                else:
                    print(
                        "The stored password needs further verification. "
                        "Do not repeat the update yet."
                    )

    except psycopg.Error:
        print(
            "Database operation failed. Check the connection settings. "
            "No database details have been printed."
        )

if __name__ == "__main__":
    main()
