# Contrato JSON y errores conocidos

## Widget custom-vega-viz

```json
{"widget": {"name": "w1",
  "queries": [{"name": "main_query", "query": {"datasetName": "ds_v", "disaggregated": false,
              "fields": [{"name": "mes", "expression": "`mes`"}, {"name": "v", "expression": "SUM(`venta`)"}]}}],
  "spec": {"version": 1, "widgetType": "custom-vega-viz",
           "jsonSpec": {"type": "vega-lite", "spec": "<json.dumps del spec>"},
           "encodings": {"fields": [{"fieldName": "mes"}, {"fieldName": "v"}]},
           "data": {"queryName": "main_query"}}},
 "position": {"x": 0, "y": 0, "width": 6, "height": 10}}
```

- **`jsonSpec.spec` es un STRING.** Si va como objeto, el widget es inválido.
- **`encodings.fields` lista cada columna.** Si está vacío, sale "Visualization has no fields selected".
- **La fuente del spec es `{"data": {"name": "databricks_query"}}`.** No funcionan `data.url`, `datasets` top-level ni Vega completo. Se permiten `values` inline en capas: geometría, rejillas, leyendas manuales.
- **`disaggregated`:**
  - `false`: el visor agrupa por las columnas sin agregación. Es lo normal.
  - `true`: manda filas crudas. Úsalo en box plot o puntos, junto con un filtro de muestra (`filters=["\`muestra\` = true"]`).
- **El tamaño es responsivo:** `width/height: "container"` + `autosize fit` (lo pone `spec()`).

## Datasets, parámetros y filtros

- Cada dataset lleva `"catalog"` y `"schema"` propios. `lakeview update` reemplaza el JSON completo y borra los defaults del create: sin ellos, nada renderiza.
- **Parámetro de valor:** `p_string("kpi", "Ventas")`. En el SQL va como `:kpi`, por ejemplo `CASE :kpi WHEN ...`. Se elige con `param_filter(name, title, opts_dataset, opts_field, "kpi", [datasets])`, que necesita un dataset de opciones (`SELECT explode(array(...)) AS opcion`).
- **Parámetro de rango de fechas:** `p_date_range("rango", min, max)`, que en SQL se usa como `:rango.min` y `:rango.max`. El selector es `range_param_filter(...)`.
- **Patrón "periodo vs mismo periodo del año anterior"** (KPIs y tendencias):
  1. Restringe el WHERE a las dos ventanas exactas: `fecha BETWEEN :rango.min AND :rango.max OR fecha BETWEEN add_months(:rango.min, -12) AND add_months(:rango.max, -12)`. Si no, se cuelan meses que no van.
  2. Arma un flag `act` y columnas `IF(act, x, 0) AS x_act`, `IF(act, 0, x) AS x_ant`.
  3. Alinea el periodo: `date_trunc('MONTH', CASE WHEN act THEN fecha ELSE add_months(fecha, 12) END)`; en semanas, `date_add(fecha, 364)`.
- **Filtro de campo en varios datasets:** `filt(name, title, campo, [ds1, ds2])` arma una query por dataset. Solo filtra los datasets que tienen ese campo.
- **Cross-filter desde Vega:** el param debe llamarse `databricks_mark_selection` (`select point` con `fields`) y el spec debe ser de una sola vista. Con `layer` deja de filtrar.

## Interacción dentro del widget (sin cross-filter)

Verificado en el visor real, en borrador y publicado, en oct-2026.

- **Params de selección con otro nombre:** funcionan en specs con `layer`. Solo `databricks_mark_selection` está atado al cross-filter y a la vista única.
- **Dónde va el param:** se define en UNA capa, la de los nodos. Las demás lo leen por expresión: `foco.k1[0]` es el valor elegido e `isValid(foco.k1)` indica si hay selección. Un `point` con `fields` resuelve a `{campo: [valores]}`; vacío es `{}`.
- **Expresiones con `datum` en propiedades de mark:** `opacity`, `strokeWidth`, `fontWeight` y `dx` aceptan `{"expr": "..."}` y se evalúan por elemento. Así se atenúa lo que no está en foco sin duplicar datos. `fontWeight` no sirve como canal de encoding, pero como propiedad del mark con `expr` sí aplica.
- **Leyenda:** usa `symbolOpacity: 1`. Si no, la leyenda hereda la opacidad atenuada y desaparece al hacer foco.
- **Modo edición:** el primer clic selecciona el widget; el segundo ya llega al spec. En la vista publicada basta un clic. Presenta siempre desde la publicada.
- **Probar el clic sin visor:** arma un HTML con `vega.min.js` y `vega-lite.min.js` de `~/.cache/aibi-vega-preview/node_modules`. Despacha `pointerdown`, `mousedown`, `pointerup`, `mouseup` y `click` sobre el `path` del nodo y lee `view.signal('foco')`.
- **En el visor real:** el lienzo es `canvas`. Busca el elemento con `document.elementFromPoint(x, y)` (coordenadas CSS = px del screenshot / `devicePixelRatio`) y despacha ahí los mismos eventos, con `PointerEvent`, `composed: true` y `pointerId: 1`.

## Errores conocidos y su arreglo

| Síntoma | Causa | Arreglo |
|---|---|---|
| Todas las viz en blanco, sin error | `dashboardTheme.resolvedFontSettings` o `widgetBackgroundColor` dentro del spec | Colores hex fijos (el kit lo hace) |
| Todo vacío tras un update | Dataset sin catalog/schema | `dataset(..., catalog, schema)` |
| La gráfica sale chiquita o aplastada | Título o subtítulo más ancho que el trazo con autosize fit | `title.limit = width + title_extra` (el kit lo hace); sube `title_extra` en barras horizontales |
| Meses corridos un día ("dic" en vez de "ene") | Funciones de tiempo locales | `utcyearmonth`, `utc()`, `utcFormat` |
| Una regla horizontal por categoría | La regla hereda `x` de una escala de bandas | `x: {value: 0}`, `x2: {value: {expr: "width"}}` (`full_rule`) |
| Se pierde el orden en barras con capas | El sort por campo se pierde al unir dominios | Clave `rango\|nombre` y `labelExpr: split(datum.label, '|')[1]` |
| La negrita condicional no aplica | `fontWeight` no es canal de encoding (se descarta en silencio) | Capa aparte con filtro y `mark.fontWeight` |
| `Cannot read properties of undefined (reading 'type')` | `x: datum` + `x2: field` | Invierte: `x: field` + `x2: datum` |
| Texto concatenado roto ("Prom. mensual" sin número) | Precedencia de `+` con el ternario de `fmt_money` | Envuelve el formato en paréntesis (el kit ya lo devuelve así) |
| KPI con % absurdo (miles de %) | Comparación de valores que cruzan cero o razones sumadas | `mom_abs=True`, o razones con `cur_den`/`prior_den` |
| Pico raro al inicio de un promedio móvil | La ventana incompleta | Pon `null` las primeras n-1 filas |
| Títulos de gauge cortados | Tarjeta angosta | Títulos de 1 o 2 palabras |
| Histograma aplastado | Outliers | `least(col, tope)` en SQL |
| Burbujas enormes en el mapa nativo | Encoding de tamaño | Quítalo |
| "Invalid widget definition" | Spec nativo no soportado (ver native-widgets.md) | Rehazlo en Vega |
| La leyenda desaparece al resaltar | Hereda la `opacity` con `expr` del mark | `legend.symbolOpacity: 1` |
| Los KPIs de razón se ven absurdos en "Edit draft" (19,46..., 586,449,6...) y bien en publicado | Render del editor | Revisa y presenta en la vista publicada |
| El nombre del dashboard se rechaza | `/` en `display_name` | Usa `·` |
| El CLI responde "Refresh token is invalid" | Sesión OAuth vencida | `databricks auth login --profile <perfil>` |

## Verificación

- **`preview.py`** reproduce la query del visor con los defaults de parámetros y filtros. Detecta errores de compilación y de SQL, ejes y etiquetas que no caben, y datos raros.
- **`preview.py --offline`** solo compila.
- **El visor real** es necesario para:
  - nativos;
  - cross-filter;
  - tokens de tema;
  - interacción de filtros y parámetros.
- **Abrir una página directo en el navegador:** `/dashboardsv3/<id>/published/pages/<nombre de página>`.
- **Revisar una página larga:** los widgets fuera de pantalla no se montan hasta que haces scroll.
- **Para revisar en el navegador una página larga:** el contenedor con scroll es `.dbsql-legacy-mfe-page`. Muévelo con JS (`el.scrollTop = n`). Las pestañas de página responden a eventos pointer/mouse despachados.
