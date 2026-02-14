#!/usr/bin/env python
"""Enable RLS on a list of public tables flagged by the linter.

Run this from the project root: `python scripts/enable_rls_flagged_tables.py`
It uses the same environment variables as the repository (`python-decouple`).
"""
import psycopg2
from decouple import config

# Load DB configuration from environment (from .env via python-decouple)
DB_HOST = config('DB_HOST')
DB_NAME = config('DB_NAME')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_PORT = config('DB_PORT', cast=int)

TABLES = [
    'accounts_staff', 'accounts_staffpermission', 'accounts_user', 'accounts_user_groups',
    'accounts_user_user_permissions', 'auth_group', 'auth_group_permissions', 'auth_permission',
    'django_admin_log', 'django_content_type', 'django_migrations', 'django_session',
    'restaurant_category', 'restaurant_menuitem', 'restaurant_order', 'restaurant_orderhistory',
    'restaurant_orderhistoryitem', 'restaurant_orderhistorypayment', 'restaurant_orderhistorystatus',
    'restaurant_orderitem', 'restaurant_orderstatuslog', 'restaurant_payment', 'restaurant_table'
]


def main():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
        )
        cursor = conn.cursor()
        print(f"Connected to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")

        for table in TABLES:
            try:
                sql = f"ALTER TABLE public.\"{table}\" ENABLE ROW LEVEL SECURITY;"
                cursor.execute(sql)
                print(f"Enabled RLS on public.{table}")
            except Exception as e:
                print(f"Failed to enable RLS on {table}: {e}")

        conn.commit()
        cursor.close()
        conn.close()
        print("Done.")
    except Exception as e:
        print(f"Connection error: {e}")


if __name__ == '__main__':
    main()
