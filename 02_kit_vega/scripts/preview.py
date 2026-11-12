#!/usr/bin/env python3
"""Preview local de un .lvdash.json: corre la query de cada widget Vega contra el warehouse (aplicando los valores
por defecto de parámetros y filtros), compila los specs con vega/vega-lite en node y arma un PNG por página con
la rejilla real. Detecta specs que no compilan, gráficas encogidas, etiquetas cortadas y leyendas que desbordan.

Uso: python preview.py out/tablero.lvdash.json [pagina ...] --profile P --warehouse W
     (o AIBI_PROFILE / AIBI_WAREHOUSE). Salida: <dir del json>/preview/<pagina>.png
     --offline: sin warehouse, solo compila cada spec (errores de esquema de Vega-Lite).
Requiere node y Google Chrome; instala vega y vega-lite en ~/.cache/aibi-vega-preview la primera vez.
Caché de resultados SQL en ~/.cache/aibi-vega-preview/sql (bórrala si cambian los datos)."""
import argparse, hashlib, json, os, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

COL_PX, ROW_PX, GUT = 118, 42, 8
NODE_DIR = os.path.expanduser("~/.cache/aibi-vega-preview")
CACHE = os.path.join(NODE_DIR, "sql")
HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "google-chrome", "chromium", "chromium-browser"]


def api(profile, method, path, body=None):
    cmd = ["databricks", "api", method, path, "--profile", profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(out.stderr or out.stdout)
    return json.loads(out.stdout or "{}")


def ensure_node():
    os.makedirs(CACHE, exist_ok=True)
    if not os.path.isdir(os.path.join(NODE_DIR, "node_modules", "vega-lite")):
        print("Instalando vega y vega-lite en", NODE_DIR)
        if not os.path.exists(os.path.join(NODE_DIR, "package.json")):
            json.dump({"name": "aibi-vega-preview", "private": True, "type": "module"}, open(os.path.join(NODE_DIR, "package.json"), "w"))
        subprocess.run(["npm", "install", "--silent", "vega", "vega-lite"], cwd=NODE_DIR, check=True)
    shutil.copy(os.path.join(HERE, "render_page.mjs"), NODE_DIR)


def sql_rows(a, stmt, catalog, schema):
    key = hashlib.md5((stmt + str(catalog) + str(schema)).encode()).hexdigest()
    cp = os.path.join(CACHE, key + ".json")
    if os.path.exists(cp):
        return json.load(open(cp))
    body = {"statement": stmt, "warehouse_id": a.warehouse, "wait_timeout": "50s", "on_wait_timeout": "CONTINUE",
            "disposition": "INLINE", "format": "JSON_ARRAY"}
    if catalog:
        body["catalog"] = catalog
    if schema:
        body["schema"] = schema
    r = api(a.profile, "post", "/api/2.0/sql/statements", body)
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        r = api(a.profile, "get", "/api/2.0/sql/statements/" + r["statement_id"])
    if r["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(r["status"].get("error", {}).get("message", "")[:600] + "\n" + stmt[:400])
    cols = r["manifest"]["schema"]["columns"]
    data = list(r.get("result", {}).get("data_array", []) or [])
    nxt = r.get("result", {}).get("next_chunk_internal_link")
    while nxt:
        c = api(a.profile, "get", nxt)
        data += c.get("data_array", []) or []
        nxt = c.get("next_chunk_internal_link")
    num = {"INT", "LONG", "DOUBLE", "DECIMAL", "FLOAT", "SHORT", "BYTE", "BIGINT"}
    rows = [{c["name"]: (float(v) if v is not None and c["type_name"] in num else v) for c, v in zip(cols, row)} for row in data]
    json.dump(rows, open(cp, "w"))
    return rows


def widget_sql(w, datasets, page_filters):
    """Reproduce lo que hace el visor: SELECT campos FROM (dataset con parámetros por defecto) WHERE filtros GROUP BY."""
    q = w["queries"][0]["query"]
    ds = datasets[q["datasetName"]]
    base = "".join(ds["queryLines"])
    for p in ds.get("parameters", []):
        if p.get("complexType") == "RANGE":
            r = p["defaultSelection"]["range"]
            base = base.replace(":" + p["keyword"] + ".min", f"DATE'{r['min']['value']}'")
            base = base.replace(":" + p["keyword"] + ".max", f"DATE'{r['max']['value']}'")
            continue
        v = p["defaultSelection"]["values"]["values"][0]["value"]
        base = base.replace(":" + p["keyword"], "'" + v.replace("'", "''") + "'")
    sel = ", ".join(f"{x['expression']} AS `{x['name']}`" for x in q["fields"])
    where = [x["expression"] for x in q.get("filters", [])]
    for field, vals in page_filters.get(q["datasetName"], {}).items():
        where.append(f"`{field}` IN ({', '.join(repr(v) for v in vals)})")
    s = f"SELECT {sel} FROM ({base}) t"
    if where:
        s += " WHERE " + " AND ".join(where)
    if not q.get("disaggregated", False):
        grp = [x["expression"] for x in q["fields"] if "(" not in x["expression"]]
        if grp:
            s += " GROUP BY " + ", ".join(grp)
    return s + " LIMIT 60000", ds.get("catalog"), ds.get("schema")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("pages", nargs="*")
    ap.add_argument("--profile", default=os.environ.get("AIBI_PROFILE", "DEFAULT"))
    ap.add_argument("--warehouse", default=os.environ.get("AIBI_WAREHOUSE"))
    ap.add_argument("--offline", action="store_true", help="no consulta el warehouse: solo valida que cada spec compile")
    a = ap.parse_args()
    if not a.warehouse and not a.offline:
        sys.exit("Falta --warehouse (o AIBI_WAREHOUSE), o usa --offline")
    ensure_node()
    d = json.load(open(a.path))
    datasets = {x["name"]: x for x in d["datasets"]}
    outdir = os.path.join(os.path.dirname(os.path.abspath(a.path)), "preview")
    os.makedirs(outdir, exist_ok=True)
    th = d.get("uiSettings", {}).get("theme", {})
    env = dict(os.environ, CANVAS=th.get("canvasBackgroundColor", {}).get("light", "#FFFFFF"),
               CARD=th.get("widgetBackgroundColor", {}).get("light", "#FFFFFF"), RADIUS=str(th.get("widgetCornerRadius", 0)))
    chrome = next((c for c in CHROME if shutil.which(c) or os.path.exists(c)), None)
    for pg in d["pages"]:
        if a.pages and pg["name"] not in a.pages:
            continue
        pf = {}
        for it in pg["layout"]:
            sp = it["widget"].get("spec", {})
            if sp.get("widgetType", "").startswith("filter") and "selection" in sp:
                vals = [v["value"] for v in sp["selection"]["defaultSelection"]["values"]["values"]]
                for q, e in zip(it["widget"]["queries"], sp["encodings"]["fields"]):
                    pf.setdefault(q["query"]["datasetName"], {})[e["fieldName"]] = vals
        jobs = [(it, *widget_sql(it["widget"], datasets, pf)) for it in pg["layout"]
                if it["widget"].get("spec", {}).get("widgetType") == "custom-vega-viz"]

        def fetch(j):
            it, s, c, sc = j
            if a.offline:
                return it["widget"]["name"], [], None
            try:
                return it["widget"]["name"], sql_rows(a, s, c, sc), None
            except Exception as e:  # noqa: BLE001
                return it["widget"]["name"], [], str(e)
        with ThreadPoolExecutor(6) as ex:
            res = {n: (rows, err) for n, rows, err in ex.map(fetch, jobs)}
        items = []
        for it in pg["layout"]:
            w, p = it["widget"], it["position"]
            sp = w.get("spec", {})
            item = {"name": w["name"], "x": p["x"] * COL_PX, "y": p["y"] * ROW_PX,
                    "w": p["width"] * COL_PX - GUT, "h": p["height"] * ROW_PX - GUT}
            if sp.get("widgetType") == "custom-vega-viz":
                rows, err = res[w["name"]]
                item.update({"type": "vega", "spec": json.loads(sp["jsonSpec"]["spec"]), "rows": rows, "err": err})
                if not err and not rows and not a.offline:
                    print("AVISO sin filas:", w["name"])
            elif "multilineTextboxSpec" in w:
                item.update({"type": "text", "text": "".join(w["multilineTextboxSpec"]["lines"])})
            else:
                item.update({"type": "native", "wt": sp.get("widgetType"), "title": sp.get("frame", {}).get("title", "")})
            items.append(item)
        jf = os.path.join(outdir, f"{pg['name']}.items.json")
        json.dump(items, open(jf, "w"))
        html = os.path.join(outdir, f"{pg['name']}.html")
        r = subprocess.run(["node", os.path.join(NODE_DIR, "render_page.mjs"), jf, html],
                           capture_output=True, text=True, cwd=NODE_DIR, env=env)
        print(pg["name"], r.stdout.strip(), r.stderr.strip()[:2000])
        if chrome:
            hmax = max(i["y"] + i["h"] for i in items) + 40
            png = os.path.join(outdir, f"{pg['name']}.png")
            subprocess.run([chrome, "--headless=new", "--disable-gpu", "--hide-scrollbars",
                            f"--window-size={12 * COL_PX + 40},{hmax}", f"--screenshot={png}", "file://" + html], capture_output=True)
            print("PNG", png)
        else:
            print("HTML", html, "(sin Chrome para screenshot)")


if __name__ == "__main__":
    main()
