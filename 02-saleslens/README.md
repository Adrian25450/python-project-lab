# SalesLens 📊

Analizador de ventas desde CSV. Calcula ingresos y unidades, compara categorías y meses y genera gráficas listas para informe.

## Uso

```bash
pip install -r requirements.txt
python analyze.py data/ventas_demo.csv --output reportes
```

Genera `resumen.json`, `ventas_por_mes.png` y `ventas_por_categoria.png`. Acepta CSV UTF-8 con las columnas `fecha,producto,categoria,cantidad,precio_unitario`.

## CV

> Construí un analizador de ventas en Python que procesa archivos CSV, calcula indicadores por periodo y categoría y exporta gráficas y resúmenes para apoyar decisiones.

