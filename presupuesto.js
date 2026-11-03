// Presupuesto diario de Meta Ads, desde la planilla «Media plan EOMTP». Lo genera actualizacion/presupuesto.py.
// «IDEM» = el valor del mes anterior; celda vacía = campaña sin presupuesto. Abril tuvo dos columnas: vale la última.
window.PRESUPUESTO = {
  "fuente": "Planilla «Media plan EOMTP», pestaña «Media plan»",
  "meses": ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09", "2026-10"],
  "columna_actual": "Octubre",
  "actual": [
    {"pais": "España", "ciudad": "Madrid", "diario": 10.0},
    {"pais": "España", "ciudad": "Barcelona", "diario": 25.0},
    {"pais": "España", "ciudad": "Vigo", "diario": 3.0},
    {"pais": "España", "ciudad": "Bilbao", "diario": 9.0},
    {"pais": "España", "ciudad": "Valencia", "diario": 22.0},
    {"pais": "España", "ciudad": "Zaragoza", "diario": 0.0},
    {"pais": "España", "ciudad": "Mallorca", "diario": 0.0},
    {"pais": "España", "ciudad": "España", "diario": 10.0},
    {"pais": "Portugal", "ciudad": "Lisboa", "diario": 7.5},
    {"pais": "Portugal", "ciudad": "Porto", "diario": 7.5},
    {"pais": "Portugal", "ciudad": "Lisboa + Porto", "diario": 4.0},
    {"pais": "Francia", "ciudad": "Bordeaux", "diario": 3.0},
    {"pais": "Francia", "ciudad": "Strasbourg", "diario": 5.0},
    {"pais": "Francia", "ciudad": "Nantes", "diario": 5.0},
    {"pais": "Francia", "ciudad": "Lille", "diario": 9.0},
    {"pais": "Francia", "ciudad": "Bélgica, Suiza, Francia, Luxemburgo", "diario": 0.0},
    {"pais": "Francia", "ciudad": "Marsella", "diario": 8.0},
    {"pais": "Francia", "ciudad": "Montpellier", "diario": 10.0},
    {"pais": "Francia", "ciudad": "Toulouse", "diario": 8.0},
    {"pais": "Francia", "ciudad": "Paris", "diario": 30.0},
    {"pais": "Francia", "ciudad": "Nice", "diario": 5.0},
    {"pais": "Francia", "ciudad": "Lyon", "diario": 9.0}
  ],
  "campanas": [
    {"plaza": "Madrid", "etapa": "Awareness", "campana": "españa_conversiones_madrid_awareness", "diario": [35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 5.0, 5.0]},
    {"plaza": "Madrid", "etapa": "Awareness", "campana": "españa_form-lead_madrid_awareness", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0]},
    {"plaza": "Barcelona", "etapa": "Awareness", "campana": "españa_conversiones_barcelona_awareness", "diario": [35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 35.0, 20.0, 20.0]},
    {"plaza": "Barcelona", "etapa": "Awareness", "campana": "españa_form-lead_barcelona_awareness", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0]},
    {"plaza": "Vigo", "etapa": "Awareness", "campana": "españa_conversiones_vigo_awareness", "diario": [5.0, 5.0, 8.0, 5.0, 5.0, 5.0, 5.0, 5.0, 3.0, 3.0]},
    {"plaza": "Bilbao", "etapa": "Awareness", "campana": "españa_conversiones_bilbao_awareness", "diario": [9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0, 9.0]},
    {"plaza": "Valencia", "etapa": "Awareness", "campana": "españa_conversiones_valencia_awareness", "diario": [18.0, 18.0, 15.0, 18.0, 18.0, 18.0, 18.0, 18.0, 17.0, 17.0]},
    {"plaza": "Valencia", "etapa": "Awareness", "campana": "españa_form-lead_valencia_awareness", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 5.0, 5.0]},
    {"plaza": "Valencia", "etapa": "Awareness", "campana": "conversiones_valencia_masterclass", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {"plaza": "Zaragoza", "etapa": "Awareness", "campana": "españa_conversiones_zaragoza_awareness", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {"plaza": "Mallorca", "etapa": "Awareness", "campana": "españa_conversiones_mallorca_awareness", "diario": [0.0, 6.0, 6.0, 6.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {"plaza": "España", "etapa": "Consideration", "campana": "videos_españa_consideration", "diario": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]},
    {"plaza": "España", "etapa": "Consideration", "campana": "reconocimiento_españa_consideration", "diario": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]},
    {"plaza": "España", "etapa": "Intention", "campana": "mensajes_españa_intention", "diario": [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0]}
  ]
};
