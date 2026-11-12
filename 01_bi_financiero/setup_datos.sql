-- Datos sintéticos para el tablero BI Financiero (Vega-Lite). Reemplazar TU_CATALOGO.TU_ESQUEMA o usar preparar.py
CREATE SCHEMA IF NOT EXISTS TU_CATALOGO.TU_ESQUEMA
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.aux_dim_cuenta COMMENT 'Catalogo de cuentas sintetico (generador)' AS
SELECT * FROM VALUES
  ('4101', 'Ventas mostrador', 'Ingreso', 'Acreedora', 'R', 0.8, 0.02, 'S', 'Estado de resultados', 'Ingresos', 'Ventas netas', 'P&L gerencial', 'Ventas netas', 'Venta tienda', 'Ciclo de ingresos', 'Control clave', 'Acumulable', 'IVA 0%', 'Sin IEPS'),
  ('4102', 'Ventas digitales y a domicilio', 'Ingreso', 'Acreedora', 'R', 0.13, 0.03, 'S', 'Estado de resultados', 'Ingresos', 'Ventas netas', 'P&L gerencial', 'Ventas netas', 'Venta digital', 'Ciclo de ingresos', 'Control clave', 'Acumulable', 'IVA 0%', 'Sin IEPS'),
  ('4103', 'Ingresos por consultorio', 'Ingreso', 'Acreedora', 'R', 0.035, 0.01, 'S', 'Estado de resultados', 'Ingresos', 'Otros ingresos', 'P&L gerencial', 'Ventas netas', 'Servicios', 'Ciclo de ingresos', 'Control estándar', 'Acumulable', 'IVA 16%', 'Sin IEPS'),
  ('4201', 'Descuentos y devoluciones', 'Ingreso', 'Deudora', 'R', 0.028, 0.05, 'S', 'Estado de resultados', 'Ingresos', 'Ventas netas', 'P&L gerencial', 'Ventas netas', 'Descuentos', 'Ciclo de ingresos', 'Control clave', 'Acumulable', 'IVA 0%', 'Sin IEPS'),
  ('5101', 'Costo de medicamentos', 'Costo', 'Deudora', 'R', 0.5, 0.015, 'S', 'Estado de resultados', 'Costo de ventas', 'Costo de mercancía', 'P&L gerencial', 'Margen bruto', 'Costo medicamento', 'Ciclo de compras', 'Control clave', 'Deducible', 'IVA 0%', 'Sin IEPS'),
  ('5102', 'Costo de consumo y cuidado personal', 'Costo', 'Deudora', 'R', 0.095, 0.015, 'S', 'Estado de resultados', 'Costo de ventas', 'Costo de mercancía', 'P&L gerencial', 'Margen bruto', 'Costo consumo', 'Ciclo de compras', 'Control clave', 'Deducible', 'IVA 16%', 'IEPS 8%'),
  ('5201', 'Mermas y caducidades', 'Costo', 'Deudora', 'R', 0.012, 0.04, 'SC', 'Estado de resultados', 'Costo de ventas', 'Mermas', 'P&L gerencial', 'Margen bruto', 'Mermas', 'Ciclo de inventarios', 'Control clave', 'Deducible', 'No aplica', 'Sin IEPS'),
  ('6101', 'Sueldos y salarios', 'Gasto', 'Deudora', 'R', 0.07, 0.01, 'SCK', 'Estado de resultados', 'Gastos de operación', 'Personal', 'P&L gerencial', 'Gastos de tienda', 'Personal', 'Ciclo de nómina', 'Control clave', 'Deducible', 'No aplica', 'Sin IEPS'),
  ('6102', 'Prestaciones y cargas sociales', 'Gasto', 'Deudora', 'R', 0.032, 0.01, 'SCK', 'Estado de resultados', 'Gastos de operación', 'Personal', 'P&L gerencial', 'Gastos de tienda', 'Personal', 'Ciclo de nómina', 'Control estándar', 'Deducible', 'No aplica', 'Sin IEPS'),
  ('6201', 'Renta de locales', 'Gasto', 'Deudora', 'R', 0.04, 0.0, 'SCK', 'Estado de resultados', 'Gastos de operación', 'Ocupación', 'P&L gerencial', 'Gastos de tienda', 'Ocupación', 'Ciclo de compras', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6202', 'Energía eléctrica', 'Gasto', 'Deudora', 'R', 0.013, 0.0, 'SCK', 'Estado de resultados', 'Gastos de operación', 'Ocupación', 'P&L gerencial', 'Gastos de tienda', 'Ocupación', 'Ciclo de compras', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6203', 'Mantenimiento de tiendas', 'Gasto', 'Deudora', 'R', 0.009, 0.02, 'SC', 'Estado de resultados', 'Gastos de operación', 'Ocupación', 'P&L gerencial', 'Gastos de tienda', 'Ocupación', 'Ciclo de compras', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6301', 'Seguridad y traslado de valores', 'Gasto', 'Deudora', 'R', 0.006, 0.0, 'S', 'Estado de resultados', 'Gastos de operación', 'Seguridad', 'P&L gerencial', 'Gastos de tienda', 'Seguridad', 'Ciclo de tesorería', 'Control clave', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6302', 'Publicidad y mercadotecnia', 'Gasto', 'Deudora', 'R', 0.011, 0.0, 'K', 'Estado de resultados', 'Gastos de operación', 'Comercial', 'P&L gerencial', 'Gastos corporativos', 'Mercadotecnia', 'Ciclo de compras', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6303', 'Comisiones bancarias y terminales', 'Gasto', 'Deudora', 'R', 0.009, 0.0, 'S', 'Estado de resultados', 'Gastos de operación', 'Comercial', 'P&L gerencial', 'Gastos de tienda', 'Comisiones', 'Ciclo de tesorería', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6304', 'Fletes y distribución', 'Gasto', 'Deudora', 'R', 0.016, 0.01, 'C', 'Estado de resultados', 'Gastos de operación', 'Logística', 'P&L gerencial', 'Gastos de logística', 'Fletes', 'Ciclo de compras', 'Control estándar', 'Deducible', 'IVA 16%', 'Sin IEPS'),
  ('6401', 'Depreciación y amortización', 'Gasto', 'Deudora', 'R', 0.014, 0.0, 'SCK', 'Estado de resultados', 'Gastos de operación', 'Depreciación', 'P&L gerencial', 'D&A', 'Depreciación', 'Ciclo de activos fijos', 'Control estándar', 'Deducible', 'No aplica', 'Sin IEPS'),
  ('7101', 'Intereses y resultado cambiario', 'Gasto', 'Deudora', 'R', 0.006, 0.15, 'K', 'Estado de resultados', 'Resultado financiero', 'Financieros', 'P&L gerencial', 'Financieros', 'Intereses', 'Ciclo de tesorería', 'Control clave', 'Deducible', 'No aplica', 'Sin IEPS'),
  ('1101', 'Caja y bancos', 'Activo', 'Deudora', 'B', 0.95, 0.0, 'SCK', 'Balance general', 'Activo', 'Activo circulante', 'Capital de trabajo', 'Efectivo', 'Bancos', 'Ciclo de tesorería', 'Control clave', 'No aplica', 'No aplica', 'Sin IEPS'),
  ('1301', 'Inventario de mercancía', 'Activo', 'Deudora', 'B', 0.62, 0.0, 'SC', 'Balance general', 'Activo', 'Activo circulante', 'Capital de trabajo', 'Inventario', 'Inventario', 'Ciclo de inventarios', 'Control clave', 'No aplica', 'No aplica', 'Sin IEPS'),
  ('2101', 'Proveedores', 'Pasivo', 'Acreedora', 'B', 0.6, 0.0, 'CK', 'Balance general', 'Pasivo', 'Pasivo circulante', 'Capital de trabajo', 'Proveedores', 'Proveedores', 'Ciclo de compras', 'Control clave', 'No aplica', 'No aplica', 'Sin IEPS'),
  ('2201', 'Impuestos por pagar', 'Pasivo', 'Acreedora', 'B', 0.07, 0.0, 'K', 'Balance general', 'Pasivo', 'Pasivo circulante', 'Capital de trabajo', 'Impuestos', 'Impuestos', 'Ciclo fiscal', 'Control clave', 'No aplica', 'No aplica', 'Sin IEPS')
AS t(cuenta, descr_cuenta, tipo_de_cuenta, naturaleza, clase, share, contra, aplica, agrupador_1, agrupador_2, agrupador_3, agrupador_1_finanzas, agrupador_2_finanzas, agrupador_3_finanzas, agrupador_auditoria_1, agrupador_auditoria_2, f_pag_prov_isr, f_pag_prov_iva, f_pag_prov_ieps)
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.aux_dim_ceco COMMENT 'Catalogo de CECOs sintetico (generador)' AS
SELECT * FROM VALUES
  ('E001', 'Monterrey Cumbres', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Nuevo León', 'S5', 'Grande', 'CC001', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Monterrey NL', 'Nuevo León', 'Norte', 'Media', '2017-03-15', 'Activa', 3400000.0, 0.0),
  ('E002', 'Monterrey Valle', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Nuevo León', 'S5', 'Grande', 'CC002', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Grande', 'Plaza comercial', 'Si', '520', 'Si', 'Si', 'Si', 'Si', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Brinks', 'San Pedro NL', 'Nuevo León', 'Norte', 'Baja', '2016-08-01', 'Activa', 3900000.0, 0.0),
  ('E003', 'Saltillo Centro', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Coahuila', 'S5', 'Mediano', 'CC003', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Saltillo COAH', 'Coahuila', 'Norte', 'Baja', '2019-05-20', 'Activa', 1800000.0, 0.0),
  ('E004', 'Chihuahua Norte', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Chihuahua', 'S5', 'Mediano', 'CC004', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Mediano', 'Calle', 'No', '340', 'No', 'No', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'Chihuahua CHIH', 'Chihuahua', 'Norte', 'Media', '2020-02-10', 'Activa', 1700000.0, 0.0),
  ('E005', 'Hermosillo Periférico', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Sonora', 'S5', 'Mediano', 'CC005', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Mediano', 'Calle', 'No', '340', 'Si', 'Si', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Hermosillo SON', 'Sonora', 'Norte', 'Media', '2018-11-05', 'Activa', 1900000.0, 0.0),
  ('E006', 'Tijuana Río', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Norte', 'S4', 'Baja California', 'S5', 'Grande', 'CC006', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Norte', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Brinks', 'Tijuana BC', 'Baja California', 'Norte', 'Alta', '2019-09-12', 'Activa', 2900000.0, 0.0),
  ('E007', 'Guadalajara Chapultepec', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Occidente', 'S4', 'Jalisco', 'S5', 'Grande', 'CC007', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Occidente', 'Grande', 'Plaza comercial', 'Si', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Guadalajara JAL', 'Jalisco', 'Occidente', 'Media', '2015-06-01', 'Activa', 3500000.0, 0.0),
  ('E008', 'Zapopan Andares', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Occidente', 'S4', 'Jalisco', 'S5', 'Grande', 'CC008', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Occidente', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Brinks', 'Zapopan JAL', 'Jalisco', 'Occidente', 'Baja', '2018-04-18', 'Activa', 3700000.0, 0.0),
  ('E009', 'Morelia Centro', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Occidente', 'S4', 'Michoacán', 'S5', 'Mediano', 'CC009', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Occidente', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Prosegur', 'Morelia MICH', 'Michoacán', 'Occidente', 'Alta', '2021-01-25', 'Activa', 1500000.0, 0.0),
  ('E010', 'Culiacán Tres Ríos', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Occidente', 'S4', 'Sinaloa', 'S5', 'Mediano', 'CC010', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Occidente', 'Mediano', 'Calle', 'No', '340', 'No', 'No', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Brinks', 'Culiacán SIN', 'Sinaloa', 'Occidente', 'Alta', '2021-07-07', 'Activa', 1600000.0, 0.0),
  ('E011', 'León Campestre', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Bajío', 'S4', 'Guanajuato', 'S5', 'Grande', 'CC011', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Bajío', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'León GTO', 'Guanajuato', 'Bajío', 'Media', '2017-10-30', 'Activa', 2800000.0, 0.0),
  ('E012', 'Querétaro Juriquilla', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Bajío', 'S4', 'Querétaro', 'S5', 'Grande', 'CC012', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Bajío', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Brinks', 'Querétaro QRO', 'Querétaro', 'Bajío', 'Baja', '2018-02-14', 'Activa', 3000000.0, 0.0),
  ('E013', 'Aguascalientes Norte', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Bajío', 'S4', 'Aguascalientes', 'S5', 'Mediano', 'CC013', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Bajío', 'Mediano', 'Calle', 'Si', '340', 'No', 'Si', 'No', 'No', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Aguascalientes AGS', 'Aguascalientes', 'Bajío', 'Baja', '2020-06-03', 'Activa', 1600000.0, 0.0),
  ('E014', 'San Luis Potosí Carranza', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Bajío', 'S4', 'San Luis Potosí', 'S5', 'Express', 'CC014', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Bajío', 'Express', 'Hospital / clínica', 'No', '160', 'No', 'No', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'San Luis Potosí SLP', 'San Luis Potosí', 'Bajío', 'Media', '2022-03-22', 'Activa', 900000.0, 0.0),
  ('E015', 'CDMX Polanco', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Ciudad de México', 'S5', 'Grande', 'CC015', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Miguel Hidalgo CDMX', 'Ciudad de México', 'Centro', 'Media', '2014-09-09', 'Activa', 4400000.0, 0.0),
  ('E016', 'CDMX Roma', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Ciudad de México', 'S5', 'Mediano', 'CC016', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Mediano', 'Calle', 'No', '340', 'Si', 'Si', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'Cuauhtémoc CDMX', 'Ciudad de México', 'Centro', 'Media', '2016-01-19', 'Activa', 2200000.0, 0.0),
  ('E017', 'CDMX Coyoacán', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Ciudad de México', 'S5', 'Mediano', 'CC017', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Mediano', 'Calle', 'Si', '340', 'Si', 'Si', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Coyoacán CDMX', 'Ciudad de México', 'Centro', 'Media', '2015-11-11', 'Activa', 2400000.0, 0.0),
  ('E018', 'CDMX Santa Fe', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Ciudad de México', 'S5', 'Express', 'CC018', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Express', 'Hospital / clínica', 'No', '160', 'No', 'No', 'No', 'No', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Brinks', 'Cuajimalpa CDMX', 'Ciudad de México', 'Centro', 'Baja', '2023-02-01', 'Activa', 1200000.0, 0.0),
  ('E019', 'Toluca Metepec', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Estado de México', 'S5', 'Mediano', 'CC019', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Prosegur', 'Metepec MEX', 'Estado de México', 'Centro', 'Alta', '2019-03-03', 'Activa', 1900000.0, 0.0),
  ('E020', 'Naucalpan Satélite', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Estado de México', 'S5', 'Grande', 'CC020', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Brinks', 'Naucalpan MEX', 'Estado de México', 'Centro', 'Alta', '2017-05-27', 'Activa', 3100000.0, 0.0),
  ('E021', 'Puebla Angelópolis', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Puebla', 'S5', 'Grande', 'CC021', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Puebla PUE', 'Puebla', 'Centro', 'Media', '2018-08-08', 'Activa', 2700000.0, 0.0),
  ('E022', 'Cuernavaca Río Mayo', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Morelos', 'S5', 'Express', 'CC022', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Express', 'Hospital / clínica', 'No', '160', 'No', 'No', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Brinks', 'Cuernavaca MOR', 'Morelos', 'Centro', 'Alta', '2022-10-17', 'Activa', 1000000.0, 0.0),
  ('E023', 'Pachuca Centro', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Centro', 'S4', 'Hidalgo', 'S5', 'Express', 'CC023', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Centro', 'Express', 'Hospital / clínica', 'No', '160', 'No', 'No', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Pachuca HGO', 'Hidalgo', 'Centro', 'Media', '2023-06-12', 'Activa', 850000.0, 0.0),
  ('E024', 'Mérida Altabrisa', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sureste', 'S4', 'Yucatán', 'S5', 'Grande', 'CC024', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sureste', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'No', 'Si', '0', 'Terrestre', 'Si', 'Si', 'Brinks', 'Mérida YUC', 'Yucatán', 'Sureste', 'Baja', '2018-12-01', 'Activa', 2600000.0, 0.0),
  ('E025', 'Cancún Tulum Av', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sureste', 'S4', 'Quintana Roo', 'S5', 'Grande', 'CC025', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sureste', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Cancún QROO', 'Quintana Roo', 'Sureste', 'Media', '2019-04-15', 'Activa', 2900000.0, 0.0),
  ('E026', 'Playa del Carmen', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sureste', 'S4', 'Quintana Roo', 'S5', 'Express', 'CC026', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sureste', 'Express', 'Hospital / clínica', 'No', '160', 'Si', 'No', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'Solidaridad QROO', 'Quintana Roo', 'Sureste', 'Media', '2022-05-09', 'Activa', 1100000.0, 0.0),
  ('E027', 'Villahermosa Tabasco 2000', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sureste', 'S4', 'Tabasco', 'S5', 'Mediano', 'CC027', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sureste', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Prosegur', 'Villahermosa TAB', 'Tabasco', 'Sureste', 'Alta', '2020-09-21', 'Activa', 1500000.0, 0.0),
  ('E028', 'Veracruz Boca del Río', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sur', 'S4', 'Veracruz', 'S5', 'Grande', 'CC028', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sur', 'Grande', 'Plaza comercial', 'No', '520', 'Si', 'Si', 'Si', 'Si', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'Boca del Río VER', 'Veracruz', 'Sur', 'Media', '2017-07-04', 'Activa', 2500000.0, 0.0),
  ('E029', 'Xalapa Ánimas', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sur', 'S4', 'Veracruz', 'S5', 'Mediano', 'CC029', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sur', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Prosegur', 'Xalapa VER', 'Veracruz', 'Sur', 'Media', '2021-03-30', 'Activa', 1400000.0, 0.0),
  ('E030', 'Oaxaca Reforma', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sur', 'S4', 'Oaxaca', 'S5', 'Express', 'CC030', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sur', 'Express', 'Hospital / clínica', 'No', '160', 'No', 'No', 'No', 'No', 'Si', 'Si', '1', 'Terrestre', 'Si', 'Si', 'Brinks', 'Oaxaca OAX', 'Oaxaca', 'Sur', 'Media', '2022-08-16', 'Activa', 950000.0, 0.0),
  ('E031', 'Tuxtla Gutiérrez Oriente', 'Farmatodo', 'FTD', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sur', 'S4', 'Chiapas', 'S5', 'Mediano', 'CC031', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sur', 'Mediano', 'Calle', 'No', '340', 'No', 'Si', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Prosegur', 'Tuxtla Gutiérrez CHIS', 'Chiapas', 'Sur', 'Alta', '2021-11-02', 'Activa', 1300000.0, 0.0),
  ('E032', 'Acapulco Costera', 'Farmatodo', 'FTD Express', 'S', 'S1', 'Retail', 'S2', 'Farmacias', 'S3', 'Sur', 'S4', 'Guerrero', 'S5', 'Express', 'CC032', 'CCH01', 'Tiendas', 'A01', 'Operación de tiendas', 'Farmacias', 'Cadena Sur', 'Express', 'Hospital / clínica', 'No', '160', 'Si', 'No', 'No', 'No', 'Si', 'Si', '2', 'Blindado', 'Si', 'Si', 'Brinks', 'Acapulco GRO', 'Guerrero', 'Sur', 'Alta', '2023-01-20', 'Activa', 900000.0, 0.0),
  ('E033', 'CEDIS Centro (Tepotzotlán)', 'Farmatodo Servicios', 'FTS', 'C', 'S1', 'Distribución', 'S2', 'Logística', 'S3', 'Centro', 'S4', 'Estado de México', 'S5', 'CEDIS', 'CC033', 'CCH02', 'Centros de distribución', 'A02', 'Logística y distribución', 'Logística', 'Red CEDIS', 'CEDIS', 'CEDIS', 'Si', '18000', 'Si', 'No', 'No', 'No', 'Si', 'Si', '3', 'No aplica', 'No', 'No', 'N/A', 'Tepotzotlán MEX', 'Estado de México', 'Centro', 'Media', '2014-01-10', 'Activa', 5000000.0, 0.0),
  ('E034', 'CEDIS Norte (Apodaca)', 'Farmatodo Servicios', 'FTS', 'C', 'S1', 'Distribución', 'S2', 'Logística', 'S3', 'Norte', 'S4', 'Nuevo León', 'S5', 'CEDIS', 'CC034', 'CCH02', 'Centros de distribución', 'A02', 'Logística y distribución', 'Logística', 'Red CEDIS', 'CEDIS', 'CEDIS', 'No', '18000', 'Si', 'No', 'No', 'No', 'Si', 'Si', '3', 'No aplica', 'No', 'No', 'N/A', 'Apodaca NL', 'Nuevo León', 'Norte', 'Media', '2017-01-16', 'Activa', 3000000.0, 0.0),
  ('E035', 'CEDIS Occidente (El Salto)', 'Farmatodo Servicios', 'FTS', 'C', 'S1', 'Distribución', 'S2', 'Logística', 'S3', 'Occidente', 'S4', 'Jalisco', 'S5', 'CEDIS', 'CC035', 'CCH02', 'Centros de distribución', 'A02', 'Logística y distribución', 'Logística', 'Red CEDIS', 'CEDIS', 'CEDIS', 'No', '18000', 'Si', 'No', 'No', 'No', 'Si', 'Si', '3', 'No aplica', 'No', 'No', 'N/A', 'El Salto JAL', 'Jalisco', 'Occidente', 'Media', '2018-06-11', 'Activa', 2500000.0, 0.0),
  ('E036', 'Corporativo', 'Farmatodo Servicios', 'FTS', 'K', 'S1', 'Soporte', 'S2', 'Corporativo', 'S3', 'Centro', 'S4', 'Ciudad de México', 'S5', 'Corporativo', 'CC036', 'CCH03', 'Corporativo', 'A03', 'Administración central', 'Corporativo', 'Corporativo', 'Corporativo', 'Oficina', 'No', '2400', 'No', 'No', 'No', 'No', 'Si', 'Si', '0', 'No aplica', 'No', 'No', 'N/A', 'Miguel Hidalgo CDMX', 'Ciudad de México', 'Centro', 'Baja', '2014-01-01', 'Activa', 18000000.0, 0.0)
AS t(entidad, descr_entidad, compania, submarca, tipo, seg_1, desc_seg_1, seg_2, desc_seg_2, seg_3, desc_seg_3, seg_4, desc_seg_4, seg_5, desc_seg_5, ceco, cc_homologado, nombre_homologado, area_homologada, nombre_de_area_homologada, unidad_de_negocio, cadena, formato, tipo_de_sucursal, inmueble_propio, m2, h24, consultorio, espacio_subarrendamiento, cajero_automatico, monitoreo_alarma, cctv, vigilantes, tipo_traslado, cofre_seguridad, traslado_de_valores, empresa_de_traslado, ubicacion, estado, zona_cluster, zona_de_riesgo, fecha_de_apertura, control_de_operaciones, size, bias)
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.aux_movimientos COMMENT 'Movimientos sinteticos base (generador)' AS
WITH meses AS (
  SELECT m AS mes, year(m) AS y, month(m) AS mo
  FROM (SELECT explode(sequence(DATE'2025-01-01', DATE'2026-09-01', INTERVAL 1 MONTH)) AS m)
),
origenes AS (SELECT * FROM VALUES ('Dynamics', 1.0), ('Ajustes de cierre', 0.06) AS o(origen, peso)),
base AS (
  SELECT ms.mes, ms.y, ms.mo, o.origen, o.peso, c.*, k.entidad, k.descr_entidad, k.size, k.tipo AS tipo_ceco,
         k.compania, k.formato,
         -- estacionalidad farmacéutica: pico invernal (respiratorias) y valle de verano
         1 + 0.10 * cos(2 * pi() * (ms.mo - 1) / 12) + 0.03 * cos(4 * pi() * (ms.mo - 1) / 12) AS season,
         CASE WHEN ms.y = 2026 THEN 1.075 ELSE 1.0 END AS growth,
         -- desempeño real por CECO (estable) y ruido mensual
         0.90 + 0.20 * (abs(xxhash64(concat_ws('|', k.entidad, 'perf'))) % 100000) / 100000.0 AS perf_ceco,
         0.92 + 0.16 * (abs(xxhash64(concat_ws('|', k.entidad, c.cuenta, cast(ms.mes as string), o.origen, 'noise'))) % 100000) / 100000.0 AS ruido,
         -- sesgo del presupuesto por CECO/cuenta (metas optimistas o conservadoras)
         0.94 + 0.13 * (abs(xxhash64(concat_ws('|', k.entidad, c.cuenta, 'ppto'))) % 100000) / 100000.0 AS sesgo_ppto,
         -- deriva de saldos de balance
         -0.06 + 0.13 * (abs(xxhash64(concat_ws('|', k.entidad, c.cuenta, cast(ms.mes as string), 'drift'))) % 100000) / 100000.0 AS deriva
  FROM meses ms
  CROSS JOIN TU_CATALOGO.TU_ESQUEMA.aux_dim_cuenta c
  CROSS JOIN TU_CATALOGO.TU_ESQUEMA.aux_dim_ceco k
  CROSS JOIN origenes o
  WHERE instr(c.aplica, k.tipo) > 0
    AND (o.origen = 'Dynamics' OR c.cuenta IN ('5201', '6102', '6401'))
),
montos AS (
  SELECT *,
    -- monto real y presupuesto del mes (positivo); corporativo/CEDIS usan su propia escala
    size * share * peso * season * growth * perf_ceco * ruido AS amt,
    size * share * peso * season * (CASE WHEN y = 2026 THEN 1.10 ELSE 1.03 END) * sesgo_ppto AS amt_ppto
  FROM base
)
SELECT mes, y, mo, origen, cuenta, descr_cuenta, naturaleza, clase, contra, entidad, compania,
  CASE WHEN clase = 'B' THEN amt * (1 + deriva / 2)
       WHEN naturaleza = 'Deudora' THEN amt * (1 + contra) ELSE amt * contra END AS cargo,
  CASE WHEN clase = 'B' THEN amt * (1 - deriva / 2)
       WHEN naturaleza = 'Deudora' THEN amt * contra ELSE amt * (1 + contra) END AS abono,
  CASE WHEN clase = 'B' THEN amt_ppto * 1.0025 WHEN naturaleza = 'Deudora' THEN amt_ppto * (1 + contra)
       ELSE amt_ppto * contra END AS cargo_ppto,
  CASE WHEN clase = 'B' THEN amt_ppto * 0.9975 WHEN naturaleza = 'Deudora' THEN amt_ppto * contra
       ELSE amt_ppto * (1 + contra) END AS abono_ppto,
  CASE WHEN clase = 'B' THEN size * share * 1.6 ELSE 0 END AS saldo_apertura
FROM montos
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_puente
COMMENT 'Puente de dimensiones (spine). Datos sinteticos con el contrato del reporte BI Financiero' AS
SELECT
  cast(m.y AS STRING) AS anio,
  lpad(cast(m.mo AS STRING), 2, '0') AS periodo,
  m.origen AS origen,
  k.compania AS compania,
  k.submarca AS submarca,
  c.cuenta AS cuenta,
  c.descr_cuenta AS descr_cuenta,
  k.entidad AS entidad,
  k.descr_entidad AS descr_entidad,
  k.seg_1 AS seg_1,
  k.desc_seg_1 AS desc_seg_1,
  k.seg_2 AS seg_2,
  k.desc_seg_2 AS desc_seg_2,
  k.seg_3 AS seg_3,
  k.desc_seg_3 AS desc_seg_3,
  k.seg_4 AS seg_4,
  k.desc_seg_4 AS desc_seg_4,
  k.seg_5 AS seg_5,
  k.desc_seg_5 AS desc_seg_5,
  k.ceco AS ceco,
  k.cc_homologado AS cc_homologado,
  k.nombre_homologado AS nombre_homologado,
  k.area_homologada AS area_homologada,
  k.nombre_de_area_homologada AS nombre_de_area_homologada,
  k.unidad_de_negocio AS unidad_de_negocio,
  k.cadena AS cadena,
  k.formato AS formato,
  k.tipo_de_sucursal AS tipo_de_sucursal,
  k.inmueble_propio AS inmueble_propio,
  k.m2 AS m2,
  k.h24 AS `24_hrs`,
  k.consultorio AS consultorio,
  k.espacio_subarrendamiento AS espacio_subarrendamiento,
  k.cajero_automatico AS cajero_automatico,
  k.monitoreo_alarma AS monitoreo_alarma,
  k.cctv AS cctv,
  k.vigilantes AS vigilantes,
  k.tipo_traslado AS tipo_traslado,
  k.cofre_seguridad AS cofre_seguridad,
  k.traslado_de_valores AS traslado_de_valores,
  k.empresa_de_traslado AS empresa_de_traslado,
  k.ubicacion AS ubicacion,
  k.estado AS estado,
  k.zona_cluster AS zona_cluster,
  k.zona_de_riesgo AS zona_de_riesgo,
  to_timestamp(k.fecha_de_apertura) AS fecha_de_apertura,
  CAST(NULL AS TIMESTAMP) AS fecha_de_cierre,
  k.control_de_operaciones AS control_de_operaciones,
  CASE WHEN k.tipo = 'S' THEN 'Tiendas comparables' ELSE 'No tiendas' END AS nivel_29,
  CASE WHEN k.fecha_de_apertura < '2022-01-01' THEN 'Madura' ELSE 'En maduración' END AS nivel_30,
  concat('Cohorte ', substr(k.fecha_de_apertura, 1, 4)) AS nivel_31,
  'Consolidado MX' AS nivel_32,
  c.agrupador_1 AS agrupador_1,
  c.agrupador_2 AS agrupador_2,
  c.agrupador_3 AS agrupador_3,
  concat(c.cuenta, ' ', c.descr_cuenta) AS agrupador_4,
  c.agrupador_1_finanzas AS agrupador_1_finanzas,
  c.agrupador_2_finanzas AS agrupador_2_finanzas,
  c.agrupador_3_finanzas AS agrupador_3_finanzas,
  c.agrupador_3_finanzas AS agrupador_4_finanzas,
  CASE WHEN k.compania = 'Farmatodo Servicios' THEN 'ICIAS-FTS' ELSE 'ICIAS-FTD' END AS icias,
  c.tipo_de_cuenta AS tipo_de_cuenta,
  c.naturaleza AS naturaleza,
  c.agrupador_auditoria_1 AS agrupador_auditoria_1,
  c.agrupador_auditoria_2 AS agrupador_auditoria_2,
  CASE WHEN c.agrupador_auditoria_2 = 'Control clave' THEN 'Revisión mensual' ELSE 'Revisión trimestral' END AS agrupador_auditoria_3,
  c.f_pag_prov_isr AS f_pag_prov_isr,
  c.f_pag_prov_iva AS f_pag_prov_iva,
  c.f_pag_prov_ieps AS f_pag_prov_ieps,
  CASE WHEN c.cuenta = '2201' THEN 'Saldo a favor IVA' ELSE 'No aplica' END AS f_slds_a_favor,
  CASE WHEN c.cuenta IN ('6401', '1301') THEN 'Partida temporal' ELSE 'No aplica' END AS f_isr_diferido,
  CASE WHEN c.clase = 'R' THEN 'Declaración anual' ELSE 'Informativa' END AS f_decl_anual,
  CASE WHEN c.clase = 'B' THEN 'Monetaria' ELSE 'No aplica' END AS f_aj_anual_inf,
  'Pendiente' AS pendiente_1,
  'Pendiente' AS pendiente_2,
  'Pendiente' AS pendiente_3,
  row_number() OVER (ORDER BY m.mes, m.entidad, m.cuenta, m.origen) AS llave_id
FROM TU_CATALOGO.TU_ESQUEMA.aux_movimientos m
JOIN TU_CATALOGO.TU_ESQUEMA.aux_dim_cuenta c ON c.cuenta = m.cuenta
JOIN TU_CATALOGO.TU_ESQUEMA.aux_dim_ceco k ON k.entidad = m.entidad
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_balanza
COMMENT 'Balanza (saldos) sintetica. Cuadra: saldo_final = saldo_inicial + cargo - abono' AS
WITH mov AS (
  SELECT p.llave_id, m.*, round(m.cargo, 2) AS c2, round(m.abono, 2) AS a2
  FROM TU_CATALOGO.TU_ESQUEMA.aux_movimientos m
  JOIN TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_puente p
    ON p.anio = cast(m.y AS STRING) AND p.periodo = lpad(cast(m.mo AS STRING), 2, '0')
   AND p.entidad = m.entidad AND p.cuenta = m.cuenta AND p.origen = m.origen
),
acum AS (
  SELECT *,
    round(CASE WHEN clase = 'B' THEN (CASE WHEN naturaleza = 'Deudora' THEN saldo_apertura ELSE -saldo_apertura END)
                    + coalesce(sum(c2 - a2) OVER (PARTITION BY entidad, cuenta, origen ORDER BY mes
                                                  ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0)
               ELSE coalesce(sum(c2 - a2) OVER (PARTITION BY entidad, cuenta, origen, y ORDER BY mes
                                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) END, 2) AS si
  FROM mov
)
SELECT
  'Activa' AS status,
  CASE WHEN (abs(xxhash64(concat_ws('|', entidad, cuenta, 'bloq'))) % 100000) / 100000.0 < 0.03 THEN 'Inactiva' ELSE 'Activa' END AS estatus_cuenta,
  CASE WHEN clase = 'B' THEN 'Balance' ELSE 'Resultados' END AS estatus_segmento,
  'Activa' AS estatus_cuenta_entidad,
  CAST(add_months(mes, 1) + INTERVAL 4 DAYS + INTERVAL 6 HOURS AS TIMESTAMP) AS fecha_extraccion,
  CAST(si AS DECIMAL(18,2)) AS saldo_inicial,
  CAST(c2 AS DECIMAL(18,2)) AS cargo,
  CAST(a2 AS DECIMAL(18,2)) AS abono,
  CAST(c2 - a2 AS DECIMAL(18,2)) AS importe_neto,
  CAST(si + c2 - a2 AS DECIMAL(18,2)) AS saldo_final,
  CAST(c2 - a2 AS DECIMAL(18,2)) AS importe_convertido,
  llave_id
FROM acum
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_presupuesto
COMMENT 'Presupuesto (PPTO) sintetico, mismo grano que la balanza' AS
WITH mov AS (
  SELECT p.*, round(m.cargo_ppto, 2) AS c2, round(m.abono_ppto, 2) AS a2, m.mes, m.y, m.clase, m.saldo_apertura
  FROM TU_CATALOGO.TU_ESQUEMA.aux_movimientos m
  JOIN TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_puente p
    ON p.anio = cast(m.y AS STRING) AND p.periodo = lpad(cast(m.mo AS STRING), 2, '0')
   AND p.entidad = m.entidad AND p.cuenta = m.cuenta AND p.origen = m.origen
),
acum AS (
  SELECT *,
    round(CASE WHEN clase = 'B' THEN (CASE WHEN naturaleza = 'Deudora' THEN saldo_apertura ELSE -saldo_apertura END)
                    + coalesce(sum(c2 - a2) OVER (PARTITION BY entidad, cuenta, origen ORDER BY mes
                                                  ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0)
               ELSE coalesce(sum(c2 - a2) OVER (PARTITION BY entidad, cuenta, origen, y ORDER BY mes
                                                ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING), 0) END, 2) AS si
  FROM mov
)
SELECT origen, compania, submarca, entidad, descr_entidad, seg_1, desc_seg_1, seg_2, desc_seg_2, seg_3, desc_seg_3,
  seg_4, desc_seg_4, seg_5, desc_seg_5, cuenta, descr_cuenta, anio, periodo,
  CAST(si AS DECIMAL(18,2)) AS saldo_inicial_ppto,
  CAST(c2 AS DECIMAL(18,2)) AS cargo_ppto,
  CAST(a2 AS DECIMAL(18,2)) AS abono_ppto,
  CAST(c2 - a2 AS DECIMAL(18,2)) AS importe_neto_ppto,
  CAST(c2 - a2 AS DECIMAL(18,2)) AS importe_convertido_ppto,
  CAST(si + c2 - a2 AS DECIMAL(18,2)) AS saldo_final_ppto,
  llave_id,
  CAST(mes AS TIMESTAMP) - INTERVAL 30 DAYS AS _load_ts
FROM acum
;
CREATE OR REPLACE TABLE TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_auxiliares
COMMENT 'Auxiliares (polizas) sinteticos; por llave suman el cargo/abono de la balanza' AS
WITH b AS (
  SELECT b.llave_id, b.cargo, b.abono, p.anio, p.periodo, p.cuenta, p.tipo_de_cuenta, p.origen, p.entidad
  FROM TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_balanza b
  JOIN TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_puente p USING (llave_id)
),
lin AS (
  SELECT b.*, n,
    0.3 + (abs(xxhash64(concat_ws('|', cast(b.llave_id as string), cast(n as string), 'w'))) % 100000) / 100000.0 AS w
  FROM b LATERAL VIEW explode(sequence(1, 2 + CAST(abs(xxhash64(cast(llave_id AS STRING), 'n')) % 5 AS INT))) x AS n
),
pes AS (SELECT *, w / sum(w) OVER (PARTITION BY llave_id) AS f FROM lin),
cat AS (
  SELECT *,
    CASE WHEN tipo_de_cuenta = 'Ingreso' THEN 'AR' WHEN tipo_de_cuenta IN ('Costo') THEN 'INV'
         WHEN cuenta IN ('6101', '6102') THEN 'PR' WHEN tipo_de_cuenta = 'Gasto' THEN 'AP'
         WHEN origen = 'Ajustes de cierre' THEN 'GL' ELSE 'CM' END AS modulo,
    abs(xxhash64(cast(llave_id AS STRING), cast(n AS STRING), 'u')) % 6 AS u,
    abs(xxhash64(cast(llave_id AS STRING), cast(n AS STRING), 'p')) % 8 AS pv,
    abs(xxhash64(cast(llave_id AS STRING), cast(n AS STRING), 'd')) % 31 AS d
  FROM pes
)
SELECT
  CAST(date_add(make_date(CAST(anio AS INT), CAST(periodo AS INT), 1), CAST(d % day(last_day(make_date(CAST(anio AS INT), CAST(periodo AS INT), 1))) AS INT)) AS TIMESTAMP) + make_interval(0,0,0,0, 9 + CAST(u AS INT), 0, 0) AS fecha_contable,
  modulo AS modulo_transaccion,
  element_at(map('AR','Cuentas por cobrar','INV','Inventarios','PR','Nómina','AP','Cuentas por pagar','GL','Contabilidad general','CM','Tesorería'), modulo) AS descr_modulo,
  element_at(map('AR','FAC','INV','SAL','PR','NOM','AP','CXP','GL','AJU','CM','MOV'), modulo) AS tipo_transaccion,
  element_at(map('AR','Factura de venta','INV','Salida de almacén','PR','Póliza de nómina','AP','Factura de proveedor','GL','Asiento de ajuste','CM','Movimiento bancario'), modulo) AS nombre_transaccion,
  concat('POL-', anio, periodo, '-', lpad(cast(llave_id AS STRING), 6, '0')) AS id_poliza,
  concat(element_at(map('AR','Ventas ','INV','Costo ','PR','Nómina ','AP','Gastos ','GL','Cierre ','CM','Tesorería '), modulo), anio, '-', periodo) AS descr_poliza_cabecera_lote,
  concat('Línea ', n, ' cuenta ', cuenta, ' ', entidad) AS descr_poliza_linea,
  'P' AS estatus_lote, 'Publicado' AS descr_estatus_lote,
  concat('USR0', u + 1) AS id_usuario_posteo,
  element_at(array('Carlos López','María García','Juan Martínez','Ana Torres','Luis Hernández','Sofía Ramírez'), CAST(u AS INT) + 1) AS nombre_de_usuario_posteo,
  concat('TRX-', lpad(cast(llave_id AS STRING), 6, '0'), '-', n) AS id_transaccion_modulo,
  element_at(map('AR','Venta','INV','Consumo de inventario','PR','Dispersión de nómina','AP','Registro de factura','GL','Provisión','CM','Conciliación'), modulo) AS descr_transaccion_modulo,
  CAST(date_add(make_date(CAST(anio AS INT), CAST(periodo AS INT), 1), CAST(d % day(last_day(make_date(CAST(anio AS INT), CAST(periodo AS INT), 1))) AS INT)) AS TIMESTAMP) + make_interval(0,0,0,0, 8 + CAST(u AS INT), 30, 0) AS fecha_transaccion_modulo,
  concat('USR0', u + 1) AS id_usuario_transaccion_modulo,
  element_at(array('Carlos López','María García','Juan Martínez','Ana Torres','Luis Hernández','Sofía Ramírez'), CAST(u AS INT) + 1) AS nombre_usuario_transaccion_modulo,
  CASE WHEN modulo = 'AR' THEN concat('CTE-', 100 + pv) ELSE concat('PROV-', 200 + pv) END AS prov_cte,
  CASE WHEN modulo = 'AR' THEN element_at(array('Público en general','Aseguradora Vida Plena','Hospital San Ángel','Club Salud Empresarial','Convenio IMSS-B','Marketplace Rappi','Marketplace Mercado Libre','Corporativo Bienestar'), CAST(pv AS INT) + 1)
       ELSE element_at(array('Distribuidora Médica del Centro','Laboratorios Andes','Farmacéutica Polar','Logística Express MX','Servicios Integrales Norte','CFE Suministrador','Inmobiliaria Plaza','Seguridad Privada Alfa'), CAST(pv AS INT) + 1) END AS nombre_prov_cte,
  CASE WHEN pv = 0 THEN 'Abierto' ELSE 'Cerrado' END AS estatus_documento,
  CASE WHEN pv = 0 THEN 'Documento abierto' ELSE 'Documento cerrado' END AS descr_estatus_documento,
  concat('DOC-', lpad(cast(llave_id AS STRING), 6, '0'), '-', n) AS folio_documento,
  CAST(round(cargo * f, 2) AS DECIMAL(18,2)) AS cargo_aux,
  CAST(round(abono * f, 2) AS DECIMAL(18,2)) AS abono_aux,
  CAST(round(cargo * f, 2) - round(abono * f, 2) AS DECIMAL(18,2)) AS importe_neto_aux,
  CAST(round(cargo * f, 2) - round(abono * f, 2) AS DECIMAL(18,2)) AS importe_convertido_aux,
  llave_id
FROM cat
;
CREATE OR REPLACE VIEW TU_CATALOGO.TU_ESQUEMA.bi_financiero
COMMENT 'BI Financiero - Financial metrics with balanza, presupuesto, and auxiliares domains'
WITH METRICS
LANGUAGE YAML
AS
$$
version: 1.1

source: TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_puente

joins:
  - name: balanza
    source: TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_balanza
    "on": source.llave_id = balanza.llave_id
    cardinality: one_to_many
  - name: presupuesto
    source: TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_presupuesto
    "on": source.llave_id = presupuesto.llave_id
    cardinality: one_to_many
  - name: auxiliares
    source: TU_CATALOGO.TU_ESQUEMA.dev_bi_financiero_vw_pbi_auxiliares
    "on": source.llave_id = auxiliares.llave_id
    cardinality: one_to_many

comment: "BI Financiero - Financial metrics with balanza, presupuesto, and auxiliares\
  \ domains"

dimensions:
  - name: anio
    expr: source.anio
    display_name: Año

  - name: periodo
    expr: source.periodo
    display_name: Periodo

  - name: origen
    expr: source.origen
    display_name: Origen

  - name: compania
    expr: source.compania
    display_name: Compañía

  - name: submarca
    expr: source.submarca
    display_name: Submarca

  - name: cuenta
    expr: source.cuenta
    display_name: Cuenta

  - name: descr_cuenta
    expr: source.descr_cuenta
    display_name: Descripción de Cuenta

  - name: entidad
    expr: source.entidad
    display_name: Entidad

  - name: descr_entidad
    expr: source.descr_entidad
    display_name: Descripción de Entidad

  - name: ceco
    expr: source.ceco
    display_name: CECO

  - name: cc_homologado
    expr: source.cc_homologado
    display_name: CC Homologado

  - name: nombre_homologado
    expr: source.nombre_homologado
    display_name: Nombre Homologado

  - name: area_homologada
    expr: source.area_homologada
    display_name: Área Homologada

  - name: nombre_de_area_homologada
    expr: source.nombre_de_area_homologada
    display_name: Nombre de Área Homologada

  - name: unidad_de_negocio
    expr: source.unidad_de_negocio
    display_name: Unidad de Negocio

  - name: cadena
    expr: source.cadena
    display_name: Cadena

  - name: formato
    expr: source.formato
    display_name: Formato

  - name: estado
    expr: source.estado
    display_name: Estado

  - name: zona_cluster
    expr: source.zona_cluster
    display_name: Zona Cluster

  - name: zona_de_riesgo
    expr: source.zona_de_riesgo
    display_name: Zona de Riesgo

  - name: icias
    expr: source.icias
    display_name: ICIAS

  - name: tipo_de_cuenta
    expr: source.tipo_de_cuenta
    display_name: Tipo de Cuenta

  - name: seg_1
    expr: source.`seg_1`
    display_name: Seg 1

  - name: desc_seg_1
    expr: source.`desc_seg_1`
    display_name: Desc seg 1

  - name: seg_2
    expr: source.`seg_2`
    display_name: Seg 2

  - name: desc_seg_2
    expr: source.`desc_seg_2`
    display_name: Desc seg 2

  - name: seg_3
    expr: source.`seg_3`
    display_name: Seg 3

  - name: desc_seg_3
    expr: source.`desc_seg_3`
    display_name: Desc seg 3

  - name: seg_4
    expr: source.`seg_4`
    display_name: Seg 4

  - name: desc_seg_4
    expr: source.`desc_seg_4`
    display_name: Desc seg 4

  - name: seg_5
    expr: source.`seg_5`
    display_name: Seg 5

  - name: desc_seg_5
    expr: source.`desc_seg_5`
    display_name: Desc seg 5

  - name: tipo_de_sucursal
    expr: source.`tipo_de_sucursal`
    display_name: Tipo de sucursal

  - name: inmueble_propio
    expr: source.`inmueble_propio`
    display_name: Inmueble propio

  - name: m2
    expr: source.`m2`
    display_name: M2

  - name: d_24_hrs
    expr: source.`24_hrs`
    display_name: 24 hrs

  - name: consultorio
    expr: source.`consultorio`
    display_name: Consultorio

  - name: espacio_subarrendamiento
    expr: source.`espacio_subarrendamiento`
    display_name: Espacio subarrendamiento

  - name: cajero_automatico
    expr: source.`cajero_automatico`
    display_name: Cajero automatico

  - name: monitoreo_alarma
    expr: source.`monitoreo_alarma`
    display_name: Monitoreo alarma

  - name: cctv
    expr: source.`cctv`
    display_name: Cctv

  - name: vigilantes
    expr: source.`vigilantes`
    display_name: Vigilantes

  - name: tipo_traslado
    expr: source.`tipo_traslado`
    display_name: Tipo traslado

  - name: cofre_seguridad
    expr: source.`cofre_seguridad`
    display_name: Cofre seguridad

  - name: traslado_de_valores
    expr: source.`traslado_de_valores`
    display_name: Traslado de valores

  - name: empresa_de_traslado
    expr: source.`empresa_de_traslado`
    display_name: Empresa de traslado

  - name: ubicacion
    expr: source.`ubicacion`
    display_name: Ubicacion

  - name: fecha_de_apertura
    expr: source.`fecha_de_apertura`
    display_name: Fecha de apertura

  - name: control_de_operaciones
    expr: source.`control_de_operaciones`
    display_name: Control de operaciones

  - name: nivel_29
    expr: source.`nivel_29`
    display_name: Nivel 29

  - name: nivel_30
    expr: source.`nivel_30`
    display_name: Nivel 30

  - name: nivel_31
    expr: source.`nivel_31`
    display_name: Nivel 31

  - name: nivel_32
    expr: source.`nivel_32`
    display_name: Nivel 32

  - name: agrupador_1
    expr: source.`agrupador_1`
    display_name: Agrupador 1

  - name: agrupador_2
    expr: source.`agrupador_2`
    display_name: Agrupador 2

  - name: agrupador_3
    expr: source.`agrupador_3`
    display_name: Agrupador 3

  - name: agrupador_4
    expr: source.`agrupador_4`
    display_name: Agrupador 4

  - name: agrupador_1_finanzas
    expr: source.`agrupador_1_finanzas`
    display_name: Agrupador 1 finanzas

  - name: agrupador_2_finanzas
    expr: source.`agrupador_2_finanzas`
    display_name: Agrupador 2 finanzas

  - name: agrupador_3_finanzas
    expr: source.`agrupador_3_finanzas`
    display_name: Agrupador 3 finanzas

  - name: agrupador_4_finanzas
    expr: source.`agrupador_4_finanzas`
    display_name: Agrupador 4 finanzas

  - name: naturaleza
    expr: source.`naturaleza`
    display_name: Naturaleza

  - name: agrupador_auditoria_1
    expr: source.`agrupador_auditoria_1`
    display_name: Agrupador auditoria 1

  - name: agrupador_auditoria_2
    expr: source.`agrupador_auditoria_2`
    display_name: Agrupador auditoria 2

  - name: agrupador_auditoria_3
    expr: source.`agrupador_auditoria_3`
    display_name: Agrupador auditoria 3

  - name: f_pag_prov_isr
    expr: source.`f_pag_prov_isr`
    display_name: F pag prov isr

  - name: f_pag_prov_iva
    expr: source.`f_pag_prov_iva`
    display_name: F pag prov iva

  - name: f_pag_prov_ieps
    expr: source.`f_pag_prov_ieps`
    display_name: F pag prov ieps

  - name: f_slds_a_favor
    expr: source.`f_slds_a_favor`
    display_name: F slds a favor

  - name: f_isr_diferido
    expr: source.`f_isr_diferido`
    display_name: F isr diferido

  - name: f_decl_anual
    expr: source.`f_decl_anual`
    display_name: F decl anual

  - name: f_aj_anual_inf
    expr: source.`f_aj_anual_inf`
    display_name: F aj anual inf

  - name: pendiente_1
    expr: source.`pendiente_1`
    display_name: Pendiente 1

  - name: pendiente_2
    expr: source.`pendiente_2`
    display_name: Pendiente 2

  - name: pendiente_3
    expr: source.`pendiente_3`
    display_name: Pendiente 3

measures:
  - name: 01 Saldo Inicial
    expr: SUM(balanza.saldo_inicial)
    display_name: Saldo Inicial
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 02 Cargos
    expr: SUM(balanza.cargo)
    display_name: Cargos
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 03 Abonos
    expr: SUM(balanza.abono)
    display_name: Abonos
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 04 Saldo Final
    expr: SUM(balanza.saldo_final)
    display_name: Saldo Final
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 05 Importe Neto (Cargos-Abonos)
    expr: SUM(balanza.importe_neto)
    display_name: Importe Neto (Cargos-Abonos)
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 06 Importe Convertido
    expr: SUM(balanza.importe_convertido)
    display_name: Importe Convertido
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 07 Saldo Inicial PPTO
    expr: SUM(presupuesto.saldo_inicial_ppto)
    display_name: Saldo Inicial PPTO
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 08 Cargos PPTO
    expr: SUM(presupuesto.cargo_ppto)
    display_name: Cargos PPTO
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 09 Abonos PPTO
    expr: SUM(presupuesto.abono_ppto)
    display_name: Abonos PPTO
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 10 Saldo Final PPTO
    expr: SUM(presupuesto.saldo_final_ppto)
    display_name: Saldo Final PPTO
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 11 Importe Neto PPTO (Cargos-Abonos)
    expr: SUM(presupuesto.importe_neto_ppto)
    display_name: Importe Neto PPTO (Cargos-Abonos)
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 12 Importe Convertido PPTO
    expr: SUM(presupuesto.importe_convertido_ppto)
    display_name: Importe Convertido PPTO
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 13 Var vs PPTO $
    expr: (MEASURE(`06 Importe Convertido`) - MEASURE(`12 Importe Convertido PPTO`))
      * -1
    display_name: Var vs PPTO $
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 14 Alcance vs PPTO
    expr: |-
      CASE
        WHEN MEASURE(`12 Importe Convertido PPTO`) = 0 THEN NULL
        ELSE MEASURE(`06 Importe Convertido`) / MEASURE(`12 Importe Convertido PPTO`)
      END
    display_name: Alcance vs PPTO
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2

  - name: 15 Var vs PPTO %
    expr: |-
      CASE
        WHEN MEASURE(`12 Importe Convertido PPTO`) = 0 THEN NULL
        ELSE MEASURE(`06 Importe Convertido`) / MEASURE(`12 Importe Convertido PPTO`) - 1
      END
    display_name: Var vs PPTO %
    format:
      type: percentage
      decimal_places:
        type: exact
        places: 2

  - name: 01 Cargo Aux
    expr: SUM(auxiliares.cargo_aux)
    display_name: Cargo Aux
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 02 Abono Aux
    expr: SUM(auxiliares.abono_aux)
    display_name: Abono Aux
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 03 Importe Neto Aux
    expr: SUM(auxiliares.importe_neto_aux)
    display_name: Importe Neto Aux
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: 04 Importe Convertido Aux
    expr: SUM(auxiliares.importe_convertido_aux)
    display_name: Importe Convertido Aux
    format:
      type: number
      decimal_places:
        type: exact
        places: 2

  - name: Act BD
    expr: "CONCAT('Actualizacion BD ', CAST(MAX(balanza.fecha_extraccion) AS STRING))"
    display_name: Actualización BD
$$
;
