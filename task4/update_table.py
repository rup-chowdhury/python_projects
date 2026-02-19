from psycopg import sql


def _print_rows_with_header(cur, rows):
    if cur.description:
        cols = [d[0] for d in cur.description]
        print(" | ".join(cols))
        print('-' * max(10, len(" | ".join(cols))))
    for r in rows:
        print(r)


def update_table(cur, table_names):
    tbl = input("Enter table name: ").strip()
    lookup = {name.lower(): name for name in table_names}
    if tbl.lower() not in lookup:
        print("Table not found in the database")
        return

    real_name = lookup[tbl.lower()]
    q = sql.SQL("SELECT ctid, * FROM {} LIMIT 100;").format(sql.Identifier(real_name))
    cur.execute(q)
    rows = cur.fetchall()
    if not rows:
        print(f"Table '{real_name}' is empty.")
        return

    desc = [d[0] for d in cur.description]
    for idx, row in enumerate(rows, start=1):
        preview = row[1:6]
        print(f"{idx}. {preview}")

    sel = input("Enter row number to update (or 'c' to cancel): ").strip()
    if sel.lower() in ('c', 'cancel'):
        print("Cancelled update.")
        return

    try:
        sel_idx = int(sel)
    except ValueError:
        print("Invalid row number.")
        return
    if not (1 <= sel_idx <= len(rows)):
        print("Row number out of range.")
        return

    chosen = rows[sel_idx - 1]

    cur.execute(
        """
        SELECT kcu.column_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema = kcu.table_schema
        WHERE tc.constraint_type = 'PRIMARY KEY'
          AND tc.table_name = %s
          AND tc.table_schema = 'public'
        ORDER BY kcu.ordinal_position;
        """,
        (real_name,)
    )
    pk_cols = [r[0] for r in cur.fetchall()]

    col_names = desc[1:]
    values = list(chosen[1:])

    where_clause = None
    where_params = None
    if pk_cols:
        pk_idx_map = {name: i for i, name in enumerate(col_names)}
        missing_pk = False
        pk_values = []
        pk_identifiers = []
        for pk in pk_cols:
            if pk in pk_idx_map:
                pk_values.append(values[pk_idx_map[pk]])
                pk_identifiers.append(sql.Identifier(pk))
            else:
                missing_pk = True
                break
        if not missing_pk:
            where_clause = sql.SQL(' AND ').join(
                sql.SQL('{} = %s').format(ident) for ident in pk_identifiers
            )
            where_params = pk_values

    if where_clause is None:
        ctid_val = chosen[0]
        where_clause = sql.SQL('ctid = %s')
        where_params = [ctid_val]

    to_update = []
    update_params = []
    print("Enter new value for each column; empty to keep current, type NULL to set NULL")
    for i, col in enumerate(col_names):
        if pk_cols and col in pk_cols:
            print(f"{col} (PRIMARY KEY) = {values[i]} (skipped)")
            continue
        cur_val = values[i]
        new = input(f"{col} [{cur_val}]: ").strip()
        if new == '':
            continue
        elif new.upper() == 'NULL':
            to_update.append(col)
            update_params.append(None)
        else:
            to_update.append(col)
            update_params.append(new)

    if not to_update:
        print("No changes provided.")
        return

    set_clause = sql.SQL(', ').join(
        sql.SQL('{} = %s').format(sql.Identifier(c)) for c in to_update
    )
    update_query = sql.SQL('UPDATE {} SET {} WHERE {}').format(
        sql.Identifier(real_name),
        set_clause,
        where_clause
    )

    params = update_params + (where_params if where_params else [])
    cur.execute(update_query, params)
    print(f"Updated {cur.rowcount} row(s).")

    select_q = sql.SQL('SELECT * FROM {} WHERE {}').format(sql.Identifier(real_name), where_clause)
    cur.execute(select_q, where_params)
    updated_rows = cur.fetchall()
    if updated_rows:
        _print_rows_with_header(cur, updated_rows)
    else:
        print("Unable to fetch updated row.")

