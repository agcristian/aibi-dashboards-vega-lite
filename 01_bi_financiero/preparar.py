#!/usr/bin/env python3
"""Genera copias del SQL y del tablero con su catálogo y esquema.

Uso:  python preparar.py --catalog mi_catalogo --schema bi_financiero_vega_demo
Salida: setup_datos_listo.sql y bi_financiero_listo.lvdash.json en esta carpeta.
"""
import argparse, json, os

aqui = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--catalog", required=True)
ap.add_argument("--schema", required=True)
a = ap.parse_args()

sql = open(os.path.join(aqui, "setup_datos.sql"), encoding="utf-8").read()
sql = sql.replace("TU_CATALOGO.TU_ESQUEMA", f"{a.catalog}.{a.schema}")
open(os.path.join(aqui, "setup_datos_listo.sql"), "w", encoding="utf-8").write(sql)

d = json.load(open(os.path.join(aqui, "bi_financiero.lvdash.json"), encoding="utf-8"))
for ds in d.get("datasets", []):
    if ds.get("catalog") == "TU_CATALOGO":
        ds["catalog"] = a.catalog
    if ds.get("schema") == "TU_ESQUEMA":
        ds["schema"] = a.schema
json.dump(d, open(os.path.join(aqui, "bi_financiero_listo.lvdash.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("Listo: setup_datos_listo.sql y bi_financiero_listo.lvdash.json")
