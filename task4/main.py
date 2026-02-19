import psycopg
import argparse
import sys

from show_table import show_table
from update_table import update_table

HOST = "localhost"
PORT = 5432
DBNAME = "shop_system"
USER = "postgres"
PASSWORD = ""

def main():
    parser = argparse.ArgumentParser(description="Simple DB inspector for shop_system")
    parser.add_argument("--host", default=HOST)
    parser.add_argument("--port", default=PORT, type=int)
    parser.add_argument("--dbname", default=DBNAME)
    parser.add_argument("--user", default=USER)
    parser.add_argument("--password", default=PASSWORD)
    args = parser.parse_args()

    conn_str = f"host={args.host} port={args.port} dbname={args.dbname} user={args.user} password={args.password}"

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # List tables in the public schema
                cur.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                    """
                )
                tables = cur.fetchall()
                table_names = [t[0] for t in tables]
                if not table_names:
                    print("No tables found in public schema.")
                else:
                    print("Tables:", table_names)

                # Interactive menu
                while True:
                    print()
                    print("Menu:")
                    print("1. Show Table")
                    print("2. Update Table")
                    print("q. Quit")
                    choice = input("Choose an option: ").strip()

                    if choice == '1':
                        show_table(cur, table_names)

                    elif choice == '2':
                        update_table(cur, table_names)

                    elif choice.lower() in ('q', 'quit', 'exit'):
                        print("Goodbye!")
                        break

                    else:
                        print("Invalid choice, please try again.")

    except Exception as e:
        print("Error:", e)
        sys.exit(1)


if __name__ == "__main__":
    main()

