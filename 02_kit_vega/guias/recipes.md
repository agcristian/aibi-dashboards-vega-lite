# Catálogo de recetas (`aibi_kit.py`)

## Uso general

- Cada receta devuelve un spec de Vega-Lite. Lo envuelves con `k.vega(nombre, dataset, fields, spec)`.
- `fields` define las columnas que llegan al spec:
  - `f("col")` para dimensiones;
  - `sum_("alias", "col")`, `avg_`, `agg("alias", "COUNT_DISTINCT", "col")` para medidas.
- Las recetas re-agregan dentro del spec. Mandar ya agregado es más rápido; mandar crudo con `disaggregated=True` sirve para distribuciones.
- `k.pre(spec, {"calculate": ..., "as": ...})` antepone cálculos: razones, renombres o filtros.

## Encabezados y tarjetas

| Receta | Datos | Notas |
|---|---|---|
| `banner(title, subtitle, right_field, right_label, bg, accent)` | 1 fila (p. ej. `corte`) | Alto 3. El acento por página va en `accent`. |
| `section(title, subtitle, color)` | cualquiera (no lee datos) | Alto 2. Separador y aire vertical. |
| `kpi_card(title, x, cur, prior, cur_den, prior_den, kind, inverse, accent, agg_mode, mom, mom_abs, note)` | periodo `x` + columnas act/ant (y denominadores si es razón) | `kind`: money, money_exact, pct, int. Con `cur_den` el valor es razón y el delta en pct va en pp. `note` reemplaza la primera línea, por ejemplo `"'Promedio: ' + (" + k.fmt_money('S_mean') + ")"`. Alto 5. |
| `stat_card(title, value_expr, sub_expr, accent, transforms)` | 1 fila | Valor sin serie. |

## Tendencias

| Receta | Datos | Notas |
|---|---|---|
| `trend_area(title, sub, x, y, prior, ma, color, x_format, drop_edges)` | serie temporal (semana/día) | Área con degradado, comparable punteado, promedio móvil y regla de hover con tooltip. `drop_edges` quita semanas incompletas. |
| `combo_bars_lines(title, sub, x, bar, lines=[(col, etiqueta, punteada)], ratio_label=col)` | mensual | Real en barras; meta y año anterior en líneas. Etiqueta de alcance verde o roja sobre la barra. |
| `dual_axis(title, sub, x, left, right, left_title, right_title)` | serie temporal | Escalas independientes; el título de cada eje va en el color de su serie. |
| `percentile_band(title, sub, x, lo, mid, hi, weight, ref, ref_label)` | p10/p50/p90 por periodo | `weight` (conteo) para re-agregar ponderado. `ref` dibuja la línea de compromiso. |
| `bump(title, sub, x, cat, val)` | periodo x categoría | Ranking por periodo, con etiqueta al final. Funciona hasta unas 10 categorías. |
| `stacked_share(title, sub, x, cat, val, normalize)` | periodo x categoría | Mezcla 100% o apilado absoluto. |
| `inflow_outflow(title, sub, x, inflow, outflow, ...)` | periodo con entradas y salidas (positivas) | Barras divergentes y línea de neto. Para flujo de efectivo. |

## Composición y ranking

| Receta | Datos | Notas |
|---|---|---|
| `donut(title, sub, cat, val, domain, colors, cross_filter)` | categoría | El cross-filter queda activado: clic en un segmento filtra la página. |
| `ranked_bars(title, sub, cat, val, top, color_field, sqrt)` | categoría | Top N horizontal con etiqueta. Usa la clave rango\|nombre para no perder el orden. |
| `diverging_bars(title, sub, cat, val, top, positive_is_good)` | categoría con variación | Verde o rojo, etiqueta a la derecha. Calcula `val` antes con `pre`. |
| `waterfall(title, sub, step, order, val, kind)` | filas en orden; `kind` = 'delta' o 'total' | Los subtotales vienen como filas del SQL. Sin `kind` es un puente de deltas. Usa nombres cortos. |
| `pareto(title, sub, cat, val, threshold)` | categoría | Barras más % acumulado en eje derecho y regla del umbral. |
| `treemap(title, sub, l1, l2, val)` | 2 niveles | Slice-and-dice calculado en Vega. Etiqueta solo en celdas grandes. |
| `sunburst(title, sub, inner, outer, val)` | 2 niveles | Exterior con el color del padre y opacidad. |

## Calor y calendario

| Receta | Datos | Notas |
|---|---|---|
| `heatmap(title, sub, x, y, val, diverging, labels, x_time_unit, x_label_expr, y_label_expr, y_sort)` | 2 dimensiones | Día x hora, elemento x mes. `diverging` usa symlog centrado en 0. |
| `cohort(title, sub, cohort, n, active, domain)` | cohorte 'yyyy-MM', mes N, activos | Retención con % en cada celda. Ajusta `domain` al rango real. |
| `calendar(title, sub, date, val)` | diario | Tipo GitHub: semanas en columnas, días en filas. |

## Distribución y relación

| Receta | Datos | Notas |
|---|---|---|
| `scatter(title, sub, x, y, size, color, log_x, log_y, cross_filter)` | 1 fila por entidad | Clic filtra por `color`. Muestrea si hay más de ~3 mil puntos. `clip` evita que se salga del marco. |
| `boxplot(title, sub, cat, val)` | crudo (`disaggregated=True`) | Usa una muestra en SQL (`id % n = 0`) para no traer todo. |
| `funnel(title, sub, stage, order, val)` | una fila por etapa | Etiqueta "etapa · n (% del total)" y conversión vs la etapa anterior. |

## Desempeño vs meta

| Receta | Datos | Notas |
|---|---|---|
| `gauge(title, field, target, lo, hi, fmt, inverse, accent)` | 1 fila | Títulos cortos: con varios gauges en fila el ancho es poco. La razón se calcula con `pre`. |
| `bullet(title, sub, cat, val, bands=[(desde, hasta, color)], target, domain, fmt)` | categoría | Bandas con `k.BAD_BG`, `k.WARN_BG` y `k.GOOD_BG`. |
| `radar(title, sub, series, metrics=[(col, etiqueta, invertir)])` | 1 fila por serie | Normaliza min-max por métrica. Usa de 4 a 7 métricas y de 2 a 6 series. |

## Mapas

| Receta | Datos | Notas |
|---|---|---|
| `choropleth(title, sub, key, val, geo_values, rename)` | región por nombre | `geo_values = k.load_geo(".../mx_estados.json")`. En ese archivo el estado se llama 'México': usa `rename={'Estado de México': 'México'}`. Para otro país, simplifica su GeoJSON con `simplify_geo.py`. |
| `tile_map(title, sub, key, value_transforms, color_scale, tiles)` | región por nombre | Celdas iguales: comparable y legible. Trae `TILES_MX`; `example_build.py` trae una rejilla mundial de 25 países. `value_transforms` deja `val` (color) y `vtxt` (etiqueta). |

## Redes y linaje

| Receta | Datos | Notas |
|---|---|---|
| `layered_network(title, sub, kinds, colors, node_color, focus_color, header_color, node_size, label_size, legend_columns, x_pad, y_pad, ...)` | dataset de `network_sql(nodos_sql, aristas_sql)`; `fields = [f(c) for c in k.NETWORK_FIELDS]` con `disaggregated=True` | Red por capas con enlaces curvos y foco por clic: clic en un nodo deja solo él, sus aristas y sus vecinos directos; clic en el fondo o doble clic regresa a todo. Sirve para linaje, flujos de proceso y dependencias. Ejemplo: `examples/example_network.py`. |

`network_sql(nodos_sql, aristas_sql)` hace el layout en SQL. Los nodos van en columnas por `orden_capa` y se centran en vertical. Además calcula los vecinos de cada nodo y agrega una fila de encabezado por capa.

- **`nodos_sql` devuelve:**
  - `nodo`: id único, sin `|`;
  - `etiqueta`;
  - `capa`: texto del encabezado;
  - `orden_capa`: número de columna;
  - `info`: texto del tooltip.
- **`aristas_sql` devuelve:** `origen`, `destino`, `relacion` (categoría del color) e `info`.

Reglas de diseño:

- **Aristas dentro de la misma columna:** se enciman y se ven como una línea vertical. Pon el destino en una subcolumna con decimales: `orden_capa` 2 y 2.45 caen bajo el mismo encabezado. Otra opción es separarlo en su propia capa.
- **Hasta unos 30 nodos y 60 aristas** se lee bien. Con más, filtra en SQL por dominio o esquema.
- **Por qué no un Sankey:** en un Sankey el grosor de la banda es una cantidad. El linaje solo dice que A alimenta a B, así que un Sankey con bandas iguales se ve igual que esta red, pero sin el foco. Usa `n_sankey` solo cuando haya volumen real: filas, montos o clientes.
- **Complementos:**
  - entradas y salidas por nodo, en barras divergentes con `diverging_bars`, para el análisis de impacto (qué nadie consume);
  - la tabla de aristas.

Linaje real desde `system.access.table_lineage` (ajusta el filtro y la regla de capas):

```sql
-- aristas
SELECT source_table_full_name AS origen, target_table_full_name AS destino,
       CASE WHEN max(target_type) IN ('VIEW', 'METRIC_VIEW') THEN 'Definición de vista' ELSE 'Transformación' END AS relacion,
       concat_ws(', ', collect_set(entity_type)) AS info
FROM system.access.table_lineage
WHERE event_date >= current_date() - INTERVAL 30 DAYS
  AND source_table_full_name LIKE 'mi_catalogo.%' AND target_table_full_name LIKE 'mi_catalogo.%'
  AND source_table_full_name NOT LIKE '%.\\_\\_%' AND target_table_full_name NOT LIKE '%.\\_\\_%'  -- tablas internas del pipeline
GROUP BY 1, 2
-- nodos: UNION de origen y destino; capa por esquema (CASE split(nodo, '\\.')[1] WHEN 'bronze' THEN 1 ...);
-- etiqueta = split(nodo, '\\.')[2]; info = table_type de information_schema.tables
```

Las entidades que escriben sin tabla de origen (pipeline, notebook) o que leen sin tabla destino (dashboard) traen `source_table_full_name` o `target_table_full_name` en NULL. Para mostrarlas como nodo, úsalas como `concat(entity_type, ' ', left(entity_id, 8))`. Tableau, Genie y los volumes no aparecen como entidades: dilo en el subtítulo.

## Matriz

`matrix(title, sub, levels, columns, measures, top, mode, period, stock_first, stock_last)` reproduce la matriz de Power BI:

- Tiene de 1 a 3 niveles con sangría y subtotal. El nivel 1 va en negrita con fondo.
- Usa zebra, barras de datos (`bar`), verde o rojo por signo (`sign`) y una píldora de alcance (`pill` = expresión de signo).
- Las columnas derivadas usan `expr` sobre medidas ya sumadas.
- Medidas tipo saldo:
  - `stock_first` toma el valor del primer periodo filtrado;
  - `stock_last` toma el del último.
- Alto sugerido: 1 fila de rejilla por cada 1.3 filas de matriz, más 3.

## Nativos (ver native-widgets.md)

| Función | Notas |
|---|---|
| `n_table` | Formatos `k.fmt_currency(code)`, `k.FMT_PCT` y `k.STYLE_SIGN`. |
| `n_sankey(stages=[(col, etiqueta)], value_col)` | |
| `n_heatmap` | |
| `n_histogram(col, bin_width)` | Recorta outliers en SQL. |
| `n_forecast` | Para `AI_FORECAST`. |
| `n_points(lat, lon, color, mapping)` | Sin tamaño. |
