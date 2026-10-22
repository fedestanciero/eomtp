# Panel de Leads (HubSpot → HTML local)

Abre `index.html` con doble clic. Funciona sin servidor ni conexión.

Para actualizar los datos:
1. En HubSpot: Configuración → Integraciones → Apps privadas → Crear app privada,
   con los permisos `crm.objects.deals.read` y `crm.objects.contacts.read`. Copia el token.
2. En una terminal, dentro de esta carpeta:
       export HUBSPOT_TOKEN="pat-eu1-..."      (Windows: set HUBSPOT_TOKEN=pat-eu1-...)
       python3 actualizar.py                   (o: python3 actualizar.py --desde 2025-09-01)
3. Recarga `index.html` en el navegador.
