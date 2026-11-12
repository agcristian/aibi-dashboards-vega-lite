// Renderiza los widgets de una página (items.json de preview.py) a un HTML con la rejilla real del dashboard.
// Los custom-vega-viz se compilan con vega-lite y se pintan como SVG; los nativos salen como recuadros.
import fs from 'fs';
import * as vega from 'vega';
import * as vl from 'vega-lite';
const [,, itemsPath, outPath] = process.argv;
const items = JSON.parse(fs.readFileSync(itemsPath));
const bg = process.env.CANVAS || '#FFFFFF';
const card = process.env.CARD || '#FFFFFF';
const radius = process.env.RADIUS || '12';
let html = `<html><head><meta charset="utf-8"></head><body style="margin:0;background:${bg};font-family:Segoe UI,Helvetica,Arial,sans-serif"><div style="position:relative;margin:20px">`;
let ok = 0, fail = 0;
for (const it of items) {
  const box = `position:absolute;left:${it.x}px;top:${it.y}px;width:${it.w}px;height:${it.h}px;overflow:hidden;border-radius:${radius}px;background:${card};`;
  if (it.type === 'vega') {
    try {
      if (it.err) throw new Error('SQL: ' + it.err);
      const s = structuredClone(it.spec);
      const swap = (o) => { if (o && typeof o === 'object') { if (o.data && o.data.name === 'databricks_query') o.data = {values: it.rows}; for (const k of Object.keys(o)) if (k !== 'data') swap(o[k]); if (o.layer) o.layer.forEach(swap); } };
      s.data = {values: it.rows};
      (s.layer || []).forEach(swap);
      s.width = it.w; s.height = it.h;
      s.params = [...(s.params || []), {name: 'mode', value: 'light'}];
      const view = new vega.View(vega.parse(vl.compile(s).spec), {renderer: 'none'});
      const svg = await view.toSVG();
      html += `<div style="${box}">${svg}</div>`; ok++;
    } catch (e) { fail++; console.log('FAIL', it.name, e.message.slice(0, 400)); html += `<div style="${box}border:2px solid red;color:red;font-size:12px;padding:8px">FAIL ${it.name}: ${e.message.slice(0, 300)}</div>`; }
  } else if (it.type === 'native') {
    html += `<div style="${box}border:1px dashed #C9D1DA;color:#5B6670;font-size:12px;padding:10px;box-sizing:border-box"><b>${it.title || it.wt}</b><br>[nativo: ${it.wt}]</div>`;
  } else {
    html += `<div style="${box}padding:8px;font-size:12px;color:#333;white-space:pre-wrap">${it.text}</div>`;
  }
}
fs.writeFileSync(outPath, html + '</div></body></html>');
console.log(`render ok=${ok} fail=${fail}`);
