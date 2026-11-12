"""aibi_kit: piezas para generar dashboards AI/BI (Lakeview) visualmente ricos con Vega-Lite + widgets nativos.

Uso típico (ver examples/example_build.py):

    import aibi_kit as k
    k.use_theme("cards", palette="vivid", locale="es")
    ds = k.dataset("ds_v", "Ventas", "SELECT ... FROM t", catalog="c", schema="s")
    w = k.vega("ventas_mes", "ds_v", [k.f("mes"), k.sum_("v", "venta")],
               k.trend_area("Ventas por mes", "Real vs año anterior", x="mes", y="v"))
    g = k.Grid(margin=0)
    g.row(10, (w, 12))
    d = k.dashboard([ds], [k.page("p1", "Resumen", g.items)])
    k.save(d, "out/mi_tablero.lvdash.json")

Reglas de custom-vega-viz (si alguna falla, la gráfica sale en blanco o con "Invalid widget"):
  - spec.version = 1 y spec.jsonSpec.spec es un STRING (json.dumps del spec Vega-Lite)
  - spec.encodings.fields lista cada columna del query que lee el spec
  - dentro del spec la fuente es {"name": "databricks_query"}; sin data.url ni datasets top-level (Vega-Lite v6)
  - colores en hex fijos: dashboardTheme.resolvedFontSettings / widgetBackgroundColor dejan el lienzo en blanco
  - cross-filter (databricks_mark_selection) solo en specs de una sola vista (sin layer)
  - fechas con funciones/timeUnits UTC; si no, los meses se corren un día
Todas las recetas devuelven un dict de Vega-Lite; vega() lo envuelve en el widget.
"""
import json
import math
import os

# ====================================================================== estilo global
PALETTES = {
    # vivo, estilo Power BI moderno
    "vivid": ["#5B7CFA", "#D63A7E", "#F07B3F", "#22A55A", "#F5B83D", "#8E5CF7", "#17B8A6", "#26318A"],
    # corporativo sobrio
    "corporate": ["#1F4E79", "#2E86DE", "#17A2B8", "#E07A5F", "#F2B134", "#7B61FF", "#5B6670", "#0F2B46"],
    # pastel suave
    "soft": ["#7C9CF5", "#F28DB2", "#F6A96B", "#6CC79A", "#F7CF6B", "#B79CF9", "#5FD0C3", "#5562A8"],
}

THEMES = {
    # lienzo gris claro con tarjetas blancas redondeadas (Power BI)
    "cards": {"canvas": "#EEF2F7", "card": "#FFFFFF", "border": "#E2E8F0", "radius": 12,
              "ink": "#0E1A2B", "muted": "#5B6670", "soft": "#8A96A3", "grid": "#EEF1F4", "domain": "#D9DEE3",
              "track": "#EEF1F6", "zebra": "#F8FAFC", "header_bg": "#26318A", "header_sub": "#C9D2F5"},
    # todo blanco: el padding interno de Vega se lee como aire entre gráficas
    "flat": {"canvas": "#FFFFFF", "card": "#FFFFFF", "border": "#FFFFFF", "radius": 0,
             "ink": "#0E1A2B", "muted": "#5B6670", "soft": "#8A96A3", "grid": "#EEF1F4", "domain": "#D9DEE3",
             "track": "#EEF1F6", "zebra": "#F8FAFC", "header_bg": "#0F2B46", "header_sub": "#B9C7D6"},
    # oscuro (los colores de Vega son fijos: el modo oscuro del visor no los cambia)
    "dark": {"canvas": "#0B1020", "card": "#141A2E", "border": "#232B45", "radius": 12,
             "ink": "#E8ECF4", "muted": "#A3AEC2", "soft": "#7F8AA3", "grid": "#232B45", "domain": "#2E3856",
             "track": "#232B45", "zebra": "#182038", "header_bg": "#1C2546", "header_sub": "#A3AEC2"},
}

S = {}            # tokens activos (se llena con use_theme)
PAL = []          # paleta activa
GOOD, BAD = "#1F9D6B", "#D64550"
GOOD_BG, BAD_BG, WARN_BG = "#E3F5EC", "#FBE7E9", "#FDF0D5"
FONT = "Segoe UI, Inter, Helvetica Neue, Arial, sans-serif"
LOCALE = "es"
THEME_NAME = "cards"

_LOCALES = {
    "es": {"number": {"decimal": ".", "thousands": ",", "grouping": [3], "currency": ["$", ""]},
           "time": {"dateTime": "%A, %e de %B de %Y, %X", "date": "%d/%m/%Y", "time": "%H:%M:%S",
                    "periods": ["a. m.", "p. m."],
                    "days": ["domingo", "lunes", "martes", "miércoles", "jueves", "viernes", "sábado"],
                    "shortDays": ["dom", "lun", "mar", "mié", "jue", "vie", "sáb"],
                    "months": ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                               "septiembre", "octubre", "noviembre", "diciembre"],
                    "shortMonths": ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]}},
    "en": {"number": {"decimal": ".", "thousands": ",", "grouping": [3], "currency": ["$", ""]},
           "time": {"dateTime": "%a %b %e %X %Y", "date": "%m/%d/%Y", "time": "%H:%M:%S", "periods": ["AM", "PM"],
                    "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    "shortDays": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                    "months": ["January", "February", "March", "April", "May", "June", "July", "August",
                               "September", "October", "November", "December"],
                    "shortMonths": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]}},
}
# sufijo de miles de millones: "MM" en español financiero, "B" en inglés
_BIG = {"es": "MM", "en": "B"}
TXT = {
    "es": {"vs_prior": "vs año ant.", "vs_prev": "vs mes ant.", "target": "Meta", "current": "Actual",
           "prior": "Año anterior", "ma": "Prom. móvil", "click": "Clic para filtrar", "up": "Aumenta",
           "down": "Disminuye", "total": "Subtotal", "cum": "% acumulado", "of_prev": "de la etapa anterior"},
    "en": {"vs_prior": "vs prior yr", "vs_prev": "vs prior mo", "target": "Target", "current": "Current",
           "prior": "Prior year", "ma": "Moving avg", "click": "Click to filter", "up": "Increase",
           "down": "Decrease", "total": "Subtotal", "cum": "Cumulative %", "of_prev": "of previous stage"},
}


def use_theme(name="cards", palette="vivid", locale="es", font=None, good=None, bad=None, **overrides):
    """Activa tema (cards | flat | dark), paleta (vivid | corporate | soft | lista de hex) y locale (es | en).
    overrides: cualquier token de THEMES (ink, muted, header_bg, ...)."""
    global PAL, LOCALE, THEME_NAME, FONT, GOOD, BAD
    S.clear()
    S.update(THEMES[name])
    S.update(overrides)
    PAL[:] = PALETTES[palette] if isinstance(palette, str) else list(palette)
    LOCALE, THEME_NAME = locale, name
    if font:
        FONT = font
    if good:
        GOOD = good
    if bad:
        BAD = bad


use_theme()


def t(key):
    return TXT[LOCALE][key]


# ====================================================================== formato de números (expresiones Vega)
def fmt_money(field, parens=False, prefix="$", signed=False, decimals=1):
    """$1.2 M / $940.0 K / $2.15 MM; negativos con '-' o entre paréntesis (estilo financiero)."""
    a = f"abs(datum['{field}'])"
    big = _BIG[LOCALE]
    core = (f"({a} >= 1e9 ? format({a} / 1e9, ',.2f') + ' {big}' : "
            f"{a} >= 1e6 ? format({a} / 1e6, ',.{decimals}f') + ' M' : "
            f"{a} >= 1e3 ? format({a} / 1e3, ',.{decimals}f') + ' K' : format({a}, ',.0f'))")
    if parens:
        return (f"datum['{field}'] == null ? '' : (datum['{field}'] < 0 ? '(' + '{prefix}' + {core} + ')' "
                f": '{prefix}' + {core})")
    neg = "'+'" if signed else "''"
    return f"(datum['{field}'] == null ? '' : (datum['{field}'] < 0 ? '-' : {neg}) + '{prefix}' + {core})"


def fmt_short(field, prefix="$"):
    """$589 M / $22.8 M / $940 K: etiquetas compactas para barras densas."""
    a = f"abs(datum['{field}'])"
    big = _BIG[LOCALE]
    core = (f"({a} >= 1e9 ? format({a} / 1e9, ',.1f') + ' {big}' : {a} >= 1e8 ? format({a} / 1e6, ',.0f') + ' M' : "
            f"{a} >= 1e6 ? format({a} / 1e6, ',.1f') + ' M' : {a} >= 1e3 ? format({a} / 1e3, ',.0f') + ' K' : "
            f"format({a}, ',.0f'))")
    return f"(datum['{field}'] == null ? '' : (datum['{field}'] < 0 ? '-{prefix}' : '{prefix}') + {core})"


def fmt_value(field, kind="money"):
    """kind: money | money_exact | pct | int | num."""
    if kind == "money":
        return fmt_money(field)
    if kind == "money_exact":
        return f"'$' + format(datum['{field}'], ',.0f')"
    if kind == "pct":
        return f"format(datum['{field}'], '.1%')"
    if kind == "int":
        return (f"(abs(datum['{field}']) >= 1e6 ? format(datum['{field}'] / 1e6, ',.2f') + ' M' : "
                f"format(datum['{field}'], ',.0f'))")
    return f"format(datum['{field}'], ',.1f')"


def axis_short(prefix=""):
    """labelExpr de eje: 12 M, 940 K."""
    big = _BIG[LOCALE]
    return (f"'{prefix}' + (abs(datum.value) >= 1e9 ? format(datum.value / 1e9, ',.1f') + ' {big}' : "
            f"abs(datum.value) >= 1e6 ? format(datum.value / 1e6, ',.0f') + ' M' : "
            f"abs(datum.value) >= 1e3 ? format(datum.value / 1e3, ',.0f') + ' K' : format(datum.value, ',.0f'))")


def truncate(expr, n=34):
    return f"length({expr}) > {n} ? substring({expr}, 0, {n - 1}) + '…' : {expr}"


# ====================================================================== spec base
def base_config(extra=None):
    c = {
        "autosize": {"type": "fit", "contains": "padding"},
        "background": S["card"],
        "font": FONT,
        "view": {"stroke": None},
        "axis": {"labelColor": S["muted"], "titleColor": S["ink"], "labelFontSize": 11, "titleFontSize": 11.5,
                 "titleFontWeight": 600, "titlePadding": 12, "labelPadding": 6, "gridColor": S["grid"],
                 "domainColor": S["domain"], "tickColor": S["domain"], "labelFont": FONT, "titleFont": FONT},
        "legend": {"labelColor": S["muted"], "titleColor": S["ink"], "labelFontSize": 11, "titleFontSize": 11,
                   "symbolSize": 90, "padding": 6, "rowPadding": 6, "labelFont": FONT, "titleFont": FONT},
        "title": {"font": FONT, "subtitleFont": FONT},
        "text": {"font": FONT, "color": S["ink"]},
        "locale": _LOCALES[LOCALE],
    }
    if extra:
        for key, v in extra.items():
            c[key] = {**c.get(key, {}), **v} if isinstance(v, dict) and isinstance(c.get(key), dict) else v
    return c


def spec(title=None, subtitle=None, pad=(36, 28, 36, 26), title_extra=0, **extra):
    """Spec Vega-Lite responsivo con padding generoso (left, top, right, bottom) y título propio.

    title_extra: px que el título puede exceder el área de trazo. El título se limita a `width + title_extra`
    porque un título/subtítulo más ancho que el trazo hace que autosize fit ENCOJA la gráfica.
    Súbelo cuando la gráfica tiene ejes/etiquetas anchas a la izquierda (barras horizontales)."""
    s = {
        "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
        "data": {"name": "databricks_query"},
        "width": "container", "height": "container",
        "padding": {"left": pad[0], "top": pad[1], "right": pad[2], "bottom": pad[3]},
        "config": base_config(extra.pop("config", None)),
    }
    if title:
        tt = {"text": title, "anchor": "start", "fontSize": 15, "fontWeight": 700, "color": S["ink"], "offset": 18,
              "limit": {"expr": f"width + {title_extra}"}}
        if subtitle:
            tt.update({"subtitle": subtitle, "subtitleFontSize": 11.5, "subtitleColor": S["muted"], "subtitlePadding": 8,
                       "subtitleLimit": {"expr": f"width + {title_extra}"}})
        s["title"] = tt
    s.update(extra)
    return s


def pre(vl, *transforms):
    """Antepone transforms al spec (p. ej. calcular una razón antes de un gauge o un radar).
    Aplica a las capas que heredan los datos; no a capas con su propio `data` (tile_map, choropleth)."""
    vl["transform"] = list(transforms) + vl.get("transform", [])
    return vl


def gradient(color, alpha="66"):
    """Relleno degradado vertical (de la tarjeta al color) para áreas."""
    return {"x1": 1, "y1": 1, "x2": 1, "y2": 0, "gradient": "linear",
            "stops": [{"offset": 0, "color": S["card"]}, {"offset": 1, "color": color + alpha}]}


def full_rule(y_datum, color=None, dash=(4, 4)):
    """Regla horizontal de lado a lado. x/x2 explícitos: si hereda x de una escala de bandas, dibuja una por categoría."""
    return {"mark": {"type": "rule", "color": color or S["soft"], "strokeDash": list(dash)},
            "encoding": {"x": {"value": 0}, "x2": {"value": {"expr": "width"}}, "y": {"datum": y_datum}}}


def color_good_bad(test):
    return {"condition": {"test": test, "value": GOOD}, "value": BAD}


# ====================================================================== widgets (JSON de Lakeview)
def f(name, expr=None):
    """Campo del query del widget. expr = expresión SQL sobre el dataset (por defecto la columna)."""
    return {"name": name, "expression": expr or f"`{name}`"}


def agg(name, fn, col=None):
    """agg('v', 'SUM', 'venta') -> SUM(`venta`) AS v. fn: SUM | AVG | MIN | MAX | COUNT | COUNT_DISTINCT."""
    col = col or name
    if fn.upper() == "COUNT_DISTINCT":
        return f(name, f"COUNT(DISTINCT `{col}`)")
    return f(name, f"{fn.upper()}(`{col}`)")


def sum_(name, col=None):
    return agg(name, "SUM", col)


def avg_(name, col=None):
    return agg(name, "AVG", col)


def vega(name, dataset, fields, vl, disaggregated=False, filters=None):
    """Widget custom-vega-viz. disaggregated=True manda filas sin agrupar (box plot, puntos)."""
    q = {"datasetName": dataset, "fields": fields, "disaggregated": disaggregated}
    if filters:
        q["filters"] = [{"expression": x} for x in filters]
    return {"widget": {
        "name": name,
        "queries": [{"name": "main_query", "query": q}],
        "spec": {"version": 1, "widgetType": "custom-vega-viz",
                 "jsonSpec": {"type": "vega-lite", "spec": json.dumps(vl, ensure_ascii=False)},
                 "encodings": {"fields": [{"fieldName": x["name"]} for x in fields]},
                 "data": {"queryName": "main_query"}},
    }}


def native(name, dataset, fields, spec_body, disaggregated=False):
    return {"widget": {"name": name,
                       "queries": [{"name": "main_query",
                                    "query": {"datasetName": dataset, "fields": fields, "disaggregated": disaggregated}}],
                       "spec": spec_body}}


def text(name, *lines):
    """Widget de texto markdown (también sirve de separador vertical: las filas vacías colapsan)."""
    return {"widget": {"name": name, "multilineTextboxSpec": {"lines": [x + "\n" for x in lines]}}}


# ====================================================================== datasets y parámetros
def dataset(name, display, sql, catalog=None, schema=None, params=None):
    """catalog/schema DENTRO de cada dataset: `lakeview update` borra los defaults del create."""
    d = {"name": name, "displayName": display, "queryLines": [x + "\n" for x in sql.strip("\n").split("\n")]}
    if catalog:
        d["catalog"] = catalog
    if schema:
        d["schema"] = schema
    if params:
        d["parameters"] = params
    return d


def p_string(keyword, default, display=None):
    """Parámetro :keyword de un valor (alimenta CASE/IF en el SQL)."""
    return {"keyword": keyword, "displayName": display or keyword, "dataType": "STRING",
            "defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": default}]}}}


def p_date_range(keyword, dmin, dmax, display=None):
    """Parámetro de rango de fechas: en SQL :keyword.min y :keyword.max."""
    return {"keyword": keyword, "displayName": display or keyword, "dataType": "DATE", "complexType": "RANGE",
            "defaultSelection": {"range": {"dataType": "DATE", "min": {"value": dmin}, "max": {"value": dmax}}}}


# ====================================================================== filtros
def filt(name, title, field, datasets, wtype="filter-multi-select", default=None):
    """Filtro de campo aplicado a varios datasets (una query por dataset).
    wtype: filter-multi-select | filter-single-select | filter-date-range-picker | filter-date-picker"""
    qs, enc = [], []
    for d in datasets:
        qn = f"f_{name}_{d}"
        qs.append({"name": qn, "query": {"datasetName": d, "fields": [f(field)], "disaggregated": False}})
        enc.append({"fieldName": field, "displayName": title, "queryName": qn})
    sp = {"version": 2, "widgetType": wtype, "encodings": {"fields": enc}, "frame": {"showTitle": True, "title": title}}
    if default is not None:
        sp["selection"] = {"defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": v} for v in default]}}}
    return {"widget": {"name": name, "queries": qs, "spec": sp}}


def param_filter(name, title, opts_dataset, opts_field, param, datasets):
    """Selector single-select que alimenta un parámetro de dataset (p. ej. elegir el indicador o la dimensión)."""
    qs = [{"name": f"q_opts_{name}", "query": {"datasetName": opts_dataset, "fields": [f(opts_field)], "disaggregated": False}}]
    enc = [{"fieldName": opts_field, "displayName": title, "queryName": f"q_opts_{name}"}]
    for d in datasets:
        qn = f"q_param_{name}_{d}"
        qs.append({"name": qn, "query": {"datasetName": d, "parameters": [{"name": param, "keyword": param}],
                                         "disaggregated": False}})
        enc.append({"parameterName": param, "queryName": qn})
    return {"widget": {"name": name, "queries": qs,
                       "spec": {"version": 2, "widgetType": "filter-single-select", "encodings": {"fields": enc},
                                "frame": {"showTitle": True, "title": title}}}}


def range_param_filter(name, title, param, datasets):
    """Date range picker atado a un parámetro RANGE (útil para comparar contra el mismo periodo del año anterior)."""
    qs, enc = [], []
    for d in datasets:
        qn = f"q_{name}_{d}"
        qs.append({"name": qn, "query": {"datasetName": d, "parameters": [{"name": param, "keyword": param}],
                                         "disaggregated": False}})
        enc.append({"parameterName": param, "queryName": qn})
    return {"widget": {"name": name, "queries": qs,
                       "spec": {"version": 2, "widgetType": "filter-date-range-picker", "encodings": {"fields": enc},
                                "frame": {"showTitle": True, "title": title}}}}


# ====================================================================== layout
def pos(w, x, y, width, height):
    return {"widget": w["widget"], "position": {"x": x, "y": y, "width": width, "height": height}}


class Grid:
    """Rejilla de 12 columnas con márgenes laterales y avance vertical automático.

        g = Grid(margin=1)              # 1 columna vacía a cada lado (tema flat)
        g.row(3, (banner, 12))          # ancho 12 se recorta al área útil
        g.row(10, (a, 7), (b, 5))       # fila de 10 de alto
        g.row(5, *[(c, 2) for c in kpis])
    Unidades: 1 fila ~ 40-42 px de alto. Las filas vacías se colapsan en el visor: para aire vertical usa
    un text() o un section() alto, no un hueco."""

    def __init__(self, margin=0, cols=12):
        self.margin, self.cols, self.y, self.items = margin, cols, 0, []

    @property
    def usable(self):
        return self.cols - 2 * self.margin

    def row(self, height, *cells):
        x = self.margin
        for w, width in cells:
            width = min(width, self.margin + self.usable - x)
            self.items.append(pos(w, x, self.y, width, height))
            x += width
        self.y += height
        return self

    def full(self, w, height):
        return self.row(height, (w, self.usable))

    def stack(self, x, width, *cells):
        """Columna de widgets apilados que empieza en la fila actual: cells = (widget, alto). No avanza y."""
        y = self.y
        for w, h in cells:
            self.items.append(pos(w, x, y, width, h))
            y += h
        return y

    def advance(self, height):
        self.y += height
        return self


def page(name, display, layout):
    return {"name": name, "displayName": display, "pageType": "PAGE_TYPE_CANVAS", "layoutVersion": "GRID_V1",
            "layout": layout}


def dashboard(datasets, pages, selection_color=None):
    """Dashboard serializado con el tema activo (lienzo, tarjetas, borde, radio, paleta)."""
    th = {
        "canvasBackgroundColor": {"light": S["canvas"], "dark": THEMES["dark"]["canvas"]},
        "widgetBackgroundColor": {"light": S["card"], "dark": THEMES["dark"]["card"]},
        "widgetBorderColor": {"light": S["border"], "dark": THEMES["dark"]["border"]},
        "fontColor": {"light": S["ink"], "dark": THEMES["dark"]["ink"]},
        "selectionColor": {"light": selection_color or PAL[1], "dark": selection_color or PAL[1]},
        "visualizationColors": PAL,
        "widgetHeaderAlignment": "LEFT",
    }
    if S.get("radius"):
        th["widgetCornerRadius"] = S["radius"]
    if THEME_NAME == "dark":
        th["canvasBackgroundColor"]["light"] = S["canvas"]
    return {"datasets": datasets, "pages": pages, "uiSettings": {"theme": th}}


def save(d, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1, ensure_ascii=False)
    n = sum(len(p["layout"]) for p in d["pages"])
    print("OK ->", path, "páginas:", len(d["pages"]), "widgets:", n)
    return path


# ====================================================================== encabezados y tarjetas
def banner(title, subtitle="", right_field=None, right_label="", bg=None, accent=None):
    """Banda de color con título, subtítulo y un dato a la derecha (p. ej. fecha de corte). Alto recomendado 3."""
    bg, accent = bg or S["header_bg"], accent or PAL[1]
    layers = [
        {"mark": {"type": "rect", "color": bg, "cornerRadius": 14},
         "encoding": {"x": {"value": 0}, "x2": {"value": {"expr": "width"}}, "y": {"value": 0},
                      "y2": {"value": {"expr": "height"}}}},
        {"mark": {"type": "rect", "color": accent, "cornerRadius": 3},
         "encoding": {"x": {"value": 28}, "x2": {"value": 34}, "y": {"value": {"expr": "height / 2 - 22"}},
                      "y2": {"value": {"expr": "height / 2 + 22"}}}},
        {"mark": {"type": "text", "align": "left", "baseline": "bottom", "fontSize": 24, "fontWeight": 700, "color": "#FFFFFF"},
         "encoding": {"x": {"value": 50}, "y": {"value": {"expr": "height / 2 + 2"}}, "text": {"value": title}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 12.5, "color": S["header_sub"]},
         "encoding": {"x": {"value": 50}, "y": {"value": {"expr": "height / 2 + 8"}}, "text": {"value": subtitle}}},
    ]
    if right_field:
        layers += [
            {"mark": {"type": "text", "align": "right", "baseline": "bottom", "fontSize": 11, "color": S["header_sub"]},
             "encoding": {"x": {"value": {"expr": "width - 28"}}, "y": {"value": {"expr": "height / 2 - 2"}},
                          "text": {"value": right_label}}},
            {"mark": {"type": "text", "align": "right", "baseline": "top", "fontSize": 15, "fontWeight": 700, "color": "#FFFFFF"},
             "encoding": {"x": {"value": {"expr": "width - 28"}}, "y": {"value": {"expr": "height / 2 + 2"}},
                          "text": {"field": right_field}}},
        ]
    return spec(pad=(0, 0, 0, 0), layer=layers)


def section(title, subtitle="", color=None):
    """Encabezado de sección (barra de acento + título + subtítulo). Alto 2. Sirve de aire vertical."""
    return spec(pad=(4, 0, 4, 0), layer=[
        {"mark": {"type": "rect", "color": color or PAL[0], "cornerRadius": 2},
         "encoding": {"x": {"value": 0}, "x2": {"value": 4}, "y": {"value": {"expr": "height / 2 - 18"}},
                      "y2": {"value": {"expr": "height / 2 + 18"}}}},
        {"mark": {"type": "text", "align": "left", "baseline": "bottom", "fontSize": 17, "fontWeight": 700, "color": S["ink"]},
         "encoding": {"x": {"value": 16}, "y": {"value": {"expr": "height / 2 + 1"}}, "text": {"value": title}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 12, "color": S["muted"]},
         "encoding": {"x": {"value": 16}, "y": {"value": {"expr": "height / 2 + 5"}}, "text": {"value": subtitle}}},
    ])


def kpi_card(title, x, cur, prior=None, cur_den=None, prior_den=None, kind="money", inverse=False, accent=None,
             agg_mode="sum", mom=True, mom_abs=False, note=None, prior_label=None, prev_label=None):
    """Tarjeta KPI: ícono + título, valor grande, delta vs periodo comparable (año ant.) y vs punto previo, sparkline.

    x: columna de periodo (mes/semana) para la sparkline y el delta vs punto previo.
    cur / prior: columnas del valor actual y del comparable. Con cur_den/prior_den el valor es razón (margen, tasa).
    kind: money | money_exact | pct | int. inverse=True: bajar es bueno (gasto, devoluciones).
    agg_mode='mean': valor = promedio de los puntos (p. ej. clientes activos por mes).
    mom_abs: delta vs punto previo en monto absoluto (útil cuando el valor cruza cero).
    note: expresión Vega que reemplaza la primera línea de delta (texto fijo o calculado; usa S_mean = promedio)."""
    accent = accent or PAL[0]
    prior_label, prev_label = prior_label or t("vs_prior"), prev_label or t("vs_prev")
    cols = [cur] + [c for c in (prior, cur_den, prior_den) if c]
    tr = [{"aggregate": [{"op": "sum", "field": c, "as": c} for c in cols], "groupby": [x]},
          {"filter": f"datum['{cur}'] != 0" + (f" || datum['{prior}'] != 0" if prior else "")}]
    ratio = cur_den is not None
    tr.append({"calculate": f"datum['{cur_den}'] == 0 ? null : datum['{cur}'] / datum['{cur_den}']" if ratio
               else f"datum['{cur}']", "as": "s"})
    tr.append({"joinaggregate": [{"op": "sum", "field": c, "as": "T_" + c} for c in cols] +
                                [{"op": "mean", "field": "s", "as": "S_mean"}]})
    if ratio:
        tr.append({"calculate": f"datum['T_{cur_den}'] == 0 ? null : datum['T_{cur}'] / datum['T_{cur_den}']", "as": "val"})
        p = f"(datum['T_{prior}'] / datum['T_{prior_den}'])" if prior and prior_den else None
        rel = (f"datum.val - {p}" if kind == "pct" else f"datum.val / {p} - 1") if p else None
        yoy = f"datum['T_{prior_den}'] == 0 || datum['T_{prior}'] == 0 ? null : {rel}" if rel else "null"
    elif agg_mode == "mean":
        tr.append({"calculate": "datum.S_mean", "as": "val"})
        yoy = "null"
    else:
        tr.append({"calculate": f"datum['T_{cur}']", "as": "val"})
        yoy = f"datum['T_{prior}'] == 0 ? null : datum.val / datum['T_{prior}'] - 1" if prior else "null"
    tr += [{"calculate": yoy, "as": "dy_"},
           {"window": [{"op": "lag", "field": "s", "as": "sprev"}], "sort": [{"field": x}]},
           {"calculate": ("datum.sprev == null ? null : datum.s - datum.sprev" if kind == "pct" or mom_abs else
                          "datum.sprev == null || datum.sprev == 0 ? null : datum.s / datum.sprev - 1"), "as": "dm_"},
           {"window": [{"op": "row_number", "as": "rn"}], "sort": [{"field": x, "order": "descending"}]},
           {"calculate": fmt_value("val", kind), "as": "vtxt"}]
    dfmt = (lambda c: f"format(abs(datum.{c}) * 100, '.1f') + ' pp'") if kind == "pct" else (lambda c: f"format(abs(datum.{c}), '.1%')")
    sign = -1 if inverse else 1
    tr += [
        {"calculate": "datum.dm_ == null ? null : abs(datum.dm_)", "as": "adm"},
        {"calculate": f"datum.dy_ == null ? 0 : (datum.dy_ * {sign} >= 0 ? 1 : -1)", "as": "gy"},
        {"calculate": f"datum.dm_ == null ? 0 : (datum.dm_ * {sign} >= 0 ? 1 : -1)", "as": "gm"},
        {"calculate": f"datum.dy_ == null ? '' : (datum.dy_ >= 0 ? '▲ ' : '▼ ') + {dfmt('dy_')} + ' {prior_label}'", "as": "l1"},
        {"calculate": (f"datum.dm_ == null ? '' : (datum.dm_ >= 0 ? '▲ ' : '▼ ') + {fmt_money('adm')} + ' {prev_label}'"
                       if mom_abs else
                       f"datum.dm_ == null ? '' : (datum.dm_ >= 0 ? '▲ ' : '▼ ') + {dfmt('dm_')} + ' {prev_label}'")
         if mom else "''", "as": "l2"},
        {"joinaggregate": [{"op": "min", "field": "s", "as": "smin"}, {"op": "max", "field": "s", "as": "smax"}]},
        {"calculate": "datum.smax == datum.smin ? 0.5 : (datum.s - datum.smin) / (datum.smax - datum.smin)", "as": "sn"},
    ]
    if note:
        tr.append({"calculate": note, "as": "l1"})
    col = lambda g: {"condition": {"test": f"datum.{g} > 0", "value": GOOD},
                     "value": {"expr": f"datum.{g} < 0 ? '{BAD}' : '{S['soft']}'"}}
    one = {"filter": "datum.rn == 1"}
    X = {"field": x, "type": "temporal", "axis": None}
    # dominio [0, 2.4]: la sparkline ocupa el 40% inferior y deja arriba el texto
    Y = {"field": "sn", "type": "quantitative", "axis": None, "scale": {"domain": [0, 2.4]}}
    return spec(pad=(20, 16, 20, 10), transform=tr, layer=[
        {"mark": {"type": "area", "interpolate": "monotone", "opacity": 0.9, "color": gradient(accent, "55")},
         "encoding": {"x": X, "y": Y}},
        {"mark": {"type": "line", "interpolate": "monotone", "color": accent, "strokeWidth": 2.2}, "encoding": {"x": X, "y": Y}},
        {"mark": {"type": "circle", "color": accent, "size": 40, "stroke": S["card"], "strokeWidth": 1.5},
         "transform": [one], "encoding": {"x": X, "y": Y}},
        {"mark": {"type": "rect", "color": accent, "cornerRadius": 4}, "transform": [one],
         "encoding": {"x": {"value": 0}, "x2": {"value": 26}, "y": {"value": 6}, "y2": {"value": 26}}},
        {"mark": {"type": "text", "align": "center", "baseline": "middle", "fontSize": 12, "color": "#FFFFFF", "fontWeight": 700},
         "transform": [one], "encoding": {"x": {"value": 13}, "y": {"value": 16.5}, "text": {"value": title[0].upper()}}},
        {"mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 12, "fontWeight": 600, "color": S["muted"]},
         "transform": [one], "encoding": {"x": {"value": 34}, "y": {"value": 16}, "text": {"value": title}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 27, "fontWeight": 700, "color": S["ink"]},
         "transform": [one], "encoding": {"x": {"value": 0}, "y": {"value": 34}, "text": {"field": "vtxt"}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 11, "fontWeight": 600},
         "transform": [one], "encoding": {"x": {"value": 0}, "y": {"value": 72}, "text": {"field": "l1"},
                                          "color": {"value": S["muted"]} if note else col("gy")}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 11, "fontWeight": 600},
         "transform": [one], "encoding": {"x": {"value": 0}, "y": {"value": 89}, "text": {"field": "l2"}, "color": col("gm")}},
    ])


def stat_card(title, value_expr, sub_expr="''", accent=None, transforms=None):
    """Tarjeta simple sin serie: valor grande + línea secundaria. value_expr/sub_expr son expresiones Vega
    sobre una fila ya agregada (el query del widget debe devolver 1 fila)."""
    accent = accent or PAL[0]
    tr = list(transforms or []) + [{"calculate": value_expr, "as": "vtxt"}, {"calculate": sub_expr, "as": "sub"}]
    return spec(pad=(22, 16, 22, 12), transform=tr, layer=[
        {"mark": {"type": "rect", "color": accent, "cornerRadius": 4},
         "encoding": {"x": {"value": 0}, "x2": {"value": 26}, "y": {"value": 6}, "y2": {"value": 26}}},
        {"mark": {"type": "text", "align": "center", "baseline": "middle", "fontSize": 12, "color": "#FFFFFF", "fontWeight": 700},
         "encoding": {"x": {"value": 13}, "y": {"value": 16.5}, "text": {"value": title[0].upper()}}},
        {"mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 12, "fontWeight": 600, "color": S["muted"]},
         "encoding": {"x": {"value": 34}, "y": {"value": 16}, "text": {"value": title}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 27, "fontWeight": 700, "color": S["ink"]},
         "encoding": {"x": {"value": 0}, "y": {"value": 34}, "text": {"field": "vtxt"}}},
        {"mark": {"type": "text", "align": "left", "baseline": "top", "fontSize": 11.5, "color": S["muted"]},
         "encoding": {"x": {"value": 0}, "y": {"value": 72}, "text": {"field": "sub"}}},
    ])


def _legend_items(items, step=150):
    """Leyenda manual (rule + texto) arriba del trazo: items = [(label, color, dashed)]."""
    return {"data": {"values": [{"s": s, "c": c, "d": 1 if d else 0} for s, c, d in items]},
            "transform": [{"window": [{"op": "row_number", "as": "i"}]}],
            "layer": [
                {"mark": {"type": "rule", "strokeWidth": 2.5},
                 "encoding": {"x": {"value": {"expr": f"(datum.i - 1) * {step}"}},
                              "x2": {"value": {"expr": f"(datum.i - 1) * {step} + 18"}},
                              "y": {"value": -10}, "color": {"field": "c", "type": "nominal", "scale": None},
                              "strokeDash": {"condition": {"test": "datum.d == 1", "value": [4, 3]}, "value": [1, 0]}}},
                {"mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 11, "color": S["muted"]},
                 "encoding": {"x": {"value": {"expr": f"(datum.i - 1) * {step} + 24"}}, "y": {"value": -10},
                              "text": {"field": "s"}}}]}


# ====================================================================== tendencias
def trend_area(title, subtitle, x, y, prior=None, ma=4, color=None, x_format="%d %b", y_prefix="",
               drop_edges=False, legend=True):
    """Área con degradado + línea del comparable (punteada) + promedio móvil + regla de hover con tooltip.
    drop_edges=True quita el primer y último punto (semanas incompletas)."""
    color = color or PAL[0]
    aggs = [{"op": "sum", "field": y, "as": "cur"}] + ([{"op": "sum", "field": prior, "as": "ant"}] if prior else [])
    tr = [{"aggregate": aggs, "groupby": [x]}, {"filter": "datum.cur != 0"}]
    if drop_edges:
        tr += [{"window": [{"op": "row_number", "as": "ra"}], "sort": [{"field": x}]},
               {"joinaggregate": [{"op": "count", "as": "nw"}]}, {"filter": "datum.ra > 1 && datum.ra < datum.nw"}]
    if ma:
        tr.append({"window": [{"op": "mean", "field": "cur", "as": "mm"}], "frame": [-(ma - 1), 0], "sort": [{"field": x}]})
    tips = [{"field": x, "type": "temporal", "title": "Fecha", "format": "%d %b %Y"},
            {"field": "cur", "title": t("current"), "format": ",.0f"}]
    layers = [{"mark": {"type": "area", "interpolate": "monotone", "line": {"color": color, "strokeWidth": 2.5},
                        "color": gradient(color, "88")},
               "encoding": {"y": {"field": "cur", "type": "quantitative", "title": None,
                                  "axis": {"labelExpr": axis_short(y_prefix), "tickCount": 5}}}}]
    items = [(t("current"), color, False)]
    if prior:
        layers.append({"mark": {"type": "line", "interpolate": "monotone", "strokeDash": [5, 4], "color": "#9AA5B1", "strokeWidth": 2},
                       "encoding": {"y": {"field": "ant", "type": "quantitative"}}})
        tips.append({"field": "ant", "title": t("prior"), "format": ",.0f"})
        items.append((t("prior"), "#9AA5B1", True))
    if ma:
        layers.append({"mark": {"type": "line", "interpolate": "monotone", "color": PAL[1], "strokeWidth": 1.6, "opacity": 0.8},
                       "encoding": {"y": {"field": "mm", "type": "quantitative"}}})
        items.append((f"{t('ma')} {ma}", PAL[1], False))
    layers += [
        {"params": [{"name": "hov", "select": {"type": "point", "on": "pointerover", "nearest": True, "fields": [x],
                                               "clear": "pointerout"}}],
         "mark": {"type": "rule", "strokeWidth": 10, "opacity": 0.001, "tooltip": True}, "encoding": {"tooltip": tips}},
        {"transform": [{"filter": {"param": "hov", "empty": False}}], "mark": {"type": "rule", "color": S["ink"], "strokeDash": [2, 2]}},
    ]
    if legend:
        layers.append(_legend_items(items))
    return spec(title, subtitle, pad=(36, 28, 36, 26), title_extra=50, transform=tr,
                encoding={"x": {"field": x, "type": "temporal", "title": None,
                                "axis": {"format": x_format, "tickCount": 10, "grid": False, "domain": False}}},
                layer=layers, config={"title": {"offset": 28}})


def combo_bars_lines(title, subtitle, x, bar, lines=(), bar_label=None, ratio_label=None, time_unit="utcyearmonth",
                     x_format="%b %y", colors=None):
    """Barras (real) + líneas (meta, año anterior) por periodo; opcional etiqueta de alcance bar/línea sobre la barra.
    lines = [(campo, etiqueta, punteada)]; ratio_label = campo de línea contra el que se calcula el alcance."""
    colors = colors or [PAL[7], PAL[4], "#9AA5B1", PAL[1]]
    bar_label = bar_label or t("current")
    aggs = [{"op": "sum", "field": bar, "as": bar_label}] + [{"op": "sum", "field": c, "as": lab} for c, lab, _ in lines]
    tr = [{"aggregate": aggs, "groupby": [x]}]
    labels = [bar_label] + [lab for _, lab, _ in lines]
    if ratio_label:
        lab = dict((c, l) for c, l, _ in lines)[ratio_label]
        tr.append({"calculate": f"datum['{lab}'] == 0 ? null : datum['{bar_label}'] / datum['{lab}']", "as": "alc"})
    X = {"field": x, "type": "ordinal", "timeUnit": time_unit, "title": None, "axis": {"format": x_format, "labelAngle": 0}}
    layers = [
        {"mark": {"type": "bar", "cornerRadiusTopLeft": 5, "cornerRadiusTopRight": 5, "width": {"band": 0.56}, "tooltip": True},
         "encoding": {"y": {"field": bar_label, "type": "quantitative", "title": None,
                            "axis": {"labelExpr": axis_short(), "tickCount": 5}},
                      "color": {"datum": bar_label, "scale": {"domain": labels, "range": colors[:len(labels)]},
                                "legend": {"orient": "top", "direction": "horizontal", "title": None}},
                      "tooltip": [{"field": x, "timeUnit": time_unit, "title": "Periodo", "format": "%b %Y"}] +
                                 [{"field": lab, "format": ",.0f"} for lab in labels] +
                                 ([{"field": "alc", "title": "Alcance", "format": ".1%"}] if ratio_label else [])}}]
    if lines:
        line_labels = [lab for _, lab, _ in lines]
        dashes = [[6, 4] if d else [1, 0] for _, _, d in lines]
        layers.append({"transform": [{"fold": line_labels, "as": ["serie", "val"]}, {"filter": "datum.val != null"}],
                       "mark": {"type": "line", "interpolate": "monotone", "strokeWidth": 2.5, "point": {"filled": True, "size": 40}},
                       "encoding": {"y": {"field": "val", "type": "quantitative"},
                                    "color": {"field": "serie", "type": "nominal", "title": None},
                                    "strokeDash": {"field": "serie", "type": "nominal", "legend": None,
                                                   "scale": {"domain": line_labels, "range": dashes}}}})
    if ratio_label:
        layers.append({"mark": {"type": "text", "dy": -10, "fontSize": 10, "fontWeight": 700},
                       "encoding": {"y": {"field": bar_label, "type": "quantitative"}, "text": {"field": "alc", "format": ".0%"},
                                    "color": color_good_bad("datum.alc >= 1")}})
    return spec(title, subtitle, title_extra=50, transform=tr, encoding={"x": X}, layer=layers)


def dual_axis(title, subtitle, x, left, right, left_title, right_title, left_color=None, right_color=None,
              x_format="%b %y", left_prefix=""):
    """Área (eje izquierdo) + línea (eje derecho) con escalas independientes y títulos de eje en el color de su serie."""
    lc, rc = left_color or PAL[0], right_color or PAL[1]
    return spec(title, subtitle, pad=(32, 28, 32, 22), title_extra=100,
                transform=[{"aggregate": [{"op": "sum", "field": left, "as": "l"}, {"op": "sum", "field": right, "as": "r"}],
                            "groupby": [x]}],
                encoding={"x": {"field": x, "type": "temporal", "title": None, "axis": {"format": x_format, "grid": False, "domain": False}}},
                layer=[
                    {"mark": {"type": "area", "interpolate": "monotone", "line": {"color": lc, "strokeWidth": 2}, "color": gradient(lc, "77")},
                     "encoding": {"y": {"field": "l", "type": "quantitative", "title": left_title, "scale": {"zero": False},
                                        "axis": {"labelExpr": axis_short(left_prefix), "titleColor": lc}}}},
                    {"mark": {"type": "line", "interpolate": "monotone", "color": rc, "strokeWidth": 2},
                     "encoding": {"y": {"field": "r", "type": "quantitative", "title": right_title,
                                        "axis": {"orient": "right", "grid": False, "titleColor": rc}}}},
                ], resolve={"scale": {"y": "independent"}})


def percentile_band(title, subtitle, x, lo, mid, hi, weight=None, ref=None, ref_label="", color=None, y_title=None):
    """Mediana (línea) + rango p10-p90 (banda). weight: columna de conteo para promediar ponderado al re-agregar."""
    color = color or PAL[5]
    if weight:
        tr = [{"calculate": f"datum['{weight}'] * datum['{c}']", "as": "w_" + c} for c in (lo, mid, hi)]
        tr += [{"aggregate": [{"op": "sum", "field": c, "as": c} for c in [weight] + ["w_" + c for c in (lo, mid, hi)]], "groupby": [x]}]
        tr += [{"calculate": f"datum['w_{c}'] / datum['{weight}']", "as": k} for c, k in ((lo, "plo"), (mid, "pmid"), (hi, "phi"))]
    else:
        tr = [{"aggregate": [{"op": "mean", "field": c, "as": k} for c, k in ((lo, "plo"), (mid, "pmid"), (hi, "phi"))], "groupby": [x]}]
    layers = [
        {"mark": {"type": "area", "interpolate": "monotone", "color": color, "opacity": 0.16},
         "encoding": {"y": {"field": "plo", "type": "quantitative", "title": y_title}, "y2": {"field": "phi"}}},
        {"mark": {"type": "line", "interpolate": "monotone", "color": color, "strokeWidth": 2.5},
         "encoding": {"y": {"field": "pmid", "type": "quantitative"},
                      "tooltip": [{"field": x, "type": "temporal", "format": "%d %b %Y"},
                                  {"field": "pmid", "title": "p50", "format": ".1f"}, {"field": "phi", "title": "p90", "format": ".1f"}]}},
    ]
    if ref is not None:
        layers += [full_rule(ref, PAL[1], (5, 4)),
                   {"mark": {"type": "text", "align": "right", "dy": -7, "color": PAL[1], "fontSize": 10.5, "fontWeight": 700},
                    "encoding": {"x": {"value": {"expr": "width"}}, "y": {"datum": ref}, "text": {"value": ref_label}}}]
    return spec(title, subtitle, pad=(32, 28, 32, 22), title_extra=50, transform=tr,
                encoding={"x": {"field": x, "type": "temporal", "title": None, "axis": {"format": "%b %y", "grid": False}}},
                layer=layers)


def bump(title, subtitle, x, cat, val, time_unit="utcyearmonth", x_format="%b %y"):
    """Bump chart: posición de cada categoría por periodo, con etiqueta al final. Deja pad derecho para nombres."""
    return spec(title, subtitle, pad=(28, 28, 130, 24),
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [x, cat]},
                           {"filter": "datum.v > 0"},
                           {"window": [{"op": "rank", "as": "rk"}], "groupby": [x], "sort": [{"field": "v", "order": "descending"}]},
                           {"joinaggregate": [{"op": "max", "field": x, "as": "mx"}]}],
                encoding={"x": {"field": x, "type": "temporal", "timeUnit": time_unit, "title": None,
                                "axis": {"format": x_format, "grid": False, "domain": False, "ticks": False}},
                          "y": {"field": "rk", "type": "ordinal", "title": None,
                                "axis": {"labelExpr": "'#' + datum.label", "domain": False, "ticks": False}},
                          "color": {"field": cat, "type": "nominal", "legend": None, "scale": {"range": PAL + ["#9AA5B1", "#2E3A59"]}}},
                layer=[
                    {"mark": {"type": "line", "interpolate": "monotone", "strokeWidth": 3, "opacity": 0.85}},
                    {"mark": {"type": "circle", "size": 120, "opacity": 1, "stroke": S["card"], "strokeWidth": 2, "tooltip": True},
                     "encoding": {"tooltip": [{"field": cat}, {"field": x, "type": "temporal", "timeUnit": time_unit, "format": "%b %Y"},
                                              {"field": "rk", "title": "#"}, {"field": "v", "format": ",.0f"}]}},
                    {"transform": [{"filter": f"datum['{x}'] == datum.mx"}],
                     "mark": {"type": "text", "align": "left", "dx": 12, "fontSize": 11, "fontWeight": 700},
                     "encoding": {"text": {"field": cat}}},
                ])


def stacked_share(title, subtitle, x, cat, val, time_unit="utcyearmonth", normalize=True, colors=None):
    """Barras apiladas por periodo (100% si normalize)."""
    return spec(title, subtitle, title_extra=40,
                mark={"type": "bar", "tooltip": True, "cornerRadius": 2},
                encoding={"x": {"field": x, "type": "ordinal", "timeUnit": time_unit, "title": None,
                                "axis": {"format": "%b %y", "labelAngle": 0}},
                          "y": {"field": val, "aggregate": "sum", "type": "quantitative", "title": None,
                                "stack": "normalize" if normalize else "zero",
                                "axis": {"format": "%"} if normalize else {"labelExpr": axis_short()}},
                          "color": {"field": cat, "type": "nominal", "title": None, "scale": {"range": colors or PAL},
                                    "legend": {"orient": "top", "direction": "horizontal", "columns": 4}},
                          "tooltip": [{"field": cat}, {"field": val, "aggregate": "sum", "format": ",.0f"}]})


def inflow_outflow(title, subtitle, x, inflow, outflow, in_label="Entradas", out_label="Salidas", net_label="Neto",
                   time_unit="utcyearmonth"):
    """Entradas arriba, salidas abajo (barras divergentes) y la línea del neto. outflow viene en positivo."""
    return spec(title, subtitle, pad=(32, 28, 32, 24), title_extra=50,
                transform=[{"aggregate": [{"op": "sum", "field": inflow, "as": in_label}, {"op": "sum", "field": outflow, "as": "s_"}],
                            "groupby": [x]},
                           {"calculate": "-datum.s_", "as": out_label},
                           {"calculate": f"datum['{in_label}'] - datum.s_", "as": "neto"}],
                encoding={"x": {"field": x, "type": "ordinal", "timeUnit": time_unit, "title": None,
                                "axis": {"format": "%b %y", "labelAngle": 0, "domain": False, "ticks": False}}},
                layer=[
                    {"transform": [{"fold": [in_label, out_label], "as": ["tipo", "val"]}],
                     "mark": {"type": "bar", "width": {"band": 0.62}, "cornerRadius": 4, "tooltip": True},
                     "encoding": {"y": {"field": "val", "type": "quantitative", "stack": None, "title": None,
                                        "axis": {"labelExpr": axis_short(), "tickCount": 6}},
                                  "color": {"field": "tipo", "type": "nominal", "title": None,
                                            "scale": {"domain": [in_label, out_label, net_label], "range": [GOOD, PAL[1], PAL[7]]},
                                            "legend": {"orient": "top", "direction": "horizontal"}},
                                  "tooltip": [{"field": x, "type": "temporal", "timeUnit": time_unit, "format": "%b %Y"},
                                              {"field": "tipo"}, {"field": "val", "format": "$,.0f"}]}},
                    {"mark": {"type": "rule", "color": "#9AA5B1"}, "encoding": {"y": {"datum": 0}}},
                    {"mark": {"type": "line", "color": PAL[7], "strokeWidth": 2.5, "interpolate": "monotone",
                              "point": {"filled": True, "size": 50, "color": PAL[7]}},
                     "encoding": {"y": {"field": "neto", "type": "quantitative"}, "color": {"datum": net_label}}},
                ])


# ====================================================================== composición y ranking
def donut(title, subtitle, cat, val, domain=None, colors=None, cross_filter=True, fmt="$,.0f"):
    """Dona. Con cross_filter=True, clic en un segmento filtra los demás widgets del mismo dataset (vista única)."""
    enc = {"theta": {"field": val, "type": "quantitative", "stack": True, "aggregate": "sum"},
           "color": {"field": cat, "type": "nominal", "title": None,
                     "scale": {"domain": domain, "range": colors} if domain else {"range": colors or PAL},
                     "legend": {"orient": "bottom", "direction": "horizontal", "columns": 2, "labelFontSize": 11.5}},
           "order": {"field": val, "aggregate": "sum", "sort": "descending"},
           "tooltip": [{"field": cat}, {"field": val, "aggregate": "sum", "format": fmt}]}
    extra = {}
    if cross_filter:
        extra["params"] = [{"name": "databricks_mark_selection", "select": {"type": "point", "fields": [cat]}}]
        enc["opacity"] = {"condition": {"param": "databricks_mark_selection", "empty": True, "value": 1}, "value": 0.3}
    return spec(title, subtitle, pad=(24, 28, 24, 20),
                mark={"type": "arc", "innerRadius": {"expr": "min(width, height) * 0.27"},
                      "outerRadius": {"expr": "min(width, height) * 0.45"}, "padAngle": 0.015, "cornerRadius": 5,
                      "tooltip": True, "cursor": "pointer", "stroke": S["card"], "strokeWidth": 2},
                encoding=enc, **extra)


def ranked_bars(title, subtitle, cat, val, top=10, color_field=None, color_domain=None, colors=None, sqrt=False,
                label_kind="short", title_extra=170):
    """Top N horizontal con etiqueta de valor. La clave rango|nombre conserva el orden en specs con capas
    (el sort por campo se pierde al unir dominios)."""
    groupby = [cat] + ([color_field] if color_field else [])
    lab = fmt_short("v") if label_kind == "short" else fmt_value("v", label_kind)
    color = ({"field": color_field, "type": "nominal", "title": None,
              "scale": {"domain": color_domain, "range": colors or PAL} if color_domain else {"range": colors or PAL},
              "legend": {"orient": "top", "direction": "horizontal"}} if color_field else {"value": PAL[0]})
    return spec(title, subtitle, pad=(24, 28, 56, 22), title_extra=title_extra,
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": groupby},
                           {"window": [{"op": "row_number", "as": "rk"}], "sort": [{"field": "v", "order": "descending"}]},
                           {"filter": f"datum.rk <= {top}"},
                           {"calculate": f"pad(toString(datum.rk), 2, '0', 'left') + '|' + datum['{cat}']", "as": "yk"},
                           {"calculate": lab, "as": "txt"}],
                encoding={"y": {"field": "yk", "type": "nominal", "sort": "ascending", "title": None,
                                "axis": {"labelExpr": "split(datum.label, '|')[1]", "labelLimit": 160, "domain": False, "ticks": False}}},
                layer=[{"mark": {"type": "bar", "cornerRadiusEnd": 5, "height": {"band": 0.62}, "tooltip": True},
                        "encoding": {"x": {"field": "v", "type": "quantitative", "axis": None, "title": None,
                                           "scale": {"type": "sqrt"} if sqrt else {}},
                                     "color": color, "tooltip": [{"field": cat}, {"field": "txt", "title": "Valor"}]}},
                       {"mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 10.5, "fontWeight": 700, "color": S["ink"]},
                        "encoding": {"x": {"field": "v", "type": "quantitative"}, "text": {"field": "txt"}}}])


def diverging_bars(title, subtitle, cat, val, top=14, positive_is_good=True, title_extra=200):
    """Variaciones +/- por elemento (top N por magnitud), verde favorable y rojo desfavorable, etiqueta a la derecha."""
    sign = "" if positive_is_good else "-"
    return spec(title, subtitle, pad=(24, 28, 28, 26), title_extra=title_extra,
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "raw"}], "groupby": [cat]},
                           {"calculate": f"{sign}datum.raw", "as": "var"},
                           {"calculate": "abs(datum.var)", "as": "av"},
                           {"window": [{"op": "row_number", "as": "rk"}], "sort": [{"field": "av", "order": "descending"}]},
                           {"filter": f"datum.rk <= {top}"},
                           {"calculate": truncate(f"datum['{cat}']", 30), "as": "lab"},
                           {"calculate": fmt_money("var", signed=True), "as": "txt"}],
                encoding={"y": {"field": "lab", "type": "nominal", "sort": {"field": "var", "order": "descending"}, "title": None,
                                "axis": {"labelLimit": 190, "domain": False, "ticks": False, "labelPadding": 8}}},
                layer=[
                    {"mark": {"type": "bar", "cornerRadius": 4, "height": {"band": 0.62}, "tooltip": True},
                     "encoding": {"x": {"field": "var", "type": "quantitative", "title": None, "scale": {"padding": 66},
                                        "axis": {"labelExpr": axis_short(), "tickCount": 3, "grid": True}},
                                  "color": color_good_bad("datum.var >= 0"),
                                  "tooltip": [{"field": "lab", "title": "Elemento"}, {"field": "var", "title": "Var", "format": "$,.0f"}]}},
                    {"mark": {"type": "rule", "color": "#9AA5B1", "strokeWidth": 1.2}, "encoding": {"x": {"datum": 0}}},
                    {"mark": {"type": "text", "fontSize": 10.5, "fontWeight": 700, "align": "right", "baseline": "middle"},
                     "encoding": {"x": {"value": {"expr": "width + 4"}}, "text": {"field": "txt"}, "color": color_good_bad("datum.var >= 0")}},
                ])


def waterfall(title, subtitle, step, order, val, kind=None, colors=None, label_angle=0):
    """Cascada / puente. kind: columna con 'delta' o 'total' (los subtotales los calcula el SQL como filas aparte).
    Sin kind: todo son deltas (puente de flujo). Etiquetas largas: usa nombres cortos en `step`."""
    up, down, tot = colors or (GOOD, BAD, PAL[7])
    kind_expr = f"datum['{kind}']" if kind else "'delta'"
    return spec(title, subtitle, pad=(30, 28, 30, 22),
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [order, step] + ([kind] if kind else [])},
                           {"calculate": kind_expr, "as": "k_"},
                           {"calculate": "datum.k_ == 'delta' ? datum.v : 0", "as": "dv"},
                           {"window": [{"op": "sum", "field": "dv", "as": "run"}], "sort": [{"field": order}], "frame": [None, 0]},
                           {"calculate": "datum.k_ == 'total' ? 0 : datum.run - datum.v", "as": "y0"},
                           {"calculate": "datum.k_ == 'total' ? datum.v : datum.run", "as": "y1"},
                           {"calculate": f"datum.k_ == 'total' ? '{t('total')}' : datum.v >= 0 ? '{t('up')}' : '{t('down')}'", "as": "clase"},
                           {"calculate": fmt_short("v"), "as": "txt"},
                           {"calculate": "max(datum.y0, datum.y1)", "as": "ytop"}],
                encoding={"x": {"field": step, "type": "nominal", "sort": {"field": order}, "title": None,
                                "axis": {"labelAngle": label_angle, "labelLimit": 110, "labelFontSize": 10.5, "labelPadding": 8,
                                         "labelExpr": "split(datum.label, ' ')" if label_angle == 0 else "datum.label",
                                         "domain": False, "ticks": False}}},
                layer=[
                    {"mark": {"type": "bar", "cornerRadius": 4, "width": {"band": 0.66}, "tooltip": True},
                     "encoding": {"y": {"field": "y0", "type": "quantitative", "title": None,
                                        "axis": {"labelExpr": axis_short(), "tickCount": 5}},
                                  "y2": {"field": "y1"},
                                  "color": {"field": "clase", "type": "nominal", "title": None,
                                            "scale": {"domain": [t("up"), t("down"), t("total")], "range": [up, down, tot]},
                                            "legend": {"orient": "top", "direction": "horizontal", "offset": 4}},
                                  "tooltip": [{"field": step}, {"field": "v", "format": "$,.0f"}]}},
                    {"mark": {"type": "text", "dy": -8, "fontSize": 10.5, "fontWeight": 700, "color": S["ink"]},
                     "encoding": {"y": {"field": "ytop", "type": "quantitative"}, "text": {"field": "txt"}}},
                ])


def pareto(title, subtitle, cat, val, threshold=0.8, color=None, line_color=None, label_angle=-45):
    """Barras ordenadas + % acumulado en eje derecho + regla del umbral (80/20)."""
    c, lc = color or PAL[0], line_color or PAL[1]
    return spec(title, subtitle, pad=(30, 28, 30, 22), title_extra=60,
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [cat]},
                           {"window": [{"op": "sum", "field": "v", "as": "cum"}, {"op": "row_number", "as": "rk"}],
                            "sort": [{"field": "v", "order": "descending"}], "frame": [None, 0]},
                           {"joinaggregate": [{"op": "sum", "field": "v", "as": "tot"}]},
                           {"calculate": "datum.cum / datum.tot", "as": "pc"},
                           {"calculate": fmt_short("v"), "as": "txt"}],
                encoding={"x": {"field": cat, "type": "nominal", "sort": {"field": "rk"}, "title": None,
                                "axis": {"labelAngle": label_angle, "labelLimit": 110, "labelFontSize": 10, "labelOverlap": "greedy",
                                         "domain": False, "ticks": False}}},
                layer=[
                    {"mark": {"type": "bar", "cornerRadiusTopLeft": 5, "cornerRadiusTopRight": 5, "width": {"band": 0.62}, "tooltip": True},
                     "encoding": {"y": {"field": "v", "type": "quantitative", "title": None, "axis": {"labelExpr": axis_short(), "tickCount": 4}},
                                  "color": {"condition": {"test": f"datum.pc <= {threshold} || datum.rk == 1", "value": c}, "value": "#C7D2FE"},
                                  "tooltip": [{"field": cat}, {"field": "txt", "title": "Valor"},
                                              {"field": "pc", "title": t("cum"), "format": ".1%"}]}},
                    {"layer": [
                        {"mark": {"type": "line", "color": lc, "strokeWidth": 2.5, "point": {"color": lc, "size": 40, "filled": True}},
                         "encoding": {"y": {"field": "pc", "type": "quantitative", "title": None, "scale": {"domain": [0, 1]},
                                            "axis": {"format": "%", "orient": "right", "grid": False}}}},
                        {"mark": {"type": "rule", "color": lc, "strokeDash": [4, 4], "opacity": 0.6},
                         "encoding": {"x": {"value": 0}, "x2": {"value": {"expr": "width"}}, "y": {"datum": threshold, "type": "quantitative"}}},
                    ]},
                ], resolve={"scale": {"y": "independent"}})


def treemap(title, subtitle, l1, l2, val, colors=None, fmt="short"):
    """Treemap slice-and-dice calculado en Vega-Lite: ancho = nivel 1, alto = nivel 2 dentro de cada columna."""
    lab = fmt_short("v") if fmt == "short" else fmt_value("v", fmt)
    return spec(title, subtitle, pad=(24, 28, 24, 20),
                transform=[
                    {"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [l1, l2]},
                    {"filter": "datum.v > 0"},
                    {"joinaggregate": [{"op": "sum", "field": "v", "as": "vc"}], "groupby": [l1]},
                    {"joinaggregate": [{"op": "sum", "field": "v", "as": "vt"}]},
                    {"window": [{"op": "sum", "field": "v", "as": "run"}],
                     "sort": [{"field": "vc", "order": "descending"}, {"field": l1}, {"field": "v", "order": "descending"}],
                     "frame": [None, 0]},
                    {"joinaggregate": [{"op": "max", "field": "run", "as": "cx1"}], "groupby": [l1]},
                    {"calculate": "(datum.cx1 - datum.vc) / datum.vt", "as": "x0"},
                    {"calculate": "datum.cx1 / datum.vt", "as": "x1"},
                    {"window": [{"op": "sum", "field": "v", "as": "runc"}], "groupby": [l1],
                     "sort": [{"field": "v", "order": "descending"}], "frame": [None, 0]},
                    {"calculate": "(datum.runc - datum.v) / datum.vc", "as": "y0"},
                    {"calculate": "datum.runc / datum.vc", "as": "y1"},
                    {"calculate": lab, "as": "txt"},
                    {"calculate": "datum.v / datum.vt", "as": "share"},
                ],
                encoding={"x": {"field": "x0", "type": "quantitative", "axis": None, "scale": {"domain": [0, 1], "nice": False}},
                          "y": {"field": "y0", "type": "quantitative", "axis": None, "scale": {"domain": [1, 0], "nice": False}}},
                layer=[
                    {"mark": {"type": "rect", "stroke": S["card"], "strokeWidth": 3, "cornerRadius": 3, "tooltip": True},
                     "encoding": {"x2": {"field": "x1"}, "y2": {"field": "y1"},
                                  "color": {"field": l1, "type": "nominal", "title": None, "scale": {"range": colors or PAL},
                                            "legend": {"orient": "bottom", "columns": 3, "labelLimit": 220, "columnPadding": 24}},
                                  "opacity": {"field": "y0", "type": "quantitative", "scale": {"domain": [0, 1], "range": [1, 0.62]}, "legend": None},
                                  "tooltip": [{"field": l1}, {"field": l2}, {"field": "txt", "title": "Valor"},
                                              {"field": "share", "title": "%", "format": ".1%"}]}},
                    {"transform": [{"filter": "datum.x1 - datum.x0 > 0.12 && datum.y1 - datum.y0 > 0.1"}],
                     "mark": {"type": "text", "align": "left", "baseline": "top", "dx": 8, "dy": 8, "fontSize": 11, "fontWeight": 700,
                              "color": "#FFFFFF", "limit": 120},
                     "encoding": {"text": {"field": l2}}},
                    {"transform": [{"filter": "datum.x1 - datum.x0 > 0.12 && datum.y1 - datum.y0 > 0.1"}],
                     "mark": {"type": "text", "align": "left", "baseline": "top", "dx": 8, "dy": 23, "fontSize": 10.5, "color": "#FFFFFFDD"},
                     "encoding": {"text": {"field": "txt"}}},
                ])


def sunburst(title, subtitle, inner, outer, val, colors=None):
    """Sunburst de 2 anillos: interior = nivel 1, exterior = nivel 2 (mismo color con opacidad)."""
    return spec(title, subtitle, pad=(20, 28, 20, 18),
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [inner, outer]},
                           {"joinaggregate": [{"op": "sum", "field": "v", "as": "vt"}], "groupby": [inner]},
                           {"window": [{"op": "dense_rank", "as": "ti"}], "sort": [{"field": "vt", "order": "descending"}]},
                           {"calculate": f"pad(toString(datum.ti), 2, '0', 'left') + datum['{outer}']", "as": "k2"}],
                layer=[
                    {"transform": [{"aggregate": [{"op": "sum", "field": "v", "as": "v"}], "groupby": [inner, "ti"]}],
                     "mark": {"type": "arc", "innerRadius": {"expr": "min(width, height) * 0.14"},
                              "outerRadius": {"expr": "min(width, height) * 0.30"}, "stroke": S["card"], "strokeWidth": 2, "tooltip": True},
                     "encoding": {"theta": {"field": "v", "type": "quantitative", "stack": True},
                                  "order": {"field": "ti"},
                                  "color": {"field": inner, "type": "nominal", "title": None, "scale": {"range": colors or PAL},
                                            "legend": {"orient": "bottom", "columns": 2, "labelFontSize": 11}},
                                  "tooltip": [{"field": inner}, {"field": "v", "format": ",.0f"}]}},
                    {"mark": {"type": "arc", "innerRadius": {"expr": "min(width, height) * 0.31"},
                              "outerRadius": {"expr": "min(width, height) * 0.46"}, "stroke": S["card"], "strokeWidth": 1.5, "tooltip": True},
                     "encoding": {"theta": {"field": "v", "type": "quantitative", "stack": True},
                                  "order": {"field": "k2"},
                                  "color": {"field": inner, "type": "nominal"},
                                  "opacity": {"value": 0.62},
                                  "tooltip": [{"field": inner}, {"field": outer}, {"field": "v", "format": ",.0f"}]}},
                ])


# ====================================================================== matrices de calor
def heatmap(title, subtitle, x, y, val, x_type="ordinal", y_type="ordinal", colors=None, diverging=False,
            labels=False, label_fmt=",.0f", x_label_expr=None, y_label_expr=None, x_time_unit=None, y_sort=None,
            legend_fmt=None, agg_op="sum", title_extra=60):
    """Heatmap genérico (día x hora, elemento x mes, etc.). diverging=True: escala symlog centrada en 0 (rojo/verde)."""
    if diverging:
        scale = {"type": "symlog", "domainMid": 0, "range": [BAD, "#F7F7F5", GOOD]}
    else:
        scale = {"range": colors or ["#EEF2FF", "#A5B4FC", PAL[0], PAL[7]]}
    xa = {"labelAngle": 0, "domain": False, "ticks": False}
    if x_label_expr:
        xa["labelExpr"] = x_label_expr
    if x_time_unit:
        xa["format"] = "%b %y"
    ya = {"domain": False, "ticks": False, "labelLimit": 200}
    if y_label_expr:
        ya["labelExpr"] = y_label_expr
    X = {"field": x, "type": x_type, "title": None, "axis": xa}
    if x_time_unit:
        X["timeUnit"] = x_time_unit
    Y = {"field": y, "type": y_type, "title": None, "axis": ya}
    if y_sort:
        Y["sort"] = y_sort
    leg = {"orient": "right", "gradientLength": 140}
    if legend_fmt:
        leg["labelExpr"] = legend_fmt
    layers = [{"mark": {"type": "rect", "cornerRadius": 4, "stroke": S["card"], "strokeWidth": 2.5, "tooltip": True},
               "encoding": {"color": {"field": "v", "type": "quantitative", "title": None, "scale": scale, "legend": leg},
                            "tooltip": [{"field": x, **({"timeUnit": x_time_unit, "format": "%b %Y"} if x_time_unit else {})},
                                        {"field": y}, {"field": "v", "title": "Valor", "format": label_fmt}]}}]
    if labels:
        layers.append({"mark": {"type": "text", "fontSize": 9.5, "fontWeight": 600},
                       "encoding": {"text": {"field": "v", "format": label_fmt},
                                    "color": {"condition": {"test": "datum.v > datum.vmin + (datum.vmax - datum.vmin) * 0.6", "value": "#FFFFFF"},
                                              "value": S["ink"]}}})
    tr = [{"aggregate": [{"op": agg_op, "field": val, "as": "v"}], "groupby": [x, y]},
          {"joinaggregate": [{"op": "max", "field": "v", "as": "vmax"}, {"op": "min", "field": "v", "as": "vmin"}]}]
    return spec(title, subtitle, pad=(28, 28, 28, 22), title_extra=title_extra, transform=tr,
                encoding={"x": X, "y": Y}, layer=layers)


def cohort(title, subtitle, cohort_field, n_field, active, domain=(0.5, 1.0), colors=None):
    """Retención por cohorte: % de la cohorte (mes 0) que sigue activa en el mes N, con etiqueta en cada celda.
    cohort_field en formato 'yyyy-MM'; n_field entero (meses desde el alta)."""
    return spec(title, subtitle, pad=(28, 28, 28, 22), title_extra=90,
                transform=[{"aggregate": [{"op": "sum", "field": active, "as": "a"}], "groupby": [cohort_field, n_field]},
                           {"joinaggregate": [{"op": "max", "field": "a", "as": "n0"}], "groupby": [cohort_field]},
                           {"calculate": "datum.a / datum.n0", "as": "ret"}],
                encoding={"x": {"field": n_field, "type": "ordinal", "title": None,
                                "axis": {"orient": "top", "labelAngle": 0, "domain": False, "ticks": False, "labelExpr": "'M' + datum.label"}},
                          "y": {"field": cohort_field, "type": "ordinal", "title": None,
                                "axis": {"domain": False, "ticks": False, "labelExpr": "timeFormat(toDate(datum.label + '-02'), '%b %Y')"}}},
                layer=[
                    {"mark": {"type": "rect", "cornerRadius": 3, "stroke": S["card"], "strokeWidth": 2, "tooltip": True},
                     "encoding": {"color": {"field": "ret", "type": "quantitative", "title": None,
                                            "scale": {"domain": list(domain), "range": colors or ["#FDE7EF", "#F49AB9", PAL[1], "#7A1E48"], "clamp": True},
                                            "legend": {"format": ".0%", "orient": "right", "gradientLength": 160}},
                                  "tooltip": [{"field": cohort_field}, {"field": n_field}, {"field": "a", "title": "Activos"},
                                              {"field": "ret", "title": "%", "format": ".0%"}]}},
                    {"mark": {"type": "text", "fontSize": 9.5, "fontWeight": 600},
                     "encoding": {"text": {"field": "ret", "format": ".0%"},
                                  "color": {"condition": {"test": f"datum.ret > {domain[0] + (domain[1] - domain[0]) * 0.6}", "value": "#FFFFFF"},
                                            "value": S["ink"]}}},
                ])


def calendar(title, subtitle, date, val, colors=None, value_fmt=None):
    """Calendario tipo GitHub: columnas = semanas (lunes), filas = día de la semana."""
    days = "['', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']" if LOCALE == "es" else "['', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']"
    return spec(title, subtitle, pad=(28, 28, 36, 24),
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [date]},
                           {"calculate": f"toDate(datum['{date}'])", "as": "fd"},
                           {"calculate": "utcday(datum.fd) == 0 ? 7 : utcday(datum.fd)", "as": "dow"},
                           {"calculate": "utc(utcyear(datum.fd), utcmonth(datum.fd), utcdate(datum.fd) - datum.dow + 1)", "as": "wk"},
                           {"calculate": value_fmt or fmt_money("v"), "as": "txt"}],
                mark={"type": "rect", "cornerRadius": 3, "stroke": S["card"], "strokeWidth": 2, "tooltip": True},
                encoding={"x": {"field": "wk", "type": "ordinal", "timeUnit": "utcyearmonthdate", "title": None,
                                "axis": {"labelExpr": "utcdate(datum.value) <= 7 ? utcFormat(datum.value, '%b %y') : ''",
                                         "labelAngle": 0, "domain": False, "ticks": False, "labelOverlap": False}},
                          "y": {"field": "dow", "type": "ordinal", "title": None,
                                "axis": {"labelExpr": f"{days}[datum.value]", "domain": False, "ticks": False}},
                          "color": {"field": "v", "type": "quantitative", "title": None,
                                    "scale": {"type": "sqrt", "range": colors or ["#E8F1FB", PAL[0], PAL[7]]},
                                    "legend": {"orient": "right", "labelExpr": axis_short(), "gradientLength": 120}},
                          "tooltip": [{"field": "fd", "type": "temporal", "timeUnit": "utcyearmonthdate", "title": "Fecha", "format": "%d %b %Y"},
                                      {"field": "txt", "title": "Valor"}]})


# ====================================================================== dispersión y distribución
def scatter(title, subtitle, x, y, size=None, color=None, color_domain=None, colors=None, log_x=False, log_y=False,
            cross_filter=True, tooltip=None, x_title=None, y_title=None, y_prefix=""):
    """Burbujas. Con cross_filter y color, clic en una burbuja filtra por esa categoría (vista única, sin capas)."""
    enc = {"x": {"field": x, "type": "quantitative", "title": x_title, "scale": {"type": "log"} if log_x else {"zero": False}},
           "y": {"field": y, "type": "quantitative", "title": y_title, "scale": {"type": "log"} if log_y else {"zero": False},
                 "axis": {"labelExpr": f"'{y_prefix}' + format(datum.value, '~s')"}},
           "tooltip": tooltip or [{"field": x}, {"field": y}]}
    if size:
        enc["size"] = {"field": size, "type": "quantitative", "legend": None, "scale": {"range": [8, 520]}}
    if color:
        enc["color"] = {"field": color, "type": "nominal", "title": None,
                        "scale": {"domain": color_domain, "range": colors or PAL} if color_domain else {"range": colors or PAL},
                        "legend": {"orient": "top", "columns": 3}}
    extra = {}
    if cross_filter and color:
        extra["params"] = [{"name": "databricks_mark_selection", "select": {"type": "point", "fields": [color]}}]
        enc["opacity"] = {"condition": {"param": "databricks_mark_selection", "empty": True, "value": 0.72}, "value": 0.08}
    else:
        enc["opacity"] = {"value": 0.72}
    return spec(title, subtitle, pad=(28, 28, 28, 24), title_extra=60,
                mark={"type": "circle", "tooltip": True, "stroke": S["card"], "strokeWidth": 0.6, "cursor": "pointer", "clip": True},
                encoding=enc, **extra)


def boxplot(title, subtitle, cat, val, colors=None, y_title=None):
    """Box plot. El widget va con disaggregated=True (filas crudas); usa una muestra si son muchas filas."""
    return spec(title, subtitle, pad=(28, 28, 28, 22),
                mark={"type": "boxplot", "extent": 1.5, "size": 42, "median": {"color": "#FFFFFF", "strokeWidth": 2},
                      "outliers": {"size": 10, "opacity": 0.35}, "rule": {"color": "#9AA5B1"}, "ticks": False},
                encoding={"x": {"field": cat, "type": "nominal", "title": None, "axis": {"labelAngle": 0, "domain": False, "ticks": False}},
                          "y": {"field": val, "type": "quantitative", "title": y_title, "scale": {"zero": True}},
                          "color": {"field": cat, "type": "nominal", "legend": None, "scale": {"range": colors or PAL}}})


def funnel(title, subtitle, stage, order, val, colors=None):
    """Embudo centrado con etiqueta 'etapa · n (% del total)' y conversión vs la etapa anterior a la derecha."""
    return spec(title, subtitle, pad=(24, 28, 24, 18),
                transform=[{"aggregate": [{"op": "sum", "field": val, "as": "p"}], "groupby": [order, stage]},
                           {"window": [{"op": "first_value", "field": "p", "as": "p0"}, {"op": "lag", "field": "p", "as": "pp"}],
                            "sort": [{"field": order}], "frame": [None, None]},
                           {"calculate": "-datum.p / 2", "as": "x0"}, {"calculate": "datum.p / 2", "as": "x1"},
                           {"calculate": f"datum['{stage}'] + '  ·  ' + format(datum.p, ',') + ' (' + format(datum.p / datum.p0, '.0%') + ')'", "as": "lt"},
                           {"calculate": f"datum.pp == null ? '' : format(datum.p / datum.pp, '.1%') + ' {t('of_prev')}'", "as": "conv"}],
                encoding={"y": {"field": order, "type": "ordinal", "sort": "ascending", "axis": None}},
                layer=[
                    {"mark": {"type": "bar", "cornerRadius": 6, "height": {"band": 0.72}, "tooltip": True},
                     "encoding": {"x": {"field": "x0", "type": "quantitative", "axis": None}, "x2": {"field": "x1"},
                                  "color": {"field": order, "type": "ordinal", "legend": None,
                                            "scale": {"range": colors or [PAL[7], PAL[0], "#8EA2FB", PAL[6], "#9DE0D6"]}},
                                  "tooltip": [{"field": stage}, {"field": "p", "format": ","}, {"field": "conv"}]}},
                    # etiqueta dentro de la barra si cabe; si no, a la izquierda de la barra
                    {"transform": [{"filter": "datum.p / datum.p0 >= 0.42"}],
                     "mark": {"type": "text", "fontSize": 11.5, "fontWeight": 700, "color": "#FFFFFF"},
                     "encoding": {"x": {"datum": 0, "type": "quantitative"}, "text": {"field": "lt"}}},
                    {"transform": [{"filter": "datum.p / datum.p0 < 0.42"}],
                     "mark": {"type": "text", "fontSize": 11, "fontWeight": 700, "color": S["ink"], "align": "right", "dx": -8},
                     "encoding": {"x": {"field": "x0", "type": "quantitative"}, "text": {"field": "lt"}}},
                    {"mark": {"type": "text", "fontSize": 10.5, "color": S["muted"], "align": "left", "dx": 8},
                     "encoding": {"x": {"field": "x1", "type": "quantitative"}, "text": {"field": "conv"}}},
                ])


# ====================================================================== desempeño vs meta
def gauge(title, field, target, lo=0.0, hi=1.0, fmt=".1%", inverse=False, accent=None, warn=None):
    """Gauge semicircular: pista, arco de valor (color de alerta si no cumple), marca de meta y valor grande.
    El query del widget debe devolver 1 fila con `field`. Títulos cortos: el gauge es angosto."""
    accent, warn = accent or PAL[0], warn or PAL[2]
    pi = math.pi
    ang = lambda v: f"(-{pi / 2} + {pi} * clamp(({v} - {lo}) / ({hi - lo}), 0, 1))"
    good = f"datum.val {'<=' if inverse else '>='} {target}"
    R = "min(width / 2, height * 0.9)"
    cx, cy = {"value": {"expr": "width / 2"}}, {"value": {"expr": "height * 0.92"}}
    return spec(title, None, pad=(18, 20, 18, 8),
                transform=[{"calculate": f"datum['{field}']", "as": "val"},
                           {"calculate": f"format(datum.val, '{fmt}')", "as": "txt"},
                           {"calculate": f"'{t('target')}: ' + format({target}, '{fmt}')", "as": "mt"}],
                layer=[
                    {"mark": {"type": "arc", "theta": -pi / 2, "theta2": pi / 2, "innerRadius": {"expr": f"{R} * 0.68"},
                              "outerRadius": {"expr": f"{R} * 0.95"}, "cornerRadius": 6, "color": S["track"]},
                     "encoding": {"x": cx, "y": cy}},
                    {"mark": {"type": "arc", "theta": -pi / 2, "innerRadius": {"expr": f"{R} * 0.68"},
                              "outerRadius": {"expr": f"{R} * 0.95"}, "cornerRadius": 6, "tooltip": True},
                     "encoding": {"x": cx, "y": cy, "theta2": {"value": {"expr": ang("datum.val")}},
                                  "color": {"condition": {"test": good, "value": accent}, "value": warn},
                                  "tooltip": [{"field": "txt", "title": title}, {"field": "mt", "title": t("target")}]}},
                    {"mark": {"type": "arc", "innerRadius": {"expr": f"{R} * 0.62"}, "outerRadius": {"expr": f"{R} * 1.0"},
                              "color": S["ink"], "theta": {"expr": ang(target) + " - 0.008"}, "theta2": {"expr": ang(target) + " + 0.008"}},
                     "encoding": {"x": cx, "y": cy}},
                    {"mark": {"type": "text", "fontSize": 26, "fontWeight": 700, "color": S["ink"], "baseline": "alphabetic"},
                     "encoding": {"x": cx, "y": {"value": {"expr": "height * 0.88"}}, "text": {"field": "txt"}}},
                    {"mark": {"type": "text", "fontSize": 10.5, "color": S["muted"], "baseline": "top"},
                     "encoding": {"x": cx, "y": {"value": {"expr": "height * 0.92 + 4"}}, "text": {"field": "mt"}}},
                ], config={"title": {"fontSize": 13, "offset": 6}})


def bullet(title, subtitle, cat, val, bands, target, domain, fmt=".1%", good_color=None, bad_color=None, title_extra=130):
    """Bullet chart horizontal: bandas cualitativas, barra de valor y marca de meta.
    bands = [(desde, hasta, color)], domain = (min, max) del eje."""
    gc, bc = good_color or PAL[7], bad_color or PAL[2]
    layers = []
    for i, (a, b, c) in enumerate(bands):
        x = {"datum": a, "type": "quantitative"}
        if i == 0:
            x.update({"scale": {"domain": list(domain)}, "axis": {"format": fmt.replace(".1", ".0"), "tickCount": 4}, "title": None})
        layers.append({"mark": {"type": "bar", "color": c, "height": {"band": 0.8}}, "encoding": {"x": x, "x2": {"datum": b}}})
    layers += [
        # x = campo y x2 = datum (al revés falla la compilación)
        {"mark": {"type": "bar", "height": {"band": 0.32}, "cornerRadiusEnd": 3, "tooltip": True},
         "encoding": {"x": {"field": "v", "type": "quantitative", "title": None}, "x2": {"datum": domain[0]},
                      "color": {"condition": {"test": f"datum.v >= {target}", "value": gc}, "value": bc},
                      "tooltip": [{"field": cat}, {"field": "v", "format": fmt}]}},
        {"mark": {"type": "tick", "color": S["ink"], "thickness": 2.5, "size": 26}, "encoding": {"x": {"datum": target, "type": "quantitative"}}},
        {"mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 10.5, "fontWeight": 700, "color": S["ink"]},
         "encoding": {"x": {"field": "v", "type": "quantitative"}, "text": {"field": "v", "format": fmt}}},
    ]
    return spec(title, subtitle, pad=(24, 28, 40, 22), title_extra=title_extra,
                transform=[{"aggregate": [{"op": "mean", "field": val, "as": "v"}], "groupby": [cat]}],
                encoding={"y": {"field": cat, "type": "nominal", "title": None, "sort": {"field": "v", "order": "descending"},
                                "axis": {"domain": False, "ticks": False, "labelFontWeight": 600}}},
                layer=layers)


def radar(title, subtitle, series, metrics, colors=None):
    """Radar normalizado min-max por métrica. metrics = [(campo, etiqueta, invertir)]; invertir=True: menos es mejor.
    El query devuelve una fila por serie con las métricas como columnas (agregadas)."""
    keys = [m for m, _, _ in metrics]
    inv = [m for m, _, i in metrics if i]
    n = len(metrics)
    axes = [{"k": i, "m": lab} for i, (_, lab, _) in enumerate(metrics)]
    sc_x, sc_y = {"domain": [-1.25, 1.25]}, {"domain": [-1.2, 1.3]}
    return spec(title, subtitle, pad=(24, 28, 24, 18),
                transform=[{"fold": keys, "as": ["met", "val"]},
                           {"calculate": f"indexof({json.dumps(keys)}, datum.met)", "as": "ai"},
                           {"joinaggregate": [{"op": "min", "field": "val", "as": "mn"}, {"op": "max", "field": "val", "as": "mx"}],
                            "groupby": ["met"]},
                           {"calculate": "datum.mx == datum.mn ? 0.6 : (datum.val - datum.mn) / (datum.mx - datum.mn)", "as": "z"},
                           {"calculate": f"indexof({json.dumps(inv)}, datum.met) >= 0 ? 1 - datum.z : datum.z", "as": "z"},
                           {"calculate": "0.25 + 0.75 * datum.z", "as": "r"},
                           # el primer vértice se repite al final para cerrar el polígono
                           {"calculate": f"datum.ai == 0 ? [0, {n}] : [datum.ai]", "as": "ks"},
                           {"flatten": ["ks"], "as": ["k"]},
                           {"calculate": f"2 * PI * datum.k / {n}", "as": "a"},
                           {"calculate": "datum.r * sin(datum.a)", "as": "x"},
                           {"calculate": "datum.r * cos(datum.a)", "as": "y"}],
                layer=[
                    {"data": {"values": [{"rr": rr, "k": k} for rr in (0.25, 0.5, 0.75, 1.0) for k in range(n + 1)]},
                     "transform": [{"calculate": f"2 * PI * datum.k / {n}", "as": "a"},
                                   {"calculate": "datum.rr * sin(datum.a)", "as": "x"}, {"calculate": "datum.rr * cos(datum.a)", "as": "y"}],
                     "mark": {"type": "line", "color": S["grid"] if THEME_NAME == "dark" else "#DDE3EA", "strokeWidth": 1},
                     "encoding": {"x": {"field": "x", "type": "quantitative", "axis": None, "scale": sc_x},
                                  "y": {"field": "y", "type": "quantitative", "axis": None, "scale": sc_y},
                                  "detail": {"field": "rr"}, "order": {"field": "k"}}},
                    {"data": {"values": axes},
                     "transform": [{"calculate": f"2 * PI * datum.k / {n}", "as": "a"},
                                   {"calculate": "1.13 * sin(datum.a)", "as": "x"}, {"calculate": "1.13 * cos(datum.a)", "as": "y"}],
                     "mark": {"type": "text", "fontSize": 11, "fontWeight": 600, "color": S["muted"]},
                     "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"},
                                  "text": {"field": "m"}}},
                    {"mark": {"type": "line", "strokeWidth": 2.2, "opacity": 0.9, "point": {"filled": True, "size": 36}},
                     "encoding": {"x": {"field": "x", "type": "quantitative"}, "y": {"field": "y", "type": "quantitative"},
                                  "order": {"field": "k"},
                                  "color": {"field": series, "type": "nominal", "title": None, "scale": {"range": colors or PAL},
                                            "legend": {"orient": "bottom", "columns": 3}}}},
                ])


# ====================================================================== redes y linaje
NETWORK_FIELDS = ["tipo", "x", "y", "x2", "y2", "relacion", "info", "etiqueta", "capa", "k1", "k2", "vecinos"]


def network_sql(nodes_sql, edges_sql, header_gap=1.1):
    """SQL de un dataset para layered_network(): posiciona los nodos por capa y deja una fila por nodo, por arista
    y por encabezado de capa (columna `tipo` = 'nodo' | 'arista' | 'capa').

    nodes_sql devuelve: nodo (id único, sin '|'), etiqueta, capa (texto del encabezado), orden_capa (número: la
      columna; con decimales hace subcolumnas dentro de una capa, p. ej. 2 y 2.45), info (texto para el tooltip).
    edges_sql devuelve: origen, destino (ids de nodo), relacion (categoría para el color), info (tooltip).
    Las aristas cuyo origen o destino no está en los nodos se descartan."""
    return f"""WITH n0 AS ({nodes_sql}),
e0 AS ({edges_sql}),
n AS (SELECT *, CAST(orden_capa AS DOUBLE) AS x,
        CAST(row_number() OVER (PARTITION BY orden_capa ORDER BY etiqueta)
             - (count(*) OVER (PARTITION BY orden_capa) + 1) / 2.0 AS DOUBLE) AS y
      FROM n0),
e AS (SELECT e0.relacion, e0.info, o.nodo AS k1, d.nodo AS k2, o.etiqueta AS l1, d.etiqueta AS l2,
             o.x, o.y, d.x AS x2, d.y AS y2
      FROM e0 JOIN n o ON o.nodo = e0.origen JOIN n d ON d.nodo = e0.destino),
v AS (SELECT k, concat('|', array_join(collect_set(o), '|'), '|') AS vecinos
      FROM (SELECT k1 AS k, k2 AS o FROM e UNION ALL SELECT k2, k1 FROM e UNION ALL SELECT nodo, nodo FROM n)
      GROUP BY k)
SELECT 'arista' AS tipo, x, y, x2, y2, relacion, info, concat('De ', l1, ' a ', l2) AS etiqueta,
       CAST(NULL AS STRING) AS capa, k1, k2, CAST(NULL AS STRING) AS vecinos
FROM e
UNION ALL
SELECT 'nodo', n.x, n.y, NULL, NULL, NULL, n.info, n.etiqueta, n.capa, n.nodo, NULL, v.vecinos
FROM n LEFT JOIN v ON v.k = n.nodo
UNION ALL
SELECT 'capa', min(x), (SELECT max(y) FROM n) + {header_gap}, NULL, NULL, NULL, NULL, NULL, capa, NULL, NULL, NULL
FROM n GROUP BY capa"""


def layered_network(title, subtitle, kinds=None, colors=None, node_color=None, focus_color=None, header_color=None,
                    node_size=260, label_size=11, legend_columns=6, x_pad=70, y_pad=34,
                    node_tip="Objeto", layer_tip="Capa", info_tip="Detalle", edge_tip="Relación", kind_tip="Tipo"):
    """Red por capas (linaje, flujo de proceso, dependencias) con enlaces curvos y FOCO POR CLIC: clic en un nodo deja
    resaltados solo él, sus aristas y sus vecinos directos; clic en el fondo (o doble clic) regresa a todo.
    Datos: el dataset de network_sql(); fields = [f(c) for c in NETWORK_FIELDS] con disaggregated=True.
    kinds/colors: dominio y colores de `relacion` (en orden). No usa cross-filter: el foco es local al widget."""
    node_color = node_color or S["ink"]
    focus_color = focus_color or PAL[1]
    header_color = header_color or PAL[0]
    sel, hay = "foco.k1[0]", "isValid(foco.k1)"
    toca = f"({sel} === datum.k1 || {sel} === datum.k2)"
    vecino = f"indexof(datum.vecinos, '|' + {sel} + '|') >= 0"
    X = {"field": "x", "type": "quantitative", "axis": None, "scale": {"zero": False, "nice": False, "padding": x_pad}}
    Y = {"field": "y", "type": "quantitative", "axis": None, "scale": {"zero": False, "nice": False, "padding": y_pad}}
    scale = {"domain": kinds, "range": colors or PAL} if kinds else {"range": colors or PAL}
    return spec(title, subtitle, pad=(24, 24, 24, 16),
                layer=[
                    # aristas: 4 puntos (origen, mitad, mitad, destino) con interpolación basis = curva en S
                    {"transform": [{"filter": "datum.tipo === 'arista'"},
                                   {"calculate": "datum.k1 + '>' + datum.k2", "as": "eid"},
                                   {"calculate": "[datum.x, (datum.x + datum.x2) / 2, (datum.x + datum.x2) / 2, datum.x2]", "as": "px"},
                                   {"calculate": "[datum.y, datum.y, datum.y2, datum.y2]", "as": "py"},
                                   {"calculate": "[0, 1, 2, 3]", "as": "pi"},
                                   {"flatten": ["px", "py", "pi"]}],
                     "mark": {"type": "line", "interpolate": "basis",
                              "strokeWidth": {"expr": f"{hay} && {toca} ? 3.2 : 1.6"},
                              "opacity": {"expr": f"{hay} ? ({toca} ? 0.95 : 0.04) : 0.5"}},
                     "encoding": {"x": {**X, "field": "px"}, "y": {**Y, "field": "py"}, "detail": {"field": "eid"},
                                  "order": {"field": "pi", "type": "quantitative"},
                                  "color": {"field": "relacion", "type": "nominal", "scale": scale,
                                            "legend": {"orient": "bottom", "title": None, "columns": legend_columns,
                                                       "symbolType": "stroke", "symbolStrokeWidth": 3, "symbolOpacity": 1,
                                                       "labelLimit": 260}},
                                  "tooltip": [{"field": "etiqueta", "title": edge_tip}, {"field": "relacion", "title": kind_tip},
                                              {"field": "info", "title": info_tip}]}},
                    # nodos: aquí vive el param de selección (los demás layers lo leen por expresión)
                    {"transform": [{"filter": "datum.tipo === 'nodo'"}],
                     "params": [{"name": "foco", "select": {"type": "point", "fields": ["k1"], "on": "click", "clear": "dblclick"}}],
                     "mark": {"type": "circle", "size": node_size, "stroke": S["card"], "strokeWidth": 2, "cursor": "pointer",
                              "opacity": {"expr": f"{hay} ? ({vecino} ? 1 : 0.15) : 1"}},
                     "encoding": {"x": X, "y": Y,
                                  "color": {"condition": {"param": "foco", "empty": False, "value": focus_color}, "value": node_color},
                                  "tooltip": [{"field": "etiqueta", "title": node_tip}, {"field": "capa", "title": layer_tip},
                                              {"field": "info", "title": info_tip}]}},
                    {"transform": [{"filter": "datum.tipo === 'nodo'"}],
                     "mark": {"type": "text", "dy": -14, "fontSize": label_size, "color": S["ink"],
                              "opacity": {"expr": f"{hay} ? ({vecino} ? 1 : 0.2) : 1"},
                              "fontWeight": {"expr": f"{hay} && {sel} === datum.k1 ? 'bold' : 'normal'"}},
                     "encoding": {"x": X, "y": Y, "text": {"field": "etiqueta"}}},
                    {"transform": [{"filter": "datum.tipo === 'capa'"}],
                     "mark": {"type": "text", "fontSize": 13, "fontWeight": "bold", "color": header_color},
                     "encoding": {"x": X, "y": Y, "text": {"field": "capa"}}},
                ])


# ====================================================================== mapas
def load_geo(path, prop="name", key="nm"):
    """Lee un GeoJSON simplificado (tools/simplify_geo.py) y lo deja listo para lookup inline."""
    g = json.load(open(path, encoding="utf-8"))
    return [{key: ft["properties"][prop], "type": "Feature", "geometry": ft["geometry"],
             "properties": {prop: ft["properties"][prop]}} for ft in g["features"]]


def choropleth(title, subtitle, key, val, geo_values, rename=None, colors=None, scale_type="sqrt",
               legend_expr=None, projection="mercator", value_fmt=None):
    """Coroplético con geometría embebida (sin data.url): lookup por nombre contra geo_values (load_geo).
    rename = {'nombre en datos': 'nombre en geojson'}. Mantén el GeoJSON < ~40 KB (simplifica antes)."""
    tr = [{"aggregate": [{"op": "sum", "field": val, "as": "v"}], "groupby": [key]}]
    if rename:
        expr = f"datum['{key}']"
        for a, b in rename.items():
            expr = f"datum['{key}'] == '{a}' ? '{b}' : ({expr})"
        tr.append({"calculate": expr, "as": "nm"})
    else:
        tr.append({"calculate": f"datum['{key}']", "as": "nm"})
    tr += [{"lookup": "nm", "from": {"data": {"values": geo_values}, "key": "nm"}, "as": "geo"},
           {"filter": "datum.geo != null"},
           {"calculate": value_fmt or fmt_money("v"), "as": "txt"}]
    return spec(title, subtitle, pad=(16, 28, 16, 16), projection={"type": projection},
                layer=[{"data": {"name": "databricks_query"}, "transform": tr,
                        "mark": {"type": "geoshape", "stroke": S["card"], "strokeWidth": 0.8, "tooltip": True},
                        "encoding": {"shape": {"field": "geo", "type": "geojson"},
                                     "color": {"field": "v", "type": "quantitative", "title": None,
                                               "scale": {"type": scale_type, "range": colors or ["#E6EBFF", "#8EA2FB", PAL[0], PAL[7]]},
                                               "legend": {"orient": "bottom-left", "direction": "horizontal", "gradientLength": 160,
                                                          "labelExpr": legend_expr or axis_short(), "offset": 0}},
                                     "tooltip": [{"field": key}, {"field": "txt", "title": "Valor"}]}}])


# Rejilla de mosaicos de México (abreviatura, nombre, columna, fila)
TILES_MX = [("BC", "Baja California", 0, 0), ("SON", "Sonora", 1, 0), ("CHIH", "Chihuahua", 2, 0),
            ("COAH", "Coahuila", 3, 0), ("NL", "Nuevo León", 4, 0),
            ("BCS", "Baja California Sur", 0, 1), ("SIN", "Sinaloa", 1, 1), ("DGO", "Durango", 2, 1),
            ("ZAC", "Zacatecas", 3, 1), ("SLP", "San Luis Potosí", 4, 1), ("TAMS", "Tamaulipas", 5, 1),
            ("NAY", "Nayarit", 1, 2), ("AGS", "Aguascalientes", 2, 2), ("GTO", "Guanajuato", 3, 2),
            ("QRO", "Querétaro", 4, 2), ("HGO", "Hidalgo", 5, 2), ("VER", "Veracruz", 6, 2),
            ("JAL", "Jalisco", 1, 3), ("MICH", "Michoacán", 2, 3), ("MEX", "Estado de México", 3, 3),
            ("CDMX", "Ciudad de México", 4, 3), ("TLAX", "Tlaxcala", 5, 3), ("PUE", "Puebla", 6, 3),
            ("TAB", "Tabasco", 7, 3), ("CAMP", "Campeche", 8, 3), ("YUC", "Yucatán", 9, 3),
            ("COL", "Colima", 1, 4), ("GRO", "Guerrero", 2, 4), ("MOR", "Morelos", 3, 4),
            ("OAX", "Oaxaca", 5, 4), ("CHIS", "Chiapas", 6, 4), ("QROO", "Quintana Roo", 9, 4)]


def tile_map(title, subtitle, key, value_transforms, color_scale, tiles=TILES_MX, value_text="vtxt",
             tooltip=None, legend_format=".0%"):
    """Mapa de mosaicos (tile grid): una celda por región en posición aproximada, gris si no hay dato.
    value_transforms: transforms que dejan por fila `key`, `val` (para color) y `value_text` (etiqueta).
    tiles = [(abrev, nombre, col, fila)]; el nombre debe coincidir con `key` en los datos."""
    tv = [{"ab": a, "nm": e, "cx": c, "cy": r} for a, e, c, r in tiles]
    mx_c, mx_r = max(x[2] for x in tiles), max(x[3] for x in tiles)
    sx = {"domain": [-0.55, mx_c + 0.55], "nice": False, "zero": False}
    sy = {"domain": [mx_r + 0.55, -0.55], "nice": False, "zero": False}
    box = [{"calculate": "datum.cx - 0.45", "as": "x0"}, {"calculate": "datum.cx + 0.45", "as": "x1"},
           {"calculate": "datum.cy - 0.45", "as": "y0"}, {"calculate": "datum.cy + 0.45", "as": "y1"}]
    rect = lambda: {"x": {"field": "x0", "type": "quantitative", "axis": None, "scale": sx}, "x2": {"field": "x1"},
                    "y": {"field": "y0", "type": "quantitative", "axis": None, "scale": sy}, "y2": {"field": "y1"}}
    ctr = {"x": {"field": "cx", "type": "quantitative", "axis": None, "scale": sx},
           "y": {"field": "cy", "type": "quantitative", "axis": None, "scale": sy}}
    return spec(title, subtitle, pad=(24, 28, 24, 22), layer=[
        {"data": {"values": tv}, "transform": box, "mark": {"type": "rect", "color": S["track"], "cornerRadius": 5}, "encoding": rect()},
        {"data": {"values": tv}, "mark": {"type": "text", "fontSize": 9, "color": "#A7B1BC", "fontWeight": 600},
         "encoding": {**ctr, "text": {"field": "ab"}}},
        {"data": {"name": "databricks_query"},
         "transform": list(value_transforms) + [{"lookup": key, "from": {"data": {"values": tv}, "key": "nm", "fields": ["ab", "cx", "cy"]}},
                                                {"filter": "datum.cx != null"}] + box,
         "layer": [
             {"mark": {"type": "rect", "cornerRadius": 5, "tooltip": True},
              "encoding": {**rect(),
                           "color": {"field": "val", "type": "quantitative", "title": None, "scale": color_scale,
                                     "legend": {"orient": "bottom", "direction": "horizontal", "gradientLength": 200,
                                                "format": legend_format, "offset": 12}},
                           "tooltip": tooltip or [{"field": key}, {"field": value_text, "title": "Valor"}]}},
             {"mark": {"type": "text", "fontSize": 10.5, "fontWeight": 700, "dy": -7, "color": "#FFFFFF"},
              "encoding": {**ctr, "text": {"field": "ab"}}},
             {"mark": {"type": "text", "fontSize": 10, "dy": 7, "color": "#FFFFFF"},
              "encoding": {**ctr, "text": {"field": value_text}}},
         ]},
    ])


# ====================================================================== matriz tipo Power BI
def matrix(title, subtitle, levels, columns, measures, top=14, mode="ident", period=None, stock_first=(), stock_last=(),
           label_header="Elemento", label_width=3.3):
    """Matriz con jerarquía, subtotales, barras de datos, píldoras y formato condicional, dibujada en Vega-Lite.

    levels   = ['l1', 'l2', 'l3'] (1 a 3 columnas; vacío '' = sin nivel). mode='ident' sangra y subtotaliza;
               mode='flat' une los niveles en una fila por combinación.
    measures = columnas numéricas que se suman (las que vienen del query).
    columns  = [{"key", "label", "fmt": money|pct|int|num, "expr": (opcional, sobre medidas ya sumadas),
                 "bar": True (barra de datos), "sign": True (verde/rojo por signo), "pill": "expr de signo"}]
    period + stock_first/stock_last: medidas tipo saldo (no se suman en el tiempo): toma el primer/último periodo."""
    keys = [c["key"] for c in columns]
    nl = len(levels)
    tr = []
    if period and (stock_first or stock_last):
        tr += [{"calculate": f"time(toDate(datum['{period}']))", "as": "mt_"},
               {"joinaggregate": [{"op": "min", "field": "mt_", "as": "m0_"}, {"op": "max", "field": "mt_", "as": "m1_"}]}]
        tr += [{"calculate": f"datum.mt_ == datum.m0_ ? datum['{m}'] : 0", "as": m} for m in stock_first]
        tr += [{"calculate": f"datum.mt_ == datum.m1_ ? datum['{m}'] : 0", "as": m} for m in stock_last]
    L = [f"(datum['{lv}'] == null ? '' : datum['{lv}'])" for lv in levels]
    tr += [{"calculate": L[i], "as": f"L{i + 1}"} for i in range(nl)]
    if mode == "ident" and nl > 1:
        tr += [{"calculate": json.dumps(list(range(1, nl + 1))), "as": "lvs"}, {"flatten": ["lvs"], "as": ["lv"]},
               {"filter": " || ".join(["datum.lv == 1"] + [f"(datum.lv == {i} && datum.L{i} != '')" for i in range(2, nl + 1)])}]
        # clave jerárquica: L1, L1|L2, L1|L2|L3 (ordena padres antes que hijos)
        parts = ["datum.L1"] + [f"datum.L{i}" for i in range(2, nl + 1)]
        key_expr = " : ".join(f"datum.lv == {i} ? " + " + '\u0001' + ".join(parts[:i]) for i in range(1, nl)) + " : " + " + '\u0001' + ".join(parts)
        lab_expr = " : ".join(f"datum.lv == {i} ? datum.L{i}" for i in range(1, nl)) + f" : datum.L{nl}"
        tr += [{"calculate": key_expr, "as": "key"}, {"calculate": lab_expr, "as": "lab"}]
        ident = True
    else:
        tr += [{"calculate": "1", "as": "lv"},
               {"calculate": " + ".join(["datum.L1"] + [f"(datum.L{i} != '' ? '\u0001' + datum.L{i} : '')" for i in range(2, nl + 1)]), "as": "key"},
               {"calculate": " + ".join(["datum.L1"] + [f"(datum.L{i} != '' ? '  ·  ' + datum.L{i} : '')" for i in range(2, nl + 1)]), "as": "lab"}]
        ident = False
    tr.append({"aggregate": [{"op": "sum", "field": m, "as": m} for m in measures], "groupby": ["key", "lv", "lab", "L1"]})
    for c in columns:
        if c.get("expr"):
            tr.append({"calculate": c["expr"], "as": c["key"]})
    bar_keys = [c["key"] for c in columns if c.get("bar")]
    sign_keys = [c["key"] for c in columns if c.get("sign")]
    pill = {c["key"]: c["pill"] for c in columns if c.get("pill")}
    w_expr = " + ".join(f"abs(datum['{k}'] || 0)" for k in (bar_keys or keys[:1]))
    tr += [
        {"calculate": f"datum.lv == 1 ? {w_expr} : 0", "as": "w1"},
        {"joinaggregate": [{"op": "max", "field": "w1", "as": "w"}], "groupby": ["L1"] if ident else ["key"]},
        {"window": [{"op": "dense_rank", "as": "r1"}], "sort": [{"field": "w", "order": "descending"}]},
        {"filter": f"datum.r1 <= {top}"},
    ]
    if ident:
        # padres por magnitud y, dentro, hijos en orden de clave
        tr.append({"window": [{"op": "row_number", "as": "rn"}], "sort": [{"field": "r1"}, {"field": "key"}]})
    else:
        tr.append({"window": [{"op": "row_number", "as": "rn"}], "sort": [{"field": "w", "order": "descending"}]})
    tr.append({"calculate": truncate("datum.lab", 44), "as": "labt"})
    for k, e in pill.items():
        tr.append({"calculate": e, "as": "pill_" + k})
    tr += [{"fold": keys, "as": ["ind", "val"]},
           {"calculate": f"indexof({json.dumps(keys)}, datum.ind)", "as": "ci"},
           {"calculate": "abs(datum.val)", "as": "av"},
           {"joinaggregate": [{"op": "max", "field": "av", "as": "mx"}], "groupby": ["ind", "lv"]}]
    fmt_case = "".join(
        f"datum.ind == '{c['key']}' ? ({_cell_fmt(c.get('fmt', 'money'))}) : " for c in columns) + "''"
    tr += [{"calculate": fmt_case, "as": "txt"}, {"calculate": f"{label_width} + datum.ci", "as": "c0"}]
    for k in pill:
        tr.append({"calculate": f"datum.ind == '{k}' ? datum['pill_{k}'] : null", "as": "ps_" + k})
    W = label_width + len(columns)
    X = {"type": "quantitative", "axis": None, "scale": {"domain": [0, W], "nice": False}}
    Y = {"field": "rn", "type": "ordinal", "axis": None, "scale": {"paddingInner": 0, "paddingOuter": 0}}
    first = {"filter": "datum.ci == 0"}
    is_l1 = "datum.lv == 1 && " + ("true" if ident else "false")
    head_bg = "#1C2546" if THEME_NAME == "dark" else "#EAF1FA"
    neg_txt = "#E07A86" if THEME_NAME == "dark" else "#B03A48"
    color_rules = "".join(f"datum.ind == '{k}' ? (datum.val >= 0 ? '{GOOD}' : '{BAD}') : " for k in sign_keys)
    color_rules += "".join(f"datum.ind == '{k}' ? (datum['ps_{k}'] >= 0 ? '{GOOD}' : '{BAD}') : " for k in pill)
    layers = [
        {"transform": [first], "mark": {"type": "rect", "cornerRadius": 4},
         "encoding": {"x": {"datum": 0, **X}, "x2": {"datum": W}, "y": Y,
                      "color": {"value": {"expr": f"{is_l1} ? '{head_bg}' : (datum.rn % 2 == 0 ? '{S['zebra']}' : '{S['card']}')"}}}},
    ]
    if bar_keys:
        layers.append({"transform": [{"filter": f"indexof({json.dumps(bar_keys)}, datum.ind) >= 0 && datum.mx > 0"},
                                     {"calculate": "datum.c0 + 0.06", "as": "b0"},
                                     {"calculate": "datum.c0 + 0.06 + 0.88 * datum.av / datum.mx", "as": "b1"}],
                       "mark": {"type": "bar", "cornerRadius": 3, "height": {"band": 0.56}},
                       "encoding": {"x": {"field": "b0", **X}, "x2": {"field": "b1"}, "y": Y,
                                    "color": {"value": {"expr": "datum.val >= 0 ? '#D6E6F8' : '#F9D9DC'"}}}})
    for k in pill:
        layers.append({"transform": [{"filter": f"datum.ind == '{k}' && datum.val != null"},
                                     {"calculate": "datum.c0 + 0.16", "as": "b0"}, {"calculate": "datum.c0 + 0.96", "as": "b1"}],
                       "mark": {"type": "bar", "cornerRadius": 8, "height": {"band": 0.62}},
                       "encoding": {"x": {"field": "b0", **X}, "x2": {"field": "b1"}, "y": Y,
                                    "color": {"value": {"expr": f"datum['ps_{k}'] >= 0 ? '{GOOD_BG}' : '{BAD_BG}'"}}}})
    # fontWeight NO es canal de encoding en Vega-Lite (se descarta en silencio): negrita = capa aparte con filtro
    bold_val = f"({is_l1}) || indexof({json.dumps(sign_keys)}, datum.ind) >= 0"
    for weight, test_l, test_v in (("bold", is_l1, bold_val), ("normal", f"!({is_l1})", f"!({bold_val})")):
        layers += [
            {"transform": [first, {"filter": test_l}, {"calculate": "datum.lv == 1 ? 0.12 : datum.lv == 2 ? 0.42 : 0.72", "as": "lx"}],
             "mark": {"type": "text", "align": "left", "baseline": "middle", "fontSize": 11.5, "fontWeight": weight},
             "encoding": {"x": {"field": "lx", **X}, "y": Y, "text": {"field": "labt"},
                          "color": {"value": {"expr": f"datum.lv == 3 ? '{S['muted']}' : '{S['ink']}'"}},
                          "tooltip": [{"field": "lab", "title": label_header}]}},
            {"transform": [{"filter": test_v}, {"calculate": "datum.c0 + 0.94", "as": "tx"}],
             "mark": {"type": "text", "align": "right", "baseline": "middle", "fontSize": 11, "fontWeight": weight},
             "encoding": {"x": {"field": "tx", **X}, "y": Y, "text": {"field": "txt"},
                          "color": {"value": {"expr": f"{color_rules}(datum.val < 0 ? '{neg_txt}' : '{S['ink']}')"}},
                          "tooltip": [{"field": "lab", "title": label_header}, {"field": "ind"}, {"field": "val", "format": ",.2f"}]}},
        ]
    layers += [
        {"data": {"values": [{"h": c["label"], "ci": i} for i, c in enumerate(columns)]},
         "transform": [{"calculate": f"{label_width} + datum.ci + 0.94", "as": "tx"}],
         "mark": {"type": "text", "align": "right", "baseline": "bottom", "fontSize": 10.5, "fontWeight": 700, "color": S["muted"]},
         "encoding": {"x": {"field": "tx", **X}, "y": {"value": -10}, "text": {"field": "h"}}},
        {"data": {"values": [{"h": label_header}]},
         "mark": {"type": "text", "align": "left", "baseline": "bottom", "fontSize": 10.5, "fontWeight": 700, "color": S["muted"]},
         "encoding": {"x": {"datum": 0.12, **X}, "y": {"value": -10}, "text": {"field": "h"}}},
        {"data": {"values": [{"a": 0}]},
         "mark": {"type": "rule", "color": S["domain"], "strokeWidth": 1.2},
         "encoding": {"x": {"datum": 0, **X}, "x2": {"datum": W}, "y": {"value": -4}}},
    ]
    return spec(title, subtitle, pad=(28, 30, 28, 18), transform=tr, layer=layers, config={"title": {"offset": 34}})


def _cell_fmt(kind):
    if kind == "pct":
        return "datum.val == null ? '' : format(datum.val, '.1%')"
    if kind == "int":
        return "datum.val == null ? '' : format(datum.val, ',.0f')"
    if kind == "num":
        return "datum.val == null ? '' : format(datum.val, ',.2f')"
    return fmt_money("val", parens=True)


# ====================================================================== widgets nativos que sí funcionan
def fmt_currency(code="MXN", compact=True, places=1):
    d = {"type": "number-currency", "currencyCode": code, "decimalPlaces": {"type": "max", "places": places}}
    if compact:
        d["abbreviation"] = "compact"
    return d


FMT_PCT = {"type": "number-percent", "decimalPlaces": {"type": "max", "places": 1}}
STYLE_SIGN = {"type": "basic", "rules": [
    {"condition": {"operand": {"type": "data-value", "value": "0"}, "operator": "<"}, "foregroundColor": BAD},
    {"condition": {"operand": {"type": "data-value", "value": "0"}, "operator": ">="}, "foregroundColor": GOOD}]}


def n_table(name, dataset, columns, title, disaggregated=True):
    """Tabla nativa (scroll, orden, descarga). columns = [{"fieldName", "displayName", "format"?, "style"?,
    "dateTimeFormat"?, "displayAs"?}]. Las columnas son también los campos del query."""
    return native(name, dataset, [f(c["fieldName"]) for c in columns],
                  {"version": 2, "widgetType": "table", "encodings": {"columns": columns},
                   "frame": {"showTitle": True, "title": title}}, disaggregated=disaggregated)


def n_sankey(name, dataset, stages, value_col, title, value_label="Valor"):
    """Sankey nativo: stages = [(columna, etiqueta)] (2 o 3 etapas), value_col se suma."""
    vf = f"sum({value_col})"
    return native(name, dataset, [f(c) for c, _ in stages] + [f(vf, f"SUM(`{value_col}`)")],
                  {"version": 1, "widgetType": "sankey",
                   "encodings": {"value": {"fieldName": vf, "displayName": value_label},
                                 "stages": [{"fieldName": c, "displayName": lab} for c, lab in stages]},
                   "frame": {"showTitle": True, "title": title}})


def n_heatmap(name, dataset, x, y, val, title, agg_fn="AVG", start="#EEF2FF", end=None, x_label=None, y_label=None, val_label=None):
    vf = f"{agg_fn.lower()}({val})"
    return native(name, dataset, [f(x), f(y), f(vf, f"{agg_fn.upper()}(`{val}`)")], {
        "version": 3, "widgetType": "heatmap",
        "encodings": {"x": {"fieldName": x, "scale": {"type": "categorical"}, "axis": {"hideTitle": True}, "displayName": x_label or x},
                      "y": {"fieldName": y, "scale": {"type": "categorical"}, "axis": {"hideTitle": True}, "displayName": y_label or y},
                      "color": {"fieldName": vf, "displayName": val_label or val,
                                "scale": {"type": "quantitative",
                                          "colorRamp": {"mode": "custom-sequential", "colors": {"start": start, "end": end or PAL[7]}}}}},
        "frame": {"showTitle": True, "title": title}})


def n_histogram(name, dataset, col, bin_width, title, x_label=None, y_label="Conteo"):
    """Histograma nativo. Recorta outliers en SQL (least(col, tope)) o se aplasta la distribución."""
    bf = f"bin({col}, binWidth={bin_width})"
    return native(name, dataset, [f(bf, f"BIN_FLOOR(`{col}`, {bin_width})"), f("count(*)", "COUNT(`*`)")], {
        "version": 3, "widgetType": "histogram",
        "encodings": {"x": {"fieldName": bf, "scale": {"type": "quantitative"}, "displayName": x_label or col},
                      "y": {"fieldName": "count(*)", "scale": {"type": "quantitative"}, "displayName": y_label}},
        "frame": {"showTitle": True, "title": title}})


def n_forecast(name, dataset, x, actual, pred, upper, lower, title, x_label="Fecha", actual_label="Real", pred_label="Pronóstico"):
    """forecast-line nativo, pensado para AI_FORECAST (ver references/native-widgets.md para el SQL)."""
    return native(name, dataset, [f(x), f(actual), f(pred), f(upper), f(lower)], {
        "version": 1, "widgetType": "forecast-line",
        "encodings": {"x": {"fieldName": x, "scale": {"type": "temporal"}, "displayName": x_label},
                      "y": {"scale": {"type": "quantitative"}, "axis": {"hideTitle": True},
                            "original": {"fieldName": actual, "displayName": actual_label},
                            "prediction": {"fieldName": pred, "displayName": pred_label},
                            "predictionUpper": {"fieldName": upper}, "predictionLower": {"fieldName": lower}}},
        "frame": {"showTitle": True, "title": title}}, disaggregated=True)


def n_points(name, dataset, lat, lon, color, title, mapping=None, opacity=0.8):
    """Mapa de puntos nativo (symbol-map). Sin encoding de tamaño: las burbujas salen enormes.
    mapping = [(valor, hex)] para colores fijos por categoría."""
    enc = {"coordinates": {"latitude": {"fieldName": lat}, "longitude": {"fieldName": lon}},
           "color": {"fieldName": color, "displayName": color}}
    if mapping:
        enc["color"]["scale"] = {"type": "categorical", "mappings": [{"value": v, "color": c} for v, c in mapping]}
    return native(name, dataset, [f(lat), f(lon), f(color)], {
        "version": 2, "widgetType": "symbol-map", "encodings": enc, "mark": {"opacity": opacity},
        "frame": {"showTitle": True, "title": title}})
