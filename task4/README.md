Usage
-----

Run interactively:

```powershell
python main.py --host localhost --port 5432 --dbname shop_system --user postgres --password ""
```

In PowerShell you can simulate interactive input by using a here-string or piping Get-Content, for example:

```powershell
@"
1
NonExistingTable
q
"@ | python main.py

# or with a file
Get-Content -Raw input.txt | python main.py
```

Option 1 (Show Table) - Prompts for a table name. If the table exists it prints up to 50 rows. If not, it prints exactly:

Table not found in the database

Option 2 - Reserved for future implementation.
