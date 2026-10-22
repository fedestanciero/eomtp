#!/usr/bin/env python3
"""Descarga los negocios de HubSpot y regenera data.js para el panel.

Uso:
    export HUBSPOT_TOKEN="pat-eu1-..."   # token de una app privada de HubSpot
    python3 actualizar.py                 # desde julio 2025 (o 15 meses atrás, lo que sea antes)
    python3 actualizar.py --desde 2025-09-01

La app privada necesita los permisos (scopes) crm.objects.deals.read y crm.objects.contacts.read.
Solo usa la biblioteca estándar de Python 3.9+.
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Europe/Madrid")
API = "https://api.hubapi.com/crm/v3/objects/deals/search"
API_ASOC = "https://api.hubapi.com/crm/v4/associations/deals/contacts/batch/read"
API_CONTACTOS = "https://api.hubapi.com/crm/v3/objects/contacts/batch/read"
DETALLE = ["hs_analytics_source_data_1", "hs_analytics_source_data_2"]
# nombres legibles para el Drill-Down 1 de «Fuentes sin conexión»
OFFLINE_1 = {"INTEGRATION": "Integración", "CRM_UI": "Alta manual en HubSpot", "IMPORT": "Importación",
             "EXTENSION": "Extensión de navegador", "CONVERSATIONS": "Bandeja de conversaciones",
             "PRESENTATIONS": "Documentos compartidos"}

# Las mismas etapas y cursos que filtran los informes del panel de HubSpot.
# canal = fuente de tráfico original del negocio (hs_analytics_source)
CANALES = {
    "PAID_SOCIAL": "Redes sociales pagadas", "OFFLINE": "Fuentes sin conexión", "PAID_SEARCH": "Búsqueda pagada",
    "ORGANIC_SEARCH": "Búsqueda orgánica", "DIRECT_TRAFFIC": "Tráfico directo", "AI_REFERRALS": "Referencias de IA",
    "SOCIAL_MEDIA": "Redes sociales orgánicas", "REFERRALS": "Referencias", "OTHER_CAMPAIGNS": "Otras campañas",
    "EMAIL_MARKETING": "Email marketing", "": "Sin canal",
}
ETAPAS = [
    ("appointmentscheduled", "Interesados"),
    ("qualifiedtobuy", "Cualificados"),
    ("presentationscheduled", "Primer intento"),
    ("112773443", "Segundo intento"),
    ("decisionmakerboughtin", "Interacción"),
    ("105885260", "Demorados con potencial"),
    ("105910376", "Pre-matriculados"),
    ("closedwon", "Matriculados"),
    ("closedlost", "Perdidos"),
]


def ms(d):
    return int(datetime(d.year, d.month, d.day, tzinfo=TZ).timestamp() * 1000)


def peticion(token, body, url=API):
    req = urllib.request.Request(
        url, data=json.dumps(body).encode(), method="POST",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    for intento in range(5):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and intento < 4:  # límite de peticiones: esperar y reintentar
                time.sleep(2 ** intento)
                continue
            sys.exit(f"Error de HubSpot {e.code}: {e.read().decode()[:500]}")


def contar_entradas(token, etapa, desde, hasta):
    """Cuántos negocios entraron en la etapa entre [desde, hasta) según hs_v2_date_entered_<etapa>."""
    prop = f"hs_v2_date_entered_{etapa}"
    body = {
        "filterGroups": [{"filters": [
            {"propertyName": prop, "operator": "GTE", "value": str(ms(desde))},
            {"propertyName": prop, "operator": "LT", "value": str(ms(hasta))},
        ]}],
        "properties": ["hs_object_id"],
        "limit": 1,
    }
    time.sleep(0.25)
    return peticion(token, body)["total"]


def matriculas_por_curso(token, desde, hasta):
    """Negocios que entraron en Matriculados entre [desde, hasta), contados por curso y por canal."""
    prop, after, cuenta, por_canal, lista = "hs_v2_date_entered_closedwon", None, {}, {}, []
    while True:
        body = {
            "filterGroups": [{"filters": [
                {"propertyName": prop, "operator": "GTE", "value": str(ms(desde))},
                {"propertyName": prop, "operator": "LT", "value": str(ms(hasta))},
            ]}],
            "properties": ["curso", "hs_analytics_source"] + DETALLE,
            "limit": 200,
        }
        if after:
            body["after"] = after
        data = peticion(token, body)
        for n in data["results"]:
            curso = n["properties"].get("curso") or "Sin curso"
            cuenta[curso] = cuenta.get(curso, 0) + 1
            canal = n["properties"].get("hs_analytics_source") or ""
            por_canal[canal] = por_canal.get(canal, 0) + 1
            lista.append(n)
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return cuenta, por_canal, lista
        time.sleep(0.25)


def origen_contactos(token, ids_negocio):
    """{id de negocio: [orígenes del registro de sus contactos]} («Record source detail 1» del contacto)."""
    ids = sorted(set(ids_negocio))
    contactos_de = {}
    for k in range(0, len(ids), 1000):
        data = peticion(token, {"inputs": [{"id": i} for i in ids[k:k + 1000]]}, API_ASOC)
        for r in data.get("results", []):
            contactos_de[str(r["from"]["id"])] = [str(t["toObjectId"]) for t in r.get("to", [])]
        time.sleep(0.25)
    todos = sorted({c for cs in contactos_de.values() for c in cs})
    origen = {}
    for k in range(0, len(todos), 100):
        data = peticion(token, {"properties": ["hs_object_source_detail_1"],
                                "inputs": [{"id": c} for c in todos[k:k + 100]]}, API_CONTACTOS)
        for r in data.get("results", []):
            origen[str(r["id"])] = r["properties"].get("hs_object_source_detail_1") or ""
        time.sleep(0.25)
    # un negocio cuenta una vez por cada origen distinto de sus contactos
    return {d: sorted({origen.get(c, "") for c in cs}) or [""] for d, cs in contactos_de.items()}


def etiqueta_origen(o):
    if not o:
        return "Sin dato"
    if o.lower().startswith("whathub"):
        return "WhatsApp (WhatHub)"
    return " ".join(w if (i and w in {"de", "del", "y", "-"}) else w[:1].upper() + w[1:]
                    for i, w in enumerate(o.split(" ")))


def buscar(token, desde, hasta):
    """Devuelve todos los negocios creados en [desde, hasta) con las etapas del panel."""
    after, out = None, []
    while True:
        body = {
            "filterGroups": [{"filters": [
                {"propertyName": "createdate", "operator": "GTE", "value": str(ms(desde))},
                {"propertyName": "createdate", "operator": "LT", "value": str(ms(hasta))},
                {"propertyName": "dealstage", "operator": "IN", "values": [e for e, _ in ETAPAS]},
            ]}],
            "properties": ["createdate", "dealstage", "curso", "hs_analytics_source"] + DETALLE,
            "sorts": [{"propertyName": "createdate", "direction": "ASCENDING"}],
            "limit": 200,
        }
        if after:
            body["after"] = after
        data = peticion(token, body)
        out += data["results"]
        after = data.get("paging", {}).get("next", {}).get("after")
        if not after:
            return out
        time.sleep(0.25)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", help="AAAA-MM-DD (por defecto, julio 2025 o 15 meses atrás, lo que sea antes)")
    args = ap.parse_args()

    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        sys.exit("Falta la variable de entorno HUBSPOT_TOKEN (token de la app privada de HubSpot).")

    hoy = datetime.now(TZ).date()
    # el panel muestra por defecto los últimos 14 meses; se descarga algo más para poder mirar atrás
    m = hoy.year * 12 + hoy.month - 1 - 15
    hace15 = date(m // 12, m % 12 + 1, 1)
    desde = date.fromisoformat(args.desde) if args.desde else min(date(2025, 7, 1), hace15)
    desde = desde.replace(day=1)

    # Una búsqueda por mes: la API de búsqueda corta en 10.000 resultados por consulta.
    meses, negocios, d = [], [], desde
    entradas = {e: [] for e, _ in ETAPAS}
    matriculas_mes, matriculas_canal = [], []  # por mes: {curso o canal: matrículas cerradas}
    matriculaciones = []  # (índice de mes, negocio) de cada entrada a Matriculados
    while d <= hoy:
        sig = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        fin = min(sig, hoy + timedelta(days=1))
        meses.append(d.strftime("%Y-%m"))
        lote = buscar(token, d, fin)
        print(f"{meses[-1]}: {len(lote)} negocios")
        negocios += lote
        for e, _ in ETAPAS:
            entradas[e].append(contar_entradas(token, e, d, fin))
        por_curso, por_canal, lista = matriculas_por_curso(token, d, fin)
        matriculaciones += [(len(meses) - 1, n) for n in lista]
        matriculas_mes.append(por_curso)
        matriculas_canal.append(por_canal)
        d = sig

    idx = {m: i for i, m in enumerate(meses)}
    etapas = {e: [0] * len(meses) for e, _ in ETAPAS}
    cursos, matriculados = {}, {}
    canales, canales_won = {}, {}
    for n in negocios:
        p = n["properties"]
        creado = datetime.fromisoformat(p["createdate"].replace("Z", "+00:00")).astimezone(TZ)
        i = idx.get(creado.strftime("%Y-%m"))
        if i is None:
            continue
        if p.get("dealstage") in etapas:
            etapas[p["dealstage"]][i] += 1
        curso = p.get("curso") or "Sin curso"
        cursos.setdefault(curso, [0] * len(meses))[i] += 1
        matriculados.setdefault(curso, [0] * len(meses))
        canal = p.get("hs_analytics_source") or ""
        canales.setdefault(canal, [0] * len(meses))[i] += 1
        canales_won.setdefault(canal, [0] * len(meses))
        if p.get("dealstage") == "closedwon":
            matriculados[curso][i] += 1
            canales_won[canal][i] += 1

    # tablas de la pestaña de canales: por detalle de la fuente y por origen del contacto
    def agregar(claves_de):
        """claves_de(negocio) -> lista de claves; cuenta leads y matriculados por mes de creación,
        y matrículas cerradas por mes de entrada a Matriculados."""
        t = {}
        nuevo = lambda: {"valores": [0] * len(meses), "matriculados": [0] * len(meses), "matriculas_mes": [0] * len(meses)}
        for n in negocios:
            i = idx.get(datetime.fromisoformat(n["properties"]["createdate"].replace("Z", "+00:00")).astimezone(TZ).strftime("%Y-%m"))
            if i is None:
                continue
            for c in claves_de(n):
                f = t.setdefault(c, nuevo())
                f["valores"][i] += 1
                if n["properties"].get("dealstage") == "closedwon":
                    f["matriculados"][i] += 1
        for i, n in matriculaciones:
            for c in claves_de(n):
                t.setdefault(c, nuevo())["matriculas_mes"][i] += 1
        return t

    detalles = {}
    for nivel, prop in (("detalle1", DETALLE[0]), ("detalle2", DETALLE[1])):
        nombres = {}
        def clave(n, prop=prop, nombres=nombres):
            canal = n["properties"].get("hs_analytics_source") or ""
            valor = (n["properties"].get(prop) or "").strip()
            nombres.setdefault((canal, valor.lower()), valor)
            return [(canal, valor.lower())]
        t = agregar(clave)
        filas = []
        for (canal, v), f in t.items():
            nombre = nombres[(canal, v)] or "Sin detalle"
            if nivel == "detalle1" and canal == "OFFLINE":
                nombre = OFFLINE_1.get(nombre.upper(), nombre)
            filas.append({"canal": canal, "nombre": nombre, **f})
        detalles[nivel] = sorted(filas, key=lambda r: -sum(r["valores"]))

    print("Leyendo los contactos de cada negocio…")
    origen_de = origen_contactos(token, [n["id"] for n in negocios] + [n["id"] for _, n in matriculaciones])
    t = agregar(lambda n: origen_de.get(str(n["id"]), [""]))
    origen_contacto = sorted(({"id": o or "Unassigned", "nombre": etiqueta_origen(o), **f} for o, f in t.items()),
                             key=lambda r: -sum(r["valores"]))

    data = {
        "generado": datetime.now(TZ).isoformat(timespec="seconds"),
        "desde": desde.isoformat(),
        "hasta": hoy.isoformat(),
        "meses": meses,
        "etapas": [{"id": e, "nombre": nom, "valores": etapas[e]} for e, nom in ETAPAS],
        "entradas": [{"id": e, "nombre": nom, "valores": entradas[e]} for e, nom in ETAPAS],
        "cursos": [{"nombre": c, "valores": cursos.get(c, [0] * len(meses)),
                    "matriculados": matriculados.get(c, [0] * len(meses)),
                    "matriculas_mes": [mm.get(c, 0) for mm in matriculas_mes]}
                   for c in sorted(set(cursos) | {c for mm in matriculas_mes for c in mm})],
        "canales": [{"id": c, "nombre": CANALES.get(c, c.replace("_", " ").capitalize()),
                     "valores": canales.get(c, [0] * len(meses)),
                     "matriculados": canales_won.get(c, [0] * len(meses)),
                     "matriculas_mes": [mm.get(c, 0) for mm in matriculas_canal]}
                    for c in sorted(set(canales) | {c for mm in matriculas_canal for c in mm})],
        "origen_contacto": origen_contacto,
        "detalle1": detalles["detalle1"],
        "detalle2": detalles["detalle2"],
    }
    destino = Path(__file__).with_name("data.js")
    destino.write_text(
        "// Generado a partir de HubSpot. Lo reescribe actualizar.py.\n"
        "window.PANEL_DATA = " + json.dumps(data, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"Listo: {len(negocios)} negocios → {destino}")


if __name__ == "__main__":
    main()
