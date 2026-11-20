"""CSV sales analytics with chart exports."""
import argparse
import csv
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
import matplotlib.pyplot as plt

FIELDS = {"fecha", "producto", "categoria", "cantidad", "precio_unitario"}

def load_rows(csv_path):
    with csv_path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = FIELDS - set(reader.fieldnames or [])
        if missing: raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing))}")
        rows = []
        for line, row in enumerate(reader, 2):
            try:
                day = date.fromisoformat(row["fecha"])
                qty, price = int(row["cantidad"]), float(row["precio_unitario"])
                if qty < 0 or price < 0: raise ValueError("valores negativos")
                rows.append({**row, "fecha_obj": day, "cantidad_num": qty, "precio_num": price, "ingreso": qty * price})
            except (ValueError, TypeError) as error: raise ValueError(f"Fila {line}: {error}") from error
    if not rows: raise ValueError("El CSV no contiene ventas")
    return rows

def build_report(rows, output):
    output.mkdir(parents=True, exist_ok=True)
    by_month, by_category = defaultdict(float), defaultdict(float)
    units_by_product = defaultdict(int)
    for row in rows:
        by_month[row["fecha_obj"].strftime("%Y-%m")] += row["ingreso"]
        by_category[row["categoria"]] += row["ingreso"]
        units_by_product[row["producto"]] += row["cantidad_num"]
    report = {"registros": len(rows), "ventas_totales": round(sum(r["ingreso"] for r in rows), 2),
              "unidades": sum(r["cantidad_num"] for r in rows), "mejor_producto_por_unidades": max(units_by_product, key=units_by_product.get),
              "ventas_por_mes": dict(sorted(by_month.items())), "ventas_por_categoria": dict(sorted(by_category.items()))}
    (output / "resumen.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for title, values, filename, color in [("Ventas por mes", report["ventas_por_mes"], "ventas_por_mes.png", "#187c83"),
                                           ("Ventas por categoría", report["ventas_por_categoria"], "ventas_por_categoria.png", "#2563eb")]:
        fig, ax = plt.subplots(figsize=(9, 4.8)); labels, amounts = list(values), list(values.values())
        ax.bar(labels, amounts, color=color, width=.62); ax.set_title(title, loc="left", fontweight="bold")
        ax.set_ylabel("Ingresos (COP)"); ax.grid(axis="y", alpha=.2); ax.set_axisbelow(True)
        ax.tick_params(axis="x", rotation=20); fig.tight_layout(); fig.savefig(output / filename, dpi=160); plt.close(fig)
    return report

def main():
    parser = argparse.ArgumentParser(description="Analiza ventas CSV y exporta gráficas")
    parser.add_argument("csv", type=Path); parser.add_argument("--output", type=Path, default=Path("reportes")); args = parser.parse_args()
    try:
        report = build_report(load_rows(args.csv), args.output)
        print(f"Ventas: ${report['ventas_totales']:,.0f} COP · Unidades: {report['unidades']} · Producto líder: {report['mejor_producto_por_unidades']}")
        print(f"Reportes guardados en {args.output.resolve()}")
    except (OSError, ValueError) as error: parser.error(str(error))

if __name__ == "__main__": main()

