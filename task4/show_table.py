import sys
from psycopg import sql


def _print_rows_with_header(cur, rows):
    if cur.description:
        cols = [d[0] for d in cur.description]
        print(" | ".join(cols))
        print('-' * max(10, len(" | ".join(cols))))
    for r in rows:
        print(r)


def show_table(cur, table_names):
    tbl = input("Enter table name: ").strip()
    lookup = {name.lower(): name for name in table_names}
    if tbl.lower() in lookup:
        real_name = lookup[tbl.lower()]
        query = sql.SQL("SELECT * FROM {} LIMIT 50;").format(sql.Identifier(real_name))
        cur.execute(query)
        rows = cur.fetchall()
        if not rows:
            print(f"Table '{real_name}' is empty.")
        else:
            _print_rows_with_header(cur, rows)
    else:
        print("Table not found in the database")

