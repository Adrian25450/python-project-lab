# SmartCalc 🧮

Calculadora CLI con expresiones matemáticas, operaciones encadenadas, memoria en JSON y validación sin ejecutar código arbitrario.

## Uso

```bash
python main.py "(1250000 + 450000) * 0.19"
python main.py "sqrt(81) + abs(-4)"
python main.py --interactive
python main.py --history
```

Operadores: `+ - * / // % **`, paréntesis y funciones `sqrt`, `abs`, `round`. La sintaxis se procesa con AST y solo se aceptan nodos matemáticos permitidos.

## CV

> Implementé una calculadora CLI en Python con parser seguro de expresiones, operaciones encadenadas, control de errores e historial persistido en JSON.

