#!/usr/bin/env python3
"""Crea o actualiza un dashboard AI/BI (Lakeview) desde un .lvdash.json y lo publica.

Uso:
  python deploy.py out/tablero.lvdash.json --name "Nombre visible" --profile P --warehouse W \
                   --parent /Users/<usuario>/carpeta [--no-publish] [--own-credentials]

Guarda el id en <dir del json>/ids.json (llave = nombre del archivo). Si ya existe, antes de actualizar baja un
snapshot de la versión viva a <dir>/snapshots/ (para poder regresar). El nombre visible no admite '/'."""
import argparse, json, os, subprocess, sys, time


def api(profile, method, path, body=None):
    cmd = ["databricks", "api", method, path, "--profile", profile]
    if body is not None:
        cmd += ["--json", json.dumps(body)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr or r.stdout)
    return json.loads(r.stdout or "{}")


def host(profile):
    r = subprocess.run(["databricks", "auth", "env", "--profile", profile], capture_output=True, text=True)
    try:
        return json.loads(r.stdout)["env"]["DATABRICKS_HOST"].rstrip("/")
    except Exception:  # noqa: BLE001
        return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--name", required=True)
    ap.add_argument("--profile", default=os.environ.get("AIBI_PROFILE", "DEFAULT"))
    ap.add_argument("--warehouse", default=os.environ.get("AIBI_WAREHOUSE"))
    ap.add_argument("--parent", default=os.environ.get("AIBI_PARENT"))
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--own-credentials", action="store_true", help="publicar sin embed_credentials (cada visor usa los suyos)")
    a = ap.parse_args()
    if not a.warehouse:
        sys.exit("Falta --warehouse (o AIBI_WAREHOUSE)")
    if "/" in a.name:
        sys.exit("El nombre visible no puede llevar '/'")
    ser = open(a.path, encoding="utf-8").read()
    base = os.path.dirname(os.path.abspath(a.path))
    ids_path = os.path.join(base, "ids.json")
    ids = json.load(open(ids_path)) if os.path.exists(ids_path) else {}
    key = os.path.basename(a.path)
    if key in ids:
        did = ids[key]
        live = api(a.profile, "get", f"/api/2.0/lakeview/dashboards/{did}")
        os.makedirs(os.path.join(base, "snapshots"), exist_ok=True)
        snap = os.path.join(base, "snapshots", f"{key}.{time.strftime('%Y%m%d_%H%M%S')}.json")
        json.dump(live, open(snap, "w"), ensure_ascii=False)
        api(a.profile, "patch", f"/api/2.0/lakeview/dashboards/{did}",
            {"display_name": a.name, "warehouse_id": a.warehouse, "serialized_dashboard": ser})
        print("UPDATED", did, "snapshot:", snap)
    else:
        if not a.parent:
            sys.exit("Falta --parent (carpeta del workspace) para crear el dashboard")
        subprocess.run(["databricks", "workspace", "mkdirs", a.parent, "--profile", a.profile], capture_output=True)
        r = api(a.profile, "post", "/api/2.0/lakeview/dashboards",
                {"display_name": a.name, "warehouse_id": a.warehouse, "parent_path": a.parent, "serialized_dashboard": ser})
        did = r["dashboard_id"]
        ids[key] = did
        json.dump(ids, open(ids_path, "w"), indent=1)
        print("CREATED", did)
    h = host(a.profile)
    if not a.no_publish:
        api(a.profile, "post", f"/api/2.0/lakeview/dashboards/{did}/published",
            {"warehouse_id": a.warehouse, "embed_credentials": not a.own_credentials})
        print("PUBLISHED")
        print(f"{h}/dashboardsv3/{did}/published")
    print(f"Borrador: {h}/dashboardsv3/{did}")


if __name__ == "__main__":
    main()
