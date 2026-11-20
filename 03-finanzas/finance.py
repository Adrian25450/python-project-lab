"""Personal finance ledger backed by SQLite."""
import argparse
import csv
from contextlib import contextmanager
import sqlite3
from datetime import date
from pathlib import Path

DB = Path(__file__).with_name("finanzas.db")

@contextmanager
def connect():
    db = sqlite3.connect(DB); db.row_factory = sqlite3.Row
    db.execute("""CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY, kind TEXT NOT NULL CHECK(kind IN ('ingreso','gasto')),
        amount INTEGER NOT NULL CHECK(amount > 0), category TEXT NOT NULL,
        note TEXT NOT NULL DEFAULT '', occurred_on TEXT NOT NULL)""")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser(description="Finanzas personales · registro local SQLite")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add"); add.add_argument("kind", choices=["ingreso", "gasto"]); add.add_argument("amount", type=int); add.add_argument("category"); add.add_argument("--note", default=""); add.add_argument("--date", default=date.today().isoformat())
    listing = commands.add_parser("list"); listing.add_argument("--type", choices=["ingreso", "gasto"]); listing.add_argument("--month")
    commands.add_parser("summary")
    export = commands.add_parser("export"); export.add_argument("file", type=Path)
    args = parser.parse_args()
    try:
        with connect() as db:
            if args.command == "add":
                if args.amount <= 0: parser.error("el monto debe ser mayor que cero")
                if not args.category.strip(): parser.error("la categoría no puede estar vacía")
                date.fromisoformat(args.date)
                cur = db.execute("INSERT INTO movements(kind,amount,category,note,occurred_on) VALUES(?,?,?,?,?)", (args.kind,args.amount,args.category.strip(),args.note,args.date))
                print(f"Movimiento #{cur.lastrowid} guardado · {args.kind} ${args.amount:,.0f} COP")
            elif args.command == "summary":
                totals = {row["kind"]: row["total"] or 0 for row in db.execute("SELECT kind,SUM(amount) total FROM movements GROUP BY kind")}
                income, expense = totals.get("ingreso",0), totals.get("gasto",0)
                print(f"Ingresos  ${income:,.0f} COP\nGastos    ${expense:,.0f} COP\nDisponible ${income-expense:,.0f} COP")
                for row in db.execute("SELECT category,SUM(amount) total FROM movements WHERE kind='gasto' GROUP BY category ORDER BY total DESC"):
                    print(f"  {row['category']}: ${row['total']:,.0f}")
            else:
                query, params = "SELECT * FROM movements WHERE 1=1", []
                if args.command == "list":
                    if args.type: query += " AND kind=?"; params.append(args.type)
                    if args.month: query += " AND substr(occurred_on,1,7)=?"; params.append(args.month)
                query += " ORDER BY occurred_on DESC,id DESC"
                rows = db.execute(query, params).fetchall()
                if args.command == "export":
                    with args.file.open("w", newline="", encoding="utf-8-sig") as stream:
                        writer=csv.writer(stream); writer.writerow(["id","tipo","monto_cop","categoria","nota","fecha"])
                        writer.writerows([tuple(row) for row in rows])
                    print(f"{len(rows)} movimientos exportados a {args.file}")
                else:
                    for row in rows: print(f"{row['occurred_on']} · {row['kind']:<7} · ${row['amount']:>12,.0f} · {row['category']} · {row['note']}")
                    if not rows: print("No hay movimientos para ese filtro.")
    except (OSError, ValueError) as error: parser.error(str(error))

if __name__ == "__main__": main()

