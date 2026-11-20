"""Inventory REST API with stock movement audit trail."""
from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

app=Flask(__name__)
DB=Path(__file__).with_name("inventario.db")

def connect():
    db=sqlite3.connect(DB); db.row_factory=sqlite3.Row
    db.executescript("""CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY,sku TEXT UNIQUE NOT NULL,name TEXT NOT NULL,category TEXT NOT NULL,
      quantity INTEGER NOT NULL DEFAULT 0 CHECK(quantity>=0),min_stock INTEGER NOT NULL DEFAULT 0 CHECK(min_stock>=0),
      unit_price INTEGER NOT NULL DEFAULT 0 CHECK(unit_price>=0),active INTEGER NOT NULL DEFAULT 1);
      CREATE TABLE IF NOT EXISTS movements(
      id INTEGER PRIMARY KEY,product_id INTEGER NOT NULL REFERENCES products(id),kind TEXT NOT NULL,
      quantity INTEGER NOT NULL CHECK(quantity>0),note TEXT NOT NULL DEFAULT '',created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);""")
    db.commit(); return db

def body_fields(data, create=False):
    if not isinstance(data,dict): raise ValueError("El cuerpo debe ser un objeto JSON")
    fields={}
    for key in ("sku","name","category"):
        if key in data or create:
            value=data.get(key)
            if not isinstance(value,str) or not value.strip(): raise ValueError(f"{key} es obligatorio")
            fields[key]=value.strip()[:100]
    for key in ("quantity","min_stock","unit_price"):
        if key in data or create:
            value=data.get(key,0)
            if not isinstance(value,int) or isinstance(value,bool) or value<0: raise ValueError(f"{key} debe ser un entero no negativo")
            fields[key]=value
    return fields

@app.errorhandler(ValueError)
def invalid(error): return jsonify(error=str(error)),400

@app.get("/api/health")
def health(): return jsonify(status="ok",service="Inventario API")

@app.get("/api/products")
def products():
    q=request.args.get("q","").strip(); low=request.args.get("low_stock")=="1"
    sql="SELECT * FROM products WHERE active=1"; params=[]
    if q: sql+=" AND (sku LIKE ? OR name LIKE ? OR category LIKE ?)"; params += [f"%{q}%"]*3
    if low: sql+=" AND quantity<=min_stock"
    sql+=" ORDER BY name LIMIT 500"
    with connect() as db: rows=db.execute(sql,params).fetchall()
    return jsonify(items=[dict(row) for row in rows],count=len(rows))

@app.post("/api/products")
def create_product():
    fields=body_fields(request.get_json(silent=True),True)
    with connect() as db:
        cur=db.execute("INSERT INTO products(sku,name,category,quantity,min_stock,unit_price) VALUES(:sku,:name,:category,:quantity,:min_stock,:unit_price)",fields)
        product=dict(db.execute("SELECT * FROM products WHERE id=?",(cur.lastrowid,)).fetchone())
    return jsonify(product),201

@app.patch("/api/products/<int:product_id>")
def update_product(product_id):
    fields=body_fields(request.get_json(silent=True))
    if not fields: return jsonify(error="No hay campos para actualizar"),400
    with connect() as db:
        if not db.execute("SELECT id FROM products WHERE id=? AND active=1",(product_id,)).fetchone(): return jsonify(error="Producto no encontrado"),404
        assignments=", ".join(f"{key}=?" for key in fields)
        db.execute(f"UPDATE products SET {assignments} WHERE id=?",[*fields.values(),product_id])
        product=dict(db.execute("SELECT * FROM products WHERE id=?",(product_id,)).fetchone())
    return jsonify(product)

@app.delete("/api/products/<int:product_id>")
def archive_product(product_id):
    with connect() as db:
        cur=db.execute("UPDATE products SET active=0 WHERE id=? AND active=1",(product_id,))
        if not cur.rowcount: return jsonify(error="Producto no encontrado"),404
    return "",204

@app.post("/api/products/<int:product_id>/movements")
def movement(product_id):
    data=request.get_json(silent=True) or {}; kind=data.get("kind"); qty=data.get("quantity")
    if kind not in {"in","out"}: return jsonify(error="kind debe ser in u out"),400
    if not isinstance(qty,int) or isinstance(qty,bool) or qty<=0: return jsonify(error="quantity debe ser un entero positivo"),400
    with connect() as db:
        product=db.execute("SELECT * FROM products WHERE id=? AND active=1",(product_id,)).fetchone()
        if not product: return jsonify(error="Producto no encontrado"),404
        next_qty=product["quantity"]+qty if kind=="in" else product["quantity"]-qty
        if next_qty<0: return jsonify(error="La salida supera las existencias disponibles"),409
        db.execute("UPDATE products SET quantity=? WHERE id=?",(next_qty,product_id))
        cur=db.execute("INSERT INTO movements(product_id,kind,quantity,note) VALUES(?,?,?,?)",(product_id,kind,qty,str(data.get("note",""))[:200]))
        row=dict(db.execute("SELECT m.*,p.sku,p.name FROM movements m JOIN products p ON p.id=m.product_id WHERE m.id=?",(cur.lastrowid,)).fetchone())
    return jsonify(row),201

@app.get("/api/movements")
def movements():
    with connect() as db: rows=db.execute("SELECT m.*,p.sku,p.name FROM movements m JOIN products p ON p.id=m.product_id ORDER BY m.id DESC LIMIT 200").fetchall()
    return jsonify(items=[dict(row) for row in rows])

@app.get("/api/summary")
def summary():
    with connect() as db:
        row=db.execute("SELECT COUNT(*) products,COALESCE(SUM(quantity),0) units,COALESCE(SUM(quantity*unit_price),0) inventory_value,SUM(CASE WHEN quantity<=min_stock THEN 1 ELSE 0 END) low_stock FROM products WHERE active=1").fetchone()
    return jsonify(dict(row))

