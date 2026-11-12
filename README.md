# Dashboards AI/BI con visualizaciones Vega-Lite

El paquete trae dos cosas:

1. **01_bi_financiero**: el tablero "BI Financiero · Vistas dinámicas", con datos sintéticos. Sigue la estructura del reporte de Power BI "BI Financiero Vistas" (puente, balanza, presupuesto y auxiliares) y está rehecho en AI/BI con visualizaciones Vega-Lite. Tiene 4 páginas: Resumen, Balanza identada, Balanza extendida y Auxiliares.
2. **02_kit_vega**: un kit en Python para construir tableros propios con el mismo estilo. Trae más de 30 recetas de visualización: tarjetas KPI con sparkline, cascada, treemap, mapa de México por estado, heatmaps, embudo, box plot, matriz jerárquica, gauges y red por capas.

En `01_bi_financiero/capturas/` y en `02_kit_vega/ejemplos/capturas/` están las imágenes de cómo se ven.

## Requisitos en el workspace

- Las visualizaciones personalizadas de AI/BI (custom visualizations, Public Preview) deben estar habilitadas. Un administrador del workspace las activa en **Previews**.
- Un SQL warehouse (serverless o pro) con permiso CAN USE.
- Permiso para crear un esquema en un catálogo de Unity Catalog (`USE CATALOG` y `CREATE SCHEMA`).

## 01. Instalar el tablero BI Financiero (sin CLI)

1. Elegir el catálogo y el esquema de destino, por ejemplo `dev` y `bi_financiero_vega_demo`.
2. Preparar los archivos con una de estas dos opciones:
   - Con Python: `python 01_bi_financiero/preparar.py --catalog dev --schema bi_financiero_vega_demo`. Se generan `setup_datos_listo.sql` y `bi_financiero_listo.lvdash.json`.
   - A mano: en `setup_datos.sql` reemplazar `TU_CATALOGO.TU_ESQUEMA` por `dev.bi_financiero_vega_demo`. En `bi_financiero.lvdash.json` reemplazar `TU_CATALOGO` por `dev` y `TU_ESQUEMA` por `bi_financiero_vega_demo`.
3. Abrir el SQL Editor, pegar el SQL preparado y ejecutarlo completo (**Run all**). Se crean las tablas sintéticas y la metric view `bi_financiero`.
4. En **Dashboards**, abrir la flecha junto a **Create dashboard**, elegir **Import dashboard from file** y subir el `.lvdash.json` preparado.
5. Asignar el warehouse en el tablero y publicar (**Publish**).

Notas sobre el tablero:

- Los datos son sintéticos y no corresponden a cifras reales.
- El selector "Grupo de dimensiones" cambia las filas de la balanza, igual que los parámetros de campo del reporte de Power BI.
- Las medidas se leen de la metric view `bi_financiero`. Así se evita el doble conteo que aparece al unir balanza y presupuesto directamente.
- El saldo inicial es el del primer mes filtrado y el saldo final es el del último mes. No se suman entre meses.

## 02. Usar el kit para tableros propios

Requisitos en la máquina: Python 3.10 o superior, Databricks CLI autenticado contra el workspace (`databricks auth login --profile MI_PERFIL`). Para la vista previa local también se necesitan Node.js y Google Chrome.

1. Leer `guias/design-system.md` (layout, color y composición) y `guias/recipes.md` (catálogo de recetas y qué datos espera cada una).
2. Partir del ejemplo `ejemplos/ejemplo_tpch.py`. Usa `samples.tpch`, que existe en todos los workspaces, y arma 3 páginas con casi todas las recetas:
   - `cd 02_kit_vega/ejemplos && python ejemplo_tpch.py` escribe `out/ejemplo_tpch.lvdash.json`.
   - `python ../scripts/preview.py out/ejemplo_tpch.lvdash.json --profile MI_PERFIL --warehouse ID_WAREHOUSE` genera un PNG por página en `out/preview/`.
   - `python ../scripts/deploy.py out/ejemplo_tpch.lvdash.json --name "Ejemplo TPCH" --profile MI_PERFIL --warehouse ID_WAREHOUSE --parent /Users/mi_usuario/demo` crea y publica el tablero.
3. Para un tablero propio, copiar el ejemplo, cambiar el SQL de los datasets por sus tablas y elegir las recetas.

Reglas que conviene respetar (detalle en `guias/contract-and-pitfalls.md`):

- Cada visualización Vega debe declarar en `fields` todas las columnas que usa.
- Colores en hexadecimal fijo y fechas en UTC.
- Un título o subtítulo largo encoge la gráfica.
- El filtrado cruzado solo funciona en visualizaciones de una sola vista (dona, dispersión).
- Las geometrías de mapas van embebidas (sin `data.url`) y deben pesar menos de ~40 KB. `assets/mx_estados.json` trae los 32 estados de México.
- Cuando el widget nativo luce igual o mejor (Sankey, tabla, pronóstico con AI_FORECAST, histograma, mapa de puntos, heatmap), conviene usar el nativo. `guias/native-widgets.md` lista cuáles funcionan.
