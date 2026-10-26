// Leads e inversión de Meta y Google Ads por ciudad (cargado a mano desde la planilla).
// Cuando se conecten Meta y Google Ads, este archivo lo generará el script de actualización.
// Octubre llega hasta el día indicado en "hasta".
window.INVERSION = {
  "hasta": "2026-10-25",
  "meses": ["2026-07", "2026-08", "2026-09", "2026-10"],
  "ciudades": {
    "Madrid":    {"leads_meta": [56, 60, 46, 31], "leads_google": [12, 10, 10, 8],  "inv_meta": [307, 308, 302, 266], "inv_google": [152, 152, 151, 124]},
    "Barcelona": {"leads_meta": [21, 36, 28, 28], "leads_google": [14, 25, 41, 41], "inv_meta": [646, 574, 595, 635], "inv_google": [670, 669, 673, 551]},
    "Valencia":  {"leads_meta": [25, 22, 19, 26], "leads_google": [27, 24, 31, 15], "inv_meta": [503, 532, 507, 533], "inv_google": [455, 451, 455, 376]},
    "Bilbao":    {"leads_meta": [17, 22, 23, 11], "leads_google": [7, 7, 11, 12],   "inv_meta": [276, 278, 271, 134], "inv_google": [271, 274, 274, 217]},
    "Vigo":      {"leads_meta": [11, 6, 7, 5],    "leads_google": [6, 6, 4, 2],     "inv_meta": [92, 92, 89, 60],     "inv_google": [151, 153, 155, 125]}
  }
};
