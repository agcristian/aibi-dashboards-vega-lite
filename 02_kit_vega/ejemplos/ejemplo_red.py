#!/usr/bin/env python3
"""Ejemplo de red por capas con foco por clic (layered_network). Corre en cualquier workspace: los datos van en VALUES.

  python example_network.py                     # escribe out/ejemplo_red.lvdash.json
  python ../scripts/preview.py out/ejemplo_red.lvdash.json --profile P --warehouse W
  python ../scripts/deploy.py out/ejemplo_red.lvdash.json --name "Ejemplo red" --profile P --warehouse W --parent /Users/<yo>/demo

Para linaje real cambia NODOS y ARISTAS por consultas a system.access.table_lineage (ver references/recipes.md).
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import aibi_kit as k  # noqa: E402
from aibi_kit import f  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
k.use_theme("flat", palette="corporate", locale="es")

# nodo, etiqueta, capa, orden_capa, info
NODOS = """SELECT * FROM VALUES
  ('crm', 'Extracto CRM', 'Origen', 0, 'Archivo diario'),
  ('erp', 'Extracto ERP', 'Origen', 0, 'Archivo diario'),
  ('b_cli', 'brz_clientes', 'Bronze', 1, 'STREAMING_TABLE'),
  ('b_ped', 'brz_pedidos', 'Bronze', 1, 'STREAMING_TABLE'),
  ('b_prod', 'brz_productos', 'Bronze', 1, 'STREAMING_TABLE'),
  ('s_cli', 'slv_clientes', 'Silver', 2, 'STREAMING_TABLE'),
  ('s_cli_h', 'slv_clientes_hist', 'Silver', 2.45, 'SCD2'),
  ('s_ped', 'slv_pedidos', 'Silver', 2, 'STREAMING_TABLE'),
  ('d_cli', 'dim_cliente', 'Gold', 3, 'MATERIALIZED_VIEW'),
  ('d_prod', 'dim_producto', 'Gold', 3, 'MATERIALIZED_VIEW'),
  ('f_ven', 'fct_ventas', 'Gold', 3.45, 'MATERIALIZED_VIEW'),
  ('mv', 'mv_ventas', 'Semántica', 4, 'METRIC_VIEW'),
  ('dash', 'Dashboard Ventas', 'Consumo', 5, 'DASHBOARD'),
  ('genie', 'Genie Ventas', 'Consumo', 5, 'GENIE_SPACE')
  AS t(nodo, etiqueta, capa, orden_capa, info)"""

# origen, destino, relacion, info
ARISTAS = """SELECT * FROM VALUES
  ('crm', 'b_cli', 'Ingesta', 'Auto Loader'), ('erp', 'b_ped', 'Ingesta', 'Auto Loader'),
  ('erp', 'b_prod', 'Ingesta', 'Auto Loader'),
  ('b_cli', 's_cli', 'Transformación', 'Pipeline'), ('s_cli', 's_cli_h', 'Transformación', 'AUTO CDC'),
  ('b_ped', 's_ped', 'Transformación', 'Pipeline'), ('s_cli_h', 'd_cli', 'Transformación', 'Pipeline'),
  ('b_prod', 'd_prod', 'Transformación', 'Pipeline'), ('s_ped', 'f_ven', 'Transformación', 'Pipeline'),
  ('d_cli', 'f_ven', 'Transformación', 'Pipeline'), ('d_prod', 'f_ven', 'Transformación', 'Pipeline'),
  ('f_ven', 'mv', 'Definición de vista', 'Metric view'), ('d_cli', 'mv', 'Definición de vista', 'Metric view'),
  ('d_prod', 'mv', 'Definición de vista', 'Metric view'), ('mv', 'dash', 'Consumo', 'AI/BI'),
  ('mv', 'genie', 'Consumo', 'Genie')
  AS t(origen, destino, relacion, info)"""

ds = k.dataset("ds_red", "Red de linaje", k.network_sql(NODOS, ARISTAS))
red = k.vega("w_red", "ds_red", [f(c) for c in k.NETWORK_FIELDS],
             k.layered_network("Linaje de la capa de ventas",
                               "Clic en un objeto para ver solo sus relaciones directas · clic en el fondo para ver todo",
                               kinds=["Ingesta", "Transformación", "Definición de vista", "Consumo"],
                               colors=["#8A9BA8", "#1B3139", "#00A972", "#FF3621"]),
             disaggregated=True)

g = k.Grid(margin=0)
g.row(14, (red, 12))
os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
k.save(k.dashboard([ds], [k.page("red", "Linaje", g.items)]), os.path.join(HERE, "out", "ejemplo_red.lvdash.json"))
