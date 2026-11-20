# Finanzas personales 💸

Aplicación CLI para registrar ingresos y gastos en SQLite, revisar balances por categoría y exportar movimientos.

## Uso

```bash
python finance.py add ingreso 2500000 salario --note "Pago mensual"
python finance.py add gasto 28000 alimentación --note "Almuerzo"
python finance.py summary
python finance.py list --type gasto --month 2026-11
python finance.py export movimientos.csv
```

El archivo `finanzas.db` se crea junto al programa. Usa COP en los ejemplos; las cantidades se guardan como enteros para evitar errores de redondeo.

## CV

> Desarrollé un gestor financiero en Python con persistencia SQLite, clasificación por categoría, filtros por periodo, resumen de balance y exportación de movimientos a CSV.

