#!/usr/bin/env python3
"""Ejecuta SQL en un SQL warehouse vía /api/2.0/sql/statements (CLI de Databricks autenticado).

Uso:
  python run_sql.py --profile P --warehouse W archivo.sql      # sentencias separadas por líneas ';;'
  python run_sql.py --profile P --warehouse W -e "SELECT 1"
  (o variables de entorno AIBI_PROFILE / AIBI_WAREHOUSE)
"""
import argparse, json, os, subprocess, sys, time


def api(profile, method, path, body=None):
    cmd = ["databricks", "api", method, path, "--profile", profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    out = subprocess.run(cmd, capture_output=True, text=True)
    if out.returncode:
        raise RuntimeError(out.stderr or out.stdout)
    return json.loads(out.stdout or "{}")


def run(stmt, profile, warehouse, catalog=None, schema=None):
    body = {"statement": stmt, "warehouse_id": warehouse, "wait_timeout": "50s", "on_wait_timeout": "CONTINUE"}
    if catalog:
        body["catalog"] = catalog
    if schema:
        body["schema"] = schema
    r = api(profile, "post", "/api/2.0/sql/statements", body)
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(3)
        r = api(profile, "get", "/api/2.0/sql/statements/" + r["statement_id"])
    if r["status"]["state"] != "SUCCEEDED":
        raise RuntimeError(f"{r['status']['state']}: {r['status'].get('error', {}).get('message')}\n--- {stmt[:300]}")
    cols = [c["name"] for c in r.get("manifest", {}).get("schema", {}).get("columns", [])]
    return cols, r.get("result", {}).get("data_array", []) or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file", nargs="?")
    ap.add_argument("-e", "--execute")
    ap.add_argument("--profile", default=os.environ.get("AIBI_PROFILE", "DEFAULT"))
    ap.add_argument("--warehouse", default=os.environ.get("AIBI_WAREHOUSE"))
    ap.add_argument("--catalog")
    ap.add_argument("--schema")
    a = ap.parse_args()
    if not a.warehouse:
        sys.exit("Falta --warehouse (o AIBI_WAREHOUSE)")
    stmts = [a.execute] if a.execute else [s.strip() for s in open(a.file).read().split("\n;;\n") if s.strip()]
    for s in stmts:
        t = time.time()
        cols, rows = run(s, a.profile, a.warehouse, a.catalog, a.schema)
        print(f"OK ({time.time() - t:.1f}s) {s.splitlines()[0][:90]}")
        if cols and rows:
            print("  ", cols)
            for row in rows[:20]:
                print("  ", row)


if __name__ == "__main__":
    main()
