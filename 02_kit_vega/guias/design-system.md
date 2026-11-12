# Sistema de diseño

El objetivo es que el tablero se lea como un Power BI bien hecho: limpio, con aire, jerarquía clara y mucha personalización, sin perder que es AI/BI (filtros nativos, parámetros, cross-filter y publicación).

## Rejilla y aire

- La rejilla tiene 12 columnas con un gutter fijo de unos 8 px. Una fila mide unos 40 a 42 px de alto.
- En el visor, las columnas vacías se respetan y las filas vacías se colapsan: los widgets suben.
  - Para aire lateral usa `Grid(margin=1)`.
  - Para aire vertical usa un `section()` o un `text()` de alto 2. No dejes huecos.
- El aire dentro de la tarjeta lo da el `padding` de Vega. La base de `spec()` es (36, 28, 36, 26); súbelo en piezas protagonistas.
- **Tema `cards`** (lienzo gris #EEF2F7, tarjetas blancas, radio 12): se ve como Power BI. Separa por contraste de tarjeta.
- **Tema `flat`** (todo blanco): el padding de Vega se lee como separación. Combínalo con `margin=1` y parejas 5+5 o 6+6. Un hueco de 2 columnas entre parejas es demasiado.

## Estructura de cada página

Las alturas están en filas de la rejilla.

| Bloque | Alto | Ancho | Notas |
|---|---|---|---|
| Banner (`banner`) | 3 | 12 | Título, subtítulo y fecha de corte a la derecha. Un acento de color distinto por página da identidad. |
| Fila de filtros | 2 | 3+3+3+3 o 4+4+4 | El periodo primero. |
| Fila de KPIs (`kpi_card`) | 5 | 6 de 2, 4 de 3 o 5 de 2 + margen | Máximo 6. |
| Protagonista + complemento | 10 | 8 + 4 o 7 + 5 | Ejemplos: tendencia + dona, mapa + ranking. |
| Filas de análisis | 9 a 12 | 6 + 6 o 7 + 5 | Una pregunta por tarjeta. |
| Detalle | 6 a 14 | 12 | Matriz o tabla nativa al final de la página. |

- Usa de 3 a 5 páginas por tablero. Ordénalas de lo general a lo operativo. Por ejemplo: Resumen, Clientes, Finanzas, Operación.
- Las columnas apiladas (`Grid.stack`) sirven para dos piezas bajas junto a una alta, como un radar con bullet + embudo.

## Color

- La paleta categórica es `k.PAL` (8 colores). Usa el mismo color para la misma categoría en todo el tablero: pasa `domain`/`colors` fijos en donas, dispersión y barras.
- El color semántico es aparte: `GOOD` (verde) y `BAD` (rojo) solo para "favorable o desfavorable", nunca como categorías.
  - Con `inverse=True` en KPIs y gauges, bajar es bueno.
- Para escalas secuenciales usa un solo tono de claro a oscuro. Las divergentes se centran en 0 (`heatmap(diverging=True)`).
- El acento por página va en el banner y en el ícono de los KPIs. Rota la paleta (`P[0]`, `P[2]`, `P[5]`...).
- El comparable (año anterior, meta) va en gris punteado. Lo actual siempre lleva color.

## Tipografía y textos

- Usa Segoe UI / Inter. Los tamaños por elemento son:
  - título 15 bold;
  - subtítulo 11.5 gris;
  - valor de KPI 27 bold;
  - etiquetas 10.5 a 11.
- Cada tarjeta lleva su título dentro del spec, con un subtítulo que explique cómo leerla. Por ejemplo: "Bandas: crítico, en riesgo, en meta · marca = meta 65%".
- Las cifras van compactas con unidades (`$1.2 M`, `940 K`, `+3.4%`, `2.1 pp`). Usa `fmt_money`, `fmt_short` y `axis_short`.
  - En español, miles de millones es `MM`; en inglés, `B`.
- No uses em dashes ni flechas en textos. Usa `·` como separador. Los triángulos ▲ ▼ solo van en deltas.

## Composición de visuales (qué usar para qué)

| Pregunta | Receta |
|---|---|
| ¿Cómo voy? | `kpi_card` (valor, vs año ant., vs mes ant., sparkline) |
| ¿Cómo evoluciona? | `trend_area` (con comparable y promedio móvil), `combo_bars_lines` (real vs meta) |
| ¿Quién aporta? | `ranked_bars`, `pareto`, `treemap`, `sunburst`, `donut` |
| ¿Qué cambió? | `diverging_bars`, `waterfall`, `heatmap(diverging=True)` |
| ¿Dónde? | `choropleth` (geometría inline), `tile_map` (comparable y legible), `n_points` (nativo) |
| ¿Cuándo? | `heatmap` día x hora, `calendar`, `bump` |
| ¿Cumplimos? | `gauge`, `bullet`, `radar`, `funnel` |
| ¿Qué tan disperso? | `boxplot`, `percentile_band`, `scatter`, `n_histogram` |
| Dinero que entra y sale | `inflow_outflow`, `waterfall` sin `kind`, `n_sankey`, `dual_axis` |
| Detalle | `matrix` (jerárquica con barras y píldoras), `n_table` (scroll, orden, descarga) |
| Futuro | `n_forecast` con `AI_FORECAST` |

## Checklist antes de entregar

- [ ] Preview de todas las páginas: no hay FAIL, avisos de "sin filas", gráficas encogidas ni etiquetas cortadas.
- [ ] Los números cuadran entre tarjetas (KPI contra suma del ranking contra tabla) y las variaciones tienen sentido. Los datos sintéticos suelen salir con crecimientos absurdos: ajústalos.
- [ ] Los colores de categoría son consistentes entre páginas.
- [ ] Revisión en el visor real: no hay "Invalid widget", los filtros afectan lo que deben, el cross-filter funciona y el parámetro cambia la vista.
- [ ] Hay snapshot de la versión previa si se actualizó un dashboard existente.
