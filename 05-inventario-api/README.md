# Inventario API 📦

API REST para catálogo de productos con búsqueda, alertas de stock bajo y registro de entradas/salidas. Flask expone endpoints; SQLite conserva los datos localmente.

## Inicio

```bash
pip install -r requirements.txt
flask --app app run --debug
```

La base `inventario.db` se crea localmente. Endpoint base: `http://127.0.0.1:5000/api`.

```bash
curl http://127.0.0.1:5000/api/products
curl -X POST http://127.0.0.1:5000/api/products -H "Content-Type: application/json" -d '{"sku":"MOU-01","name":"Mouse inalámbrico","category":"Periféricos","quantity":8,"min_stock":3,"unit_price":76000}'
curl -X POST http://127.0.0.1:5000/api/products/1/movements -H "Content-Type: application/json" -d '{"kind":"out","quantity":2,"note":"Entrega"}'
```

## Endpoints

`GET /api/products?q=&low_stock=1`, `POST /api/products`, `PATCH /api/products/<id>`, `DELETE /api/products/<id>`, `POST /api/products/<id>/movements`, `GET /api/movements`, `GET /api/summary`.

## CV

> Diseñé una API REST de inventario con Flask y SQLite, con validación de entradas, búsqueda, alertas de stock mínimo y trazabilidad de movimientos de entrada/salida.

