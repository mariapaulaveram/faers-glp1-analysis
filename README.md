# 💊 FAERS Adverse Event Analysis — GLP-1 Agonists
## Pharmacovigilance Dashboard | Ozempic · Victoza · Trulicity · Byetta

Real-world pharmacovigilance analysis of adverse events reported to the FDA for GLP-1 receptor agonists (semaglutide/Ozempic, liraglutide, dulaglutide, exenatide), using the public openFDA API (FAERS database).

🔗 **[Ver dashboard interactivo](https://mariapaulaveram.github.io/faers-glp1-analysis/)**

---

## ¿Qué hace este proyecto?

Descarga datos reales de eventos adversos del sistema FAERS (FDA Adverse Event Reporting System) a través de la API pública de openFDA, los procesa y los presenta en un dashboard interactivo con filtros en tiempo real.

Es un análisis de farmacovigilancia real — el mismo tipo de revisión que realizan equipos de Drug Safety y Clinical Data Management en la industria farmacéutica.

> ⚠️ **Disclaimer:** Los datos provienen del sistema FAERS de la FDA a través de openFDA. Los reportes son de carácter voluntario y pueden contener duplicados o información incompleta. Este proyecto es de uso educativo y de portfolio. No constituye asesoramiento médico ni regulatorio.

---

## Drogas analizadas

| Nombre genérico | Nombres comerciales | Clase |
|----------------|---------------------|-------|
| Semaglutide | Ozempic, Wegovy, Rybelsus | GLP-1 RA |
| Liraglutide | Victoza, Saxenda | GLP-1 RA |
| Dulaglutide | Trulicity | GLP-1 RA |
| Exenatide | Byetta, Bydureon | GLP-1 RA |

---

## Estructura del proyecto

```
faers-glp1-analysis/
│
├── main.py           ← Punto de entrada. Ejecuta el pipeline completo
├── fetch_data.py     ← Paso 1: descarga datos reales de openFDA API
├── analyze.py        ← Paso 2: procesa y analiza los eventos adversos
├── dashboard.py      ← Paso 3: genera el dashboard HTML interactivo
│
├── faers_glp1_raw.csv          ← generado automáticamente
├── faers_top_reactions.csv     ← generado automáticamente
├── faers_reactions_by_drug.csv ← generado automáticamente
├── faers_sex_dist.csv          ← generado automáticamente
├── faers_outcome_dist.csv      ← generado automáticamente
├── faers_yearly.csv            ← generado automáticamente
├── faers_age_dist.csv          ← generado automáticamente
├── faers_serious.csv           ← generado automáticamente
└── index.html                  ← generado automáticamente (GitHub Pages ready)
```

---

## Cómo ejecutarlo

### Requisitos
- Python 3.8 o superior
- Conexión a internet (solo para el Paso 1)
- Librerías: requests, pandas, numpy

```bash
pip install requests pandas numpy
```

### Ejecución completa (recomendado la primera vez)
Abrí una terminal en la carpeta del proyecto y ejecutá:

```bash
python main.py
```

Esto corre los 3 pasos en orden automáticamente. La primera vez tarda 2-3 minutos porque descarga los datos desde internet. Al finalizar genera el archivo `index.html` listo para abrir en el navegador o subir a GitHub Pages.

### Ejecución por pasos (si ya tenés los datos descargados)
Si `faers_glp1_raw.csv` ya existe y solo querés regenerar el dashboard:

```bash
python analyze.py
python dashboard.py
```

Esto evita volver a descargar los datos y es mucho más rápido.

---

## ¿Qué hace cada archivo?

### `main.py` — El director de orquesta
No hace cálculos propios. Su único trabajo es ejecutar los tres scripts en el orden correcto y mostrar en consola qué está pasando. Si algún paso falla, detiene todo y avisa.

```
python main.py
  └→ fetch_data.py   (Paso 1 — descarga datos reales)
  └→ analyze.py      (Paso 2 — procesa y analiza)
  └→ dashboard.py    (Paso 3 — genera el HTML)
```

---

### `fetch_data.py` — Paso 1: Descarga datos reales de FAERS
Conecta con la API pública de openFDA y descarga hasta 1000 reportes de eventos adversos por droga. Para cada reporte extrae:

- Reacción adversa (término MedDRA)
- Outcome (Recovered, Fatal, Not recovered, etc.)
- Sexo y edad del paciente
- País de reporte
- Fecha del reporte
- Si el evento fue considerado grave (serious)

Respeta el rate limit de la API con pausas entre requests para no ser bloqueado.

**Output:** `faers_glp1_raw.csv`

> Nota: Este paso requiere conexión a internet. Una vez descargado el CSV, no es necesario volver a correrlo a menos que quieras actualizar los datos.

---

### `analyze.py` — Paso 2: Procesa y analiza los eventos adversos
Lee el CSV crudo y genera 7 datasets de análisis listos para el dashboard:

- **Top 15 reacciones adversas** más frecuentes en total
- **Top 10 reacciones por droga** — permite comparar perfiles de seguridad
- **Distribución por sexo** — desglosada por droga
- **Distribución por outcome** — Recovered, Fatal, Not recovered, etc.
- **Evolución anual** — reportes por año desde 2018
- **Distribución por grupo etario** — 18-30, 31-45, 46-60, 61-75, 76+
- **Eventos graves** — filtrado de reportes con outcome Fatal o Not recovered

**Outputs:**
- `faers_top_reactions.csv`
- `faers_reactions_by_drug.csv`
- `faers_sex_dist.csv`
- `faers_outcome_dist.csv`
- `faers_yearly.csv`
- `faers_age_dist.csv`
- `faers_serious.csv`
- `faers_kpis.json`

---

### `dashboard.py` — Paso 3: Genera el dashboard interactivo
Lee todos los CSVs del paso anterior, convierte los datos a JSON y construye un archivo `index.html` con todo embebido adentro: datos reales, gráficos interactivos y filtros.

El resultado es un **único archivo HTML** que cualquier navegador puede abrir sin necesitar Python, servidores ni dependencias externas.

**El dashboard incluye:**
- 5 KPIs: total reportes, eventos graves (%), fatales (%), reacciones únicas, drogas analizadas
- Top 15 reacciones adversas (gráfico de barras horizontal)
- Distribución de outcomes (donut)
- Evolución de reportes por año y por droga (líneas)
- Distribución por sexo por droga (barras apiladas)
- Distribución por grupo etario (barras apiladas)
- Top reacciones por droga — selector interactivo por droga
- Tabla de eventos graves y fatales
- Filtros en tiempo real por droga, outcome y sexo
- Disclaimer regulatorio

**Output:** `index.html` (listo para GitHub Pages)

---

## Fuente de datos

**FDA Adverse Event Reporting System (FAERS)**
Sistema de reporte post-marketing de la FDA que recopila información sobre eventos adversos y errores de medicación reportados por profesionales de salud, pacientes y fabricantes.

API pública: [https://open.fda.gov/apis/drug/event/](https://open.fda.gov/apis/drug/event/)

Los datos están disponibles desde 2004 y se actualizan trimestralmente.

---

## Hallazgos principales

- Las **reacciones gastrointestinales** (nausea, vómitos, diarrea) son los eventos adversos más frecuentes para toda la clase GLP-1
- **Semaglutide** concentra el mayor volumen de reportes, consistente con su rápido crecimiento de prescripciones desde 2021
- El perfil de **outcomes fatales** es bajo en términos porcentuales pero representa una señal relevante para farmacovigilancia
- El grupo etario **46-75 años** concentra la mayoría de los reportes, coherente con la población objetivo del tratamiento

---

## Contexto clínico y regulatorio

Este proyecto refleja competencias directamente aplicables a roles de Drug Safety, Pharmacovigilance y Clinical Data Management:

- Consumo y análisis de APIs de datos regulatorios públicos (openFDA/FAERS)
- Procesamiento y limpieza de datos de eventos adversos (MedDRA terms)
- Análisis de señales de seguridad post-marketing
- Visualización de perfiles de seguridad por droga y población
- Comprensión del ciclo de reporte de eventos adversos bajo ICH-GCP E6(R3)

---

## Tecnologías

- Python 3.8+
- requests · pandas · numpy
- HTML · JavaScript · Chart.js
- Fuente: openFDA Drug Adverse Event API (FAERS) — datos reales públicos de la FDA

---

## Autora

**María Paula Vera Morandini**
Bioquímica | Coordinadora de Estudios & QA | Clinical Data Management
ICH-GCP E6(R3) Certificada | ANMAT 7516/25
[LinkedIn](https://www.linkedin.com/in/maria-paula-vera-morandini-43b284399) · Buenos Aires, Argentina