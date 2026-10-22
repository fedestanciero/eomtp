#!/usr/bin/env python3
"""Descarga los negocios de HubSpot y regenera data.js para el panel.

Uso:
    export HUBSPOT_TOKEN="pat-eu1-..."   # token de una app privada de HubSpot
    python3 actualizar.py                 # desde el 1 de enero del año en curso
    python3 actualizar.py --desde 2025-09-01

La app privada necesita el permiso (scope) crm.objects.deals.read.
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

# Las mismas etapas y cursos que filtran los informes del panel de HubSpot.
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


def peticion(token, body):
    req = urllib.request.Request(
        API, data=json.dumps(body).encode(), method="POST",
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
            "properties": ["createdate", "dealstage", "curso"],
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
    ap.add_argument("--desde", help="AAAA-MM-DD (por defecto, 1 de enero de este año)")
    args = ap.parse_args()

    token = os.environ.get("HUBSPOT_TOKEN")
    if not token:
        sys.exit("Falta la variable de entorno HUBSPOT_TOKEN (token de la app privada de HubSpot).")

    hoy = datetime.now(TZ).date()
    desde = date.fromisoformat(args.desde) if args.desde else date(hoy.year, 1, 1)
    desde = desde.replace(day=1)

    # Una búsqueda por mes: la API de búsqueda corta en 10.000 resultados por consulta.
    meses, negocios, d = [], [], desde
    entradas = {e: [] for e, _ in ETAPAS}
    while d <= hoy:
        sig = (d.replace(day=28) + timedelta(days=4)).replace(day=1)
        fin = min(sig, hoy + timedelta(days=1))
        meses.append(d.strftime("%Y-%m"))
        lote = buscar(token, d, fin)
        print(f"{meses[-1]}: {len(lote)} negocios")
        negocios += lote
        for e, _ in ETAPAS:
            entradas[e].append(contar_entradas(token, e, d, fin))
        d = sig

    idx = {m: i for i, m in enumerate(meses)}
    etapas = {e: [0] * len(meses) for e, _ in ETAPAS}
    cursos, matriculados = {}, {}
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
        if p.get("dealstage") == "closedwon":
            matriculados[curso][i] += 1

    data = {
        "generado": datetime.now(TZ).isoformat(timespec="seconds"),
        "desde": desde.isoformat(),
        "hasta": hoy.isoformat(),
        "meses": meses,
        "etapas": [{"id": e, "nombre": nom, "valores": etapas[e]} for e, nom in ETAPAS],
        "entradas": [{"id": e, "nombre": nom, "valores": entradas[e]} for e, nom in ETAPAS],
        "cursos": [{"nombre": c, "valores": v, "matriculados": matriculados[c]} for c, v in sorted(cursos.items())],
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
