# Widgets nativos: cuáles usar y cuáles reemplazar

Observado en el visor real de AI/BI (octubre 2026). Los nativos dan interacción gratis: tooltip, orden, descarga y filtros. Úsalos cuando lucen igual o mejor que Vega.

## Funcionan (el kit trae la función)

### Tabla (`n_table`, table v2)

- `columns`: lista con `fieldName` y `displayName`, más opcionales:
  - `format`: `k.fmt_currency("USD")`, `k.FMT_PCT`;
  - `style`: `k.STYLE_SIGN` (verde o rojo por signo);
  - `dateTimeFormat`: "MMM YYYY", "DD/MM/YYYY HH:mm".
- Úsala para detalle descargable al final de la página.
- `displayAs: "color-scale"` se acepta pero no siempre se ve coloreado. Para formato condicional seguro usa `style` con reglas.

### Sankey (`n_sankey`, sankey v1)

- Tiene 2 o 3 etapas y un valor sumado. El valor se llama `sum(col)` como fieldName.
- Sirve para entradas, banco y uso, o región, segmento y canal.

### Heatmap (`n_heatmap`, heatmap v3)

- Ejes categóricos con `hideTitle` y rampa `custom-sequential` (start/end).

### Histograma (`n_histogram`, histogram v3)

- El campo es `bin(col, binWidth=N)` con expresión `BIN_FLOOR(\`col\`, N)`, y `count(*)` es `COUNT(\`*\`)`.
- Recorta outliers en SQL.

### Pronóstico (`n_forecast`, forecast-line v1)

- Va con `disaggregated=True`. El SQL une tres partes:
  1. histórico con las columnas de pronóstico en NULL;
  2. la última fila real duplicada como pronóstico, para que la línea no tenga hueco;
  3. la salida de `AI_FORECAST`.
- `AI_FORECAST` sí corre en warehouse serverless:

```sql
WITH a AS (SELECT date_trunc('WEEK', fecha) AS semana, CAST(SUM(v) AS DOUBLE) AS venta FROM t GROUP BY 1),
f AS (SELECT semana, venta_forecast, venta_upper, venta_lower
      FROM AI_FORECAST(TABLE(a), horizon => '2026-12-28', time_col => 'semana', value_col => 'venta')),
br AS (SELECT semana, venta AS venta_forecast, venta AS venta_upper, venta AS venta_lower, venta FROM a
       WHERE semana = (SELECT max(semana) FROM a))
SELECT semana, venta, CAST(NULL AS DOUBLE) AS venta_forecast, CAST(NULL AS DOUBLE) AS venta_upper, CAST(NULL AS DOUBLE) AS venta_lower FROM a
UNION ALL SELECT semana, venta, venta_forecast, venta_upper, venta_lower FROM br
UNION ALL SELECT semana, CAST(NULL AS DOUBLE), venta_forecast, venta_upper, venta_lower FROM f
```

### Mapa de puntos (`n_points`, symbol-map v2)

- Lleva latitud, longitud, color categórico con `mappings` y `mark.opacity`.
- Sin encoding de tamaño: las burbujas salen gigantes.

### Filtros

- Tipos: `filter-multi-select`, `filter-single-select`, `filter-date-range-picker` y `filter-date-picker`.
- Pueden ser de campo o atados a parámetro.

## Fallaron y se reemplazan con Vega

| Nativo | Qué pasó | Reemplazo |
|---|---|---|
| Coroplético (`choropleth-map`, regiones `mapbox-v4-admin`) | Con admin0 = país, los estados de México no resolvieron ni por ISO 3166-2 ni por nombre: el mapa salió vacío. Otros países pueden funcionar; pruébalo antes. | `choropleth` con geometría inline (`load_geo`) o `tile_map` |
| Embudo (`funnel` v1 / v3) | v1: "Invalid widget definition". v3 se dibujó como líneas. | `funnel` |
| Box plot (`box` v1 / v3) | v1 inválido; v3 "no fields selected" con las specs documentadas | `boxplot` |

## Preferir Vega aunque exista nativo

- **Tarjetas KPI:** el `counter` nativo no trae sparkline ni doble delta. Usa `kpi_card`.
- **Matriz con jerarquía, barras de datos y píldoras:** el pivot nativo no da ese control visual. Usa `matrix`. Si el usuario necesita exportar, deja además una tabla nativa.
