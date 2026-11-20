# FileFlow 🗂️

Organizador por tipo y fecha con vista previa como comportamiento inicial, control de colisiones y reporte CSV. Solo copia al aplicar: nunca elimina archivos originales.

## Uso

```bash
python organize.py "C:/Users/usuario/Descargas" --output "C:/Users/usuario/Ordenados"
python organize.py ./entrada --output ./salida --apply --report ./salida/reporte.csv
```

El primer comando imprime el plan sin modificar archivos. `--apply` copia y conserva metadatos; nombres repetidos reciben sufijos. Revisa cuidadosamente las rutas antes de activar la copia.

## CV

> Automaticé la clasificación de archivos con Python, vista previa de cambios, prevención de sobrescritura y generación de reportes CSV, conservando los originales.

