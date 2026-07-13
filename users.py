from database import (
    add_user,
    get_user,
    get_connection
)


def create_user(telegram_id, name, role="USER"):
    add_user(
        telegram_id,
        name,
        role
    )


def find_user(telegram_id):
    return get_user(telegram_id)


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, telegram_id, name, role, status
    FROM users
    """)

    users = cursor.fetchall()

    conn.close()

    return users


def update_user_status(telegram_id, status):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET status=?
    WHERE telegram_id=?
    """,
    (
        status,
        telegram_id
    ))

    conn.commit()
    conn.close()


def update_user_role(telegram_id, role):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE users
    SET role=?
    WHERE telegram_id=?
    """,
    (
        role,
        telegram_id
    ))

    conn.commit()
    conn.close()
