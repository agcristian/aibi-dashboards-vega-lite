#!/usr/bin/env python3
"""Simplifica un GeoJSON de polígonos (estados, provincias, regiones) para embeberlo en un spec Vega-Lite
(custom-vega-viz no permite data.url). Douglas-Peucker + redondeo de coordenadas; descarta islas pequeñas.

Uso: python -I simplify_geo.py entrada.geojson salida.json [--eps 0.045] [--min-area 0.03] [--prop name] [--decimals 2]
Objetivo: < ~40 KB por mapa. Sube --eps si sigue pesado; bájalo si las formas se deforman.
Corre con -I si el GeoJSON viene de internet (archivo no confiable)."""
import argparse, json, math, sys
sys.setrecursionlimit(10000)


def dp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dmax, idx = 0, 0
    for i in range(1, len(pts) - 1):
        x0, y0 = pts[i]
        num = abs((y2 - y1) * x0 - (x2 - x1) * y0 + x2 * y1 - y2 * x1)
        d = num / (math.hypot(y2 - y1, x2 - x1) or 1e-12)
        if d > dmax:
            dmax, idx = d, i
    if dmax > eps:
        return dp(pts[:idx + 1], eps)[:-1] + dp(pts[idx:], eps)
    return [pts[0], pts[-1]]


def area(r):
    return abs(sum(r[i][0] * r[i - 1][1] - r[i - 1][0] * r[i][1] for i in range(len(r)))) / 2


ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("dst")
ap.add_argument("--eps", type=float, default=0.045)
ap.add_argument("--min-area", type=float, default=0.03)
ap.add_argument("--prop", default="name")
ap.add_argument("--decimals", type=int, default=2)
a = ap.parse_args()
src = json.load(open(a.src, encoding="utf-8"))
out = []
for ft in src["features"]:
    g = ft["geometry"]
    if g is None:
        continue
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    keep = []
    for poly in polys:
        outer = poly[0]
        if area(outer) < a.min_area:
            continue
        # anillo cerrado: se parte en dos mitades (DP con extremos iguales colapsa a 2 puntos)
        h = len(outer) // 2
        s = dp(outer[:h + 1], a.eps)[:-1] + dp(outer[h:], a.eps)
        s = [[round(x, a.decimals), round(y, a.decimals)] for x, y in s]
        if len(s) >= 4:
            keep.append([s])
    if keep:
        out.append({"type": "Feature", "properties": {a.prop: ft["properties"].get(a.prop)},
                    "geometry": {"type": "MultiPolygon", "coordinates": keep}})
json.dump({"type": "FeatureCollection", "features": out}, open(a.dst, "w", encoding="utf-8"), separators=(",", ":"), ensure_ascii=False)
import os
print(len(out), "features,", sum(len(r[0]) for x in out for r in x["geometry"]["coordinates"]), "puntos,",
      round(os.path.getsize(a.dst) / 1024, 1), "KB")
