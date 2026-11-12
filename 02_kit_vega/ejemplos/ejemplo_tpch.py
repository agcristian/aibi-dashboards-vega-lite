#!/usr/bin/env python3
"""Ejemplo de punta a punta con samples.tpch (existe en cualquier workspace): 3 páginas con casi todas las recetas.

  python example_build.py                       # escribe out/ejemplo_tpch.lvdash.json
  python ../scripts/preview.py out/ejemplo_tpch.lvdash.json --profile P --warehouse W
  python ../scripts/deploy.py out/ejemplo_tpch.lvdash.json --name "Ejemplo TPCH" --profile P --warehouse W --parent /Users/<yo>/demo

Úsalo como plantilla: cambia datasets (SQL), nombres de campos y textos; el diseño se conserva.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
import aibi_kit as k  # noqa: E402
from aibi_kit import f, sum_, avg_  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
k.use_theme("cards", palette="vivid", locale="es")
P = k.PAL
CAT, SCH = "samples", "tpch"
D0, D1 = "1997-01-01", "1997-12-31"
RANGO = k.p_date_range("rango", D0, D1)

# ------------------------------------------------------------------ datasets (agrega en SQL al grano que usa la página)
ORD = """samples.tpch.orders o
  JOIN samples.tpch.customer c ON o.o_custkey = c.c_custkey
  JOIN samples.tpch.nation n ON c.c_nationkey = n.n_nationkey
  JOIN samples.tpch.region r ON n.n_regionkey = r.r_regionkey"""
WIN = """o.o_orderdate BETWEEN :rango.min AND :rango.max
     OR o.o_orderdate BETWEEN add_months(:rango.min, -12) AND add_months(:rango.max, -12)"""

# periodo actual y mismo periodo del año anterior alineado al calendario actual (act/ant en columnas)
M_SQL = f"""WITH b AS (
  SELECT o.o_orderdate AS fecha, initcap(r.r_name) AS region, initcap(n.n_name) AS pais,
         initcap(c.c_mktsegment) AS segmento, substring(o.o_orderpriority, 3) AS prioridad, o.o_totalprice AS venta,
         o.o_orderdate BETWEEN :rango.min AND :rango.max AS act
  FROM {ORD}
  WHERE {WIN}
)
SELECT date_trunc('MONTH', CASE WHEN act THEN fecha ELSE add_months(fecha, 12) END) AS mes,
       date_trunc('WEEK', CASE WHEN act THEN fecha ELSE date_add(fecha, 364) END) AS semana,
       region, pais, segmento, prioridad,
       SUM(IF(act, venta, 0)) AS v_act, SUM(IF(act, 0, venta)) AS v_ant,
       SUM(IF(act, 1, 0)) AS n_act, SUM(IF(act, 0, 1)) AS n_ant
FROM b GROUP BY ALL"""

LI_SQL = """SELECT date_trunc('MONTH', l_shipdate) AS mes, date_trunc('WEEK', l_shipdate) AS semana, initcap(l_shipmode) AS modo,
       count(*) AS lineas, SUM(IF(l_receiptdate <= l_commitdate, 1, 0)) AS a_tiempo,
       SUM(IF(l_returnflag = 'R', 1, 0)) AS devueltas, SUM(l_extendedprice) AS bruto,
       SUM(l_extendedprice * l_discount) AS descuento, SUM(IF(l_returnflag = 'R', l_extendedprice, 0)) AS devuelto,
       AVG(datediff(l_receiptdate, l_shipdate)) AS dias,
       percentile_approx(datediff(l_receiptdate, l_shipdate), 0.1) AS p10,
       percentile_approx(datediff(l_receiptdate, l_shipdate), 0.5) AS p50,
       percentile_approx(datediff(l_receiptdate, l_shipdate), 0.9) AS p90
FROM samples.tpch.lineitem
WHERE l_shipdate BETWEEN :rango.min AND :rango.max
GROUP BY ALL"""

WF_SQL = """WITH t AS (
  SELECT SUM(l_extendedprice) AS bruto, SUM(l_extendedprice * l_discount) AS dsc,
         SUM(l_extendedprice * (1 - l_discount) * l_tax) AS imp
  FROM samples.tpch.lineitem WHERE l_shipdate BETWEEN :rango.min AND :rango.max
)
SELECT * FROM (
  SELECT 1 AS orden, 'Venta bruta' AS paso, 'delta' AS tipo, bruto AS v FROM t
  UNION ALL SELECT 2, 'Descuentos', 'delta', -dsc FROM t
  UNION ALL SELECT 3, 'Venta neta', 'total', bruto - dsc FROM t
  UNION ALL SELECT 4, 'Impuestos', 'delta', imp FROM t
  UNION ALL SELECT 5, 'Facturado', 'total', bruto - dsc + imp FROM t
)"""

PART_SQL = """SELECT initcap(split(p.p_type, ' ')[0]) AS linea, initcap(split(p.p_type, ' ')[1]) AS acabado,
       replace(p.p_brand, 'Brand#', 'Marca ') AS marca, split(p.p_container, ' ')[0] AS empaque,
       SUM(l.l_extendedprice * (1 - l.l_discount)) AS venta
FROM samples.tpch.lineitem l JOIN samples.tpch.part p ON l.l_partkey = p.p_partkey
WHERE l.l_shipdate BETWEEN :rango.min AND :rango.max
GROUP BY ALL"""

CLI_SQL = f"""SELECT c.c_custkey AS cliente, initcap(c.c_mktsegment) AS segmento, initcap(r.r_name) AS region,
       count(*) AS pedidos, SUM(o.o_totalprice) AS venta
FROM {ORD}
WHERE o.o_orderdate BETWEEN :rango.min AND :rango.max AND c.c_custkey % 61 = 1
GROUP BY ALL"""

PED_SQL = """SELECT o_orderkey AS pedido, substring(o_orderpriority, 3) AS prioridad, o_totalprice AS ticket,
       least(o_totalprice, 400000) AS ticket_cap, o_orderdate AS fecha
FROM samples.tpch.orders
WHERE o_orderdate BETWEEN :rango.min AND :rango.max AND o_orderkey % 97 = 0"""

DIA_SQL = """SELECT o_orderdate AS fecha, dayofweek(o_orderdate) AS dow, date_trunc('MONTH', o_orderdate) AS mes,
       count(*) AS pedidos, SUM(o_totalprice) AS venta
FROM samples.tpch.orders WHERE o_orderdate BETWEEN :rango.min AND :rango.max GROUP BY ALL"""

COHORT_SQL = """WITH a AS (SELECT DISTINCT o_custkey, date_trunc('MONTH', o_orderdate) AS mes FROM samples.tpch.orders
                WHERE o_orderdate >= DATE'1996-01-01' AND o_custkey % 10 = 0),
c AS (SELECT o_custkey, min(mes) AS cohorte FROM a GROUP BY 1)
SELECT date_format(c.cohorte, 'yyyy-MM') AS cohorte, CAST(months_between(a.mes, c.cohorte) AS INT) AS m,
       count(DISTINCT a.o_custkey) AS activos
FROM c JOIN a USING (o_custkey)
WHERE c.cohorte BETWEEN DATE'1996-01-01' AND DATE'1997-06-01' AND months_between(a.mes, c.cohorte) <= 12
GROUP BY ALL"""

FUNNEL_SQL = """WITH p AS (
  SELECT l_orderkey, count(*) AS n, SUM(IF(l_receiptdate <= l_commitdate, 1, 0)) AS ok
  FROM samples.tpch.lineitem WHERE l_shipdate BETWEEN :rango.min AND :rango.max GROUP BY 1
)
SELECT * FROM (
  SELECT 1 AS orden, 'Pedidos enviados' AS etapa, count(*) AS n FROM p
  UNION ALL SELECT 2, 'Alguna línea a tiempo', count(*) FROM p WHERE ok >= 1
  UNION ALL SELECT 3, 'Mitad o más a tiempo', count(*) FROM p WHERE ok * 2 >= n
  UNION ALL SELECT 4, 'Todo a tiempo', count(*) FROM p WHERE ok = n
)"""

FC_SQL = """WITH a AS (SELECT date_trunc('WEEK', o_orderdate) AS semana, CAST(SUM(o_totalprice) AS DOUBLE) AS venta
           FROM samples.tpch.orders WHERE o_orderdate BETWEEN DATE'1996-01-01' AND DATE'1998-06-28' GROUP BY 1),
f AS (SELECT semana, venta_forecast, venta_upper, venta_lower
      FROM AI_FORECAST(TABLE(a), horizon => '1998-12-28', time_col => 'semana', value_col => 'venta')),
br AS (SELECT semana, venta AS venta_forecast, venta AS venta_upper, venta AS venta_lower, venta FROM a
       WHERE semana = (SELECT max(semana) FROM a))
SELECT semana, venta, CAST(NULL AS DOUBLE) AS venta_forecast, CAST(NULL AS DOUBLE) AS venta_upper,
       CAST(NULL AS DOUBLE) AS venta_lower FROM a WHERE semana >= DATE'1997-06-01'
UNION ALL SELECT semana, venta, venta_forecast, venta_upper, venta_lower FROM br
UNION ALL SELECT semana, CAST(NULL AS DOUBLE), venta_forecast, venta_upper, venta_lower FROM f"""

META_SQL = "SELECT date_format(max(o_orderdate), 'dd/MM/yyyy') AS corte FROM samples.tpch.orders"


def ds(name, display, sql, params=None):
    return k.dataset(name, display, sql, catalog=CAT, schema=SCH, params=params)


DATASETS = [ds("ds_meta", "Corte", META_SQL), ds("ds_m", "Pedidos por mes y semana", M_SQL, [RANGO]),
            ds("ds_li", "Líneas enviadas", LI_SQL, [RANGO]), ds("ds_wf", "Puente de ventas", WF_SQL, [RANGO]),
            ds("ds_part", "Ventas por producto", PART_SQL, [RANGO]), ds("ds_cli", "Clientes (muestra)", CLI_SQL, [RANGO]),
            ds("ds_ped", "Pedidos (muestra)", PED_SQL, [RANGO]), ds("ds_dia", "Pedidos por día", DIA_SQL, [RANGO]),
            ds("ds_cohort", "Cohortes", COHORT_SQL), ds("ds_funnel", "Embudo de entrega", FUNNEL_SQL, [RANGO]),
            ds("ds_fc", "Pronóstico AI_FORECAST", FC_SQL)]
SALES = ["ds_m"]
ALL_RANGE = ["ds_m", "ds_li", "ds_wf", "ds_part", "ds_cli", "ds_ped", "ds_dia", "ds_funnel"]

META = [f("corte")]


def banner(name, title, sub, accent):
    return k.vega(name, "ds_meta", META, k.banner(title, sub, right_field="corte", right_label="Datos al", accent=accent))


def filters(p):
    return [k.range_param_filter(f"{p}_rango", "Periodo", "rango", ALL_RANGE),
            k.filt(f"{p}_region", "Región", "region", ["ds_m", "ds_cli"]),
            k.filt(f"{p}_seg", "Segmento", "segmento", ["ds_m", "ds_cli"]),
            k.filt(f"{p}_prio", "Prioridad", "prioridad", ["ds_m", "ds_ped"])]


# ------------------------------------------------------------------ página 1: Resumen
MK = [f("mes"), sum_("v_act"), sum_("v_ant"), sum_("n_act"), sum_("n_ant")]
LK = [f("mes"), sum_("lineas"), sum_("a_tiempo"), sum_("bruto"), sum_("descuento")]
kpis = [
    k.vega("k_venta", "ds_m", MK, k.kpi_card("Ventas", "mes", "v_act", "v_ant", accent=P[0])),
    k.vega("k_ped", "ds_m", MK, k.kpi_card("Pedidos", "mes", "n_act", "n_ant", kind="int", accent=P[2])),
    k.vega("k_ticket", "ds_m", MK, k.kpi_card("Ticket promedio", "mes", "v_act", "v_ant", "n_act", "n_ant",
                                               kind="money_exact", accent=P[3])),
    k.vega("k_ot", "ds_li", LK, k.kpi_card("Entregas a tiempo", "mes", "a_tiempo", cur_den="lineas", kind="pct", accent=P[5],
                                           note="'Líneas recibidas antes del compromiso'")),
]
w_trend = k.vega("p1_trend", "ds_m", [f("semana"), sum_("v_act"), sum_("v_ant")],
                 k.trend_area("Tendencia semanal de ventas", "Periodo vs mismo periodo del año anterior · promedio móvil de 4 semanas",
                              x="semana", y="v_act", prior="v_ant", drop_edges=True))
w_donut = k.vega("p1_donut", "ds_m", [f("segmento"), sum_("v", "v_act")],
                 k.donut("Ventas por segmento", k.t("click"), "segmento", "v"))
TILES = [("CAN", "Canada", 1, 0), ("GBR", "United Kingdom", 4, 0), ("RUS", "Russia", 7, 0),
         ("USA", "United States", 1, 1), ("FRA", "France", 4, 1), ("DEU", "Germany", 5, 1), ("ROU", "Romania", 6, 1),
         ("CHN", "China", 8, 1), ("JPN", "Japan", 9, 1),
         ("MAR", "Morocco", 4, 2), ("DZA", "Algeria", 5, 2), ("EGY", "Egypt", 6, 2), ("JOR", "Jordan", 7, 2),
         ("IRQ", "Iraq", 8, 2), ("IRN", "Iran", 9, 2),
         ("PER", "Peru", 1, 3), ("BRA", "Brazil", 2, 3), ("ETH", "Ethiopia", 6, 3), ("SAU", "Saudi Arabia", 7, 3),
         ("IND", "India", 8, 3), ("VNM", "Vietnam", 9, 3),
         ("ARG", "Argentina", 2, 4), ("KEN", "Kenya", 6, 4), ("IDN", "Indonesia", 9, 4), ("MOZ", "Mozambique", 6, 5)]
w_tiles = k.vega("p1_tiles", "ds_m", [f("pais"), sum_("v_act"), sum_("v_ant")], k.tile_map(
    "Crecimiento por país", "Mapa de mosaicos · color = ventas vs año anterior", "pais",
    [{"aggregate": [{"op": "sum", "field": "v_act", "as": "a"}, {"op": "sum", "field": "v_ant", "as": "b"}], "groupby": ["pais"]},
     {"calculate": "datum.b == 0 ? null : datum.a / datum.b - 1", "as": "val"},
     {"calculate": "format(datum.val, '+.1%')", "as": "vtxt"}],
    {"domain": [-0.03, 0, 0.03], "range": [k.BAD, "#F5E6A8", k.GOOD], "clamp": True}, tiles=TILES, legend_format="+.0%"))
w_rank = k.vega("p1_rank", "ds_m", [f("pais"), f("region"), sum_("v", "v_act")],
                k.ranked_bars("Principales países", "Ventas del periodo", "pais", "v", top=10, color_field="region"))
w_wf = k.vega("p1_wf", "ds_wf", [f("orden"), f("paso"), f("tipo"), sum_("v")],
              k.waterfall("De la venta bruta a lo facturado", "Puente del periodo", "paso", "orden", "v", kind="tipo"))
w_tree = k.vega("p1_tree", "ds_part", [f("linea"), f("acabado"), sum_("venta")],
                k.treemap("Mezcla por línea y acabado", "Ancho = línea · alto = acabado", "linea", "acabado", "venta"))
w_pareto = k.vega("p1_pareto", "ds_part", [f("marca"), sum_("venta")],
                  k.pareto("Pareto de marcas", "Ventas y % acumulado · punteada = 80%", "marca", "venta"))
w_fc = k.n_forecast("p1_fc", "ds_fc", "semana", "venta", "venta_forecast", "venta_upper", "venta_lower",
                    "Pronóstico semanal de ventas con AI_FORECAST (nativo)", "Semana", "Ventas reales")

f1 = filters("p1")
g1 = k.Grid()
g1.row(3, (banner("p1_banner", "Comercial · Resumen", "Ejemplo del kit sobre samples.tpch", P[1]), 12))
g1.row(2, (f1[0], 3), (f1[1], 3), (f1[2], 3), (f1[3], 3))
g1.row(5, *[(w, 3) for w in kpis])
g1.row(10, (w_trend, 8), (w_donut, 4))
g1.row(10, (w_tiles, 6), (w_rank, 6))
g1.row(10, (w_wf, 6), (w_tree, 6))
g1.row(9, (w_pareto, 5), (w_fc, 7))

# ------------------------------------------------------------------ página 2: Clientes y mercado
w_sun = k.vega("p2_sun", "ds_part", [f("linea"), f("empaque"), sum_("venta")],
               k.sunburst("Ventas por línea y empaque", "Interior = línea · exterior = empaque", "linea", "empaque", "venta"))
w_bump = k.vega("p2_bump", "ds_m", [f("mes"), f("region"), sum_("v", "v_act")],
                k.bump("Ranking mensual de regiones", "Posición por ventas de cada mes", "mes", "region", "v"))
w_cohort = k.vega("p2_cohort", "ds_cohort", [f("cohorte"), f("m"), sum_("activos")],
                  k.cohort("Retención por cohorte", "% de la cohorte que vuelve a comprar en el mes N (muestra 10%)",
                           "cohorte", "m", "activos", domain=(0.10, 0.22)))
w_sc = k.vega("p2_scatter", "ds_cli", [f("cliente"), f("segmento"), sum_("pedidos"), sum_("venta")],
              k.pre(k.scatter("Clientes: frecuencia vs ticket", "Un cliente por burbuja · clic filtra",
                              "pedidos", "ticket", size="venta", color="segmento", y_prefix="$",
                              x_title="Pedidos en el periodo", y_title="Ticket promedio",
                              tooltip=[{"field": "cliente"}, {"field": "segmento"}, {"field": "pedidos"},
                                       {"field": "ticket", "format": "$,.0f"}]),
                    {"calculate": "datum.venta / datum.pedidos", "as": "ticket"}))
DOW_ES = "['', 'Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'][datum.value]"
w_dh = k.vega("p2_dh", "ds_dia", [f("mes"), f("dow"), sum_("pedidos")],
              k.heatmap("Pedidos por día de la semana", "Cada celda: pedidos del mes en ese día", "mes", "dow", "pedidos",
                        x_time_unit="utcyearmonth", y_label_expr=DOW_ES, labels=True))
w_hist = k.n_histogram("p2_hist", "ds_ped", "ticket_cap", 20000, "Distribución del ticket por pedido (histograma nativo)",
                       "Ticket (tope 400 K)", "Pedidos")
w_stack = k.vega("p2_stack", "ds_m", [f("mes"), f("prioridad"), sum_("v", "v_act")],
                 k.stacked_share("Mezcla por prioridad", "Participación mensual de cada prioridad", "mes", "prioridad", "v"))
MAT_COLS = [{"key": "v_act", "label": "Ventas", "fmt": "money", "bar": True},
            {"key": "v_ant", "label": "Año ant.", "fmt": "money"},
            {"key": "var", "label": "Var $", "fmt": "money", "expr": "datum.v_act - datum.v_ant", "sign": True},
            {"key": "crec", "label": "Crec. %", "fmt": "pct", "expr": "datum.v_ant == 0 ? null : datum.v_act / datum.v_ant - 1",
             "pill": "datum.v_act - datum.v_ant"},
            {"key": "n_act", "label": "Pedidos", "fmt": "int"}]
w_mat = k.vega("p2_mat", "ds_m", [f("region"), f("pais"), sum_("v_act"), sum_("v_ant"), sum_("n_act")],
               k.matrix("Matriz región · país", "Subtotal por región (fondo azul) y países sangrados · ordenado por ventas",
                        ["region", "pais"], MAT_COLS, ["v_act", "v_ant", "n_act"], top=5))
w_div = k.vega("p2_div", "ds_m", [f("pais"), sum_("v_act"), sum_("v_ant")],
               k.pre(k.diverging_bars("Variación vs año anterior por país", "Top 12 por magnitud", "pais", "var", top=12),
                     {"calculate": "datum.v_act - datum.v_ant", "as": "var"}))
w_sankey = k.n_sankey("p2_sankey", "ds_m", [("region", "Región"), ("segmento", "Segmento"), ("prioridad", "Prioridad")],
                      "v_act", "Flujo de ventas región, segmento y prioridad (Sankey nativo)", "Ventas")
w_table = k.n_table("p2_table", "ds_m", [
    {"fieldName": "pais", "displayName": "País"}, {"fieldName": "segmento", "displayName": "Segmento"},
    {"fieldName": "v_act", "displayName": "Ventas", "format": k.fmt_currency("USD"), "displayAs": "color-scale"},
    {"fieldName": "v_ant", "displayName": "Año anterior", "format": k.fmt_currency("USD")},
    {"fieldName": "n_act", "displayName": "Pedidos"}], "Detalle por país y segmento (tabla nativa)", disaggregated=False)

f2 = filters("p2")
g2 = k.Grid()
g2.row(3, (banner("p2_banner", "Clientes y mercado", "Mezcla, ranking, retención y comportamiento", P[2]), 12))
g2.row(2, (f2[0], 3), (f2[1], 3), (f2[2], 3), (f2[3], 3))
g2.row(11, (w_sun, 4), (w_bump, 8))
g2.row(12, (w_cohort, 7), (w_sc, 5))
g2.row(9, (w_dh, 7), (w_hist, 5))
g2.row(23, (w_mat, 12))
g2.row(10, (w_div, 6), (w_stack, 6))
g2.row(10, (w_sankey, 6), (w_table, 6))

# ------------------------------------------------------------------ página 3: Operación
GF = [sum_("lineas"), sum_("a_tiempo"), sum_("bruto"), sum_("descuento")]
RATIOS = [{"calculate": "datum.a_tiempo / datum.lineas", "as": "ot"}, {"calculate": "datum.bruto / datum.lineas", "as": "tl"},
          {"calculate": "datum.descuento / datum.bruto", "as": "dsc"}]
URG = [{"joinaggregate": [{"op": "sum", "field": "n", "as": "tot"}]}, {"filter": "datum.prioridad == 'URGENT'"},
       {"calculate": "datum.n / datum.tot", "as": "urg"}]
gauges = [k.vega("p3_g1", "ds_li", GF, k.pre(k.gauge("A tiempo", "ot", 0.40, 0.2, 0.6, accent=P[5]), *RATIOS)),
          k.vega("p3_g2", "ds_m", [f("prioridad"), sum_("n", "n_act")],
                 k.pre(k.gauge("Urgentes", "urg", 0.18, 0.0, 0.4, inverse=True, accent=P[3]), *URG)),
          k.vega("p3_g3", "ds_li", GF, k.pre(k.gauge("Descuento", "dsc", 0.06, 0.0, 0.1, inverse=True, accent=P[0]), *RATIOS)),
          k.vega("p3_g4", "ds_li", [avg_("dias")], k.gauge("Días de tránsito", "dias", 16, 0, 30, fmt=".1f", inverse=True, accent=P[6]))]
w_radar = k.vega("p3_radar", "ds_li", [f("modo")] + GF + [avg_("dias")],
                 k.pre(k.radar("Comparativo de modos de envío", "Normalizado (más afuera = mejor)", "modo",
                               [("ot", "A tiempo", False), ("tl", "Valor por línea", False), ("dsc", "Descuento", True),
                                ("lineas", "Volumen", False), ("dias", "Días", True)]), *RATIOS))
w_bullet = k.vega("p3_bullet", "ds_li", [f("modo"), sum_("lineas"), sum_("a_tiempo")],
                  k.pre(k.bullet("A tiempo por modo vs meta", "Bandas: crítico, en riesgo, en meta · marca = meta 37%", "modo", "ot",
                                 [(0.35, 0.365, k.BAD_BG), (0.365, 0.37, k.WARN_BG), (0.37, 0.38, k.GOOD_BG)], 0.37, (0.35, 0.38)),
                        {"calculate": "datum.a_tiempo / datum.lineas", "as": "ot"}))
w_funnel = k.vega("p3_funnel", "ds_funnel", [f("orden"), f("etapa"), sum_("n")],
                  k.funnel("Embudo de entrega a tiempo", "Pedidos según cuántas de sus líneas llegaron antes del compromiso", "etapa", "orden", "n"))
w_box = k.vega("p3_box", "ds_ped", [f("prioridad"), f("ticket")],
               k.boxplot("Ticket por prioridad", "Box plot sobre una muestra de pedidos", "prioridad", "ticket", y_title="Ticket"),
               disaggregated=True)
w_band = k.vega("p3_band", "ds_li", [f("semana"), sum_("lineas"), avg_("p10"), avg_("p50"), avg_("p90")],
                k.percentile_band("Días de tránsito por semana", "Mediana y rango p10-p90", "semana", "p10", "p50", "p90",
                                  weight="lineas", ref=15, ref_label="Compromiso 15 días", y_title="Días"))
w_cal = k.vega("p3_cal", "ds_dia", [f("fecha"), sum_("venta")],
               k.calendar("Calendario de ventas", "Cada columna es una semana", "fecha", "venta"))
w_dual = k.vega("p3_dual", "ds_dia", [f("fecha"), sum_("venta"), sum_("pedidos")],
                k.dual_axis("Ventas y pedidos diarios", "Área = ventas · línea = pedidos (eje derecho)",
                            "fecha", "venta", "pedidos", "Ventas", "Pedidos", left_prefix="$"))
w_flow = k.vega("p3_flow", "ds_li", [f("mes"), sum_("bruto"), sum_("descuento")],
                k.inflow_outflow("Ingreso bruto vs descuentos", "Arriba ingreso, abajo descuentos · línea = neto",
                                 "mes", "bruto", "descuento", "Ingreso", "Descuentos", "Neto"))
w_nheat = k.n_heatmap("p3_nheat", "ds_li", "modo", "mes", "dias", "Días de tránsito por modo y mes (heatmap nativo)",
                      x_label="Modo", y_label="Mes", val_label="Días")

f3 = [k.range_param_filter("p3_rango", "Periodo", "rango", ALL_RANGE), k.filt("p3_modo", "Modo de envío", "modo", ["ds_li"])]
g3 = k.Grid()
g3.row(3, (banner("p3_banner", "Operación y logística", "Cumplimiento, tiempos y calidad de entrega", P[5]), 12))
g3.row(2, (f3[0], 6), (f3[1], 6))
g3.row(5, *[(w, 3) for w in gauges])
y = g3.y
g3.items.append(k.pos(w_radar, 0, y, 5, 12))
g3.stack(5, 7, (w_bullet, 6), (w_funnel, 6))
g3.advance(12)
g3.row(10, (w_box, 6), (w_band, 6))
g3.row(8, (w_cal, 12))
g3.row(10, (w_dual, 6), (w_flow, 6))
g3.row(9, (w_nheat, 12))

DASH = k.dashboard(DATASETS, [k.page("resumen", "Resumen", g1.items), k.page("clientes", "Clientes y mercado", g2.items),
                              k.page("operacion", "Operación", g3.items)])

if __name__ == "__main__":
    k.save(DASH, os.path.join(HERE, "out", "ejemplo_tpch.lvdash.json"))
