# PROJECT COMMAND 404 — v0.6.0 · Release Candidate

Incluye fases 1–5 y correcciones de fase 6. **No es una release certificada**: Chromium del entorno devuelve `ERR_BLOCKED_BY_ADMINISTRATOR` al abrir localhost, impidiendo QA de interacción y persistencia.

## Inicio

En Windows, ejecutar `INICIAR_WINDOWS.bat` con Python 3 instalado. O bien `python -m http.server 8765 --bind 127.0.0.1` y abrir http://127.0.0.1:8765/. Para GitHub Pages, publicar el contenido de esta carpeta en la raíz del repositorio.

## Correcciones

- Se acota el porcentaje mostrado en barras de progreso.
- Se controla el error de URL GitHub mal formada.
- Se rechazan URLs de repositorio con parámetros o fragmentos al introducirlas o importar copias.

## Comprobaciones pendientes antes de publicar como estable

- Crear, editar y borrar proyecto; recargar y verificar IndexedDB.
- Crear tarea e hito, cambiar estados, bloquear tareas dependientes y verificar arrastre Kanban.
- Registrar bug, decisión, QA y release; revisar métricas del radar.
- Exportar JSON, borrar e importar; confirmar integridad y datos.
- Probar GitHub Connect con repositorio público, 404, error de red y límites de API.
- Probar teclado, móvil y navegadores reales.

Los datos son locales y no cifrados. Exporta copias antes de actualizar. No hay sincronización automática.


## Auditoría 0.6.1-RC
Consulta `QA-REPORT.md`. Ejecuta `node tests/static-qa.cjs` para verificar las validaciones de importación de copias. Las pruebas en navegador siguen pendientes.


## v0.6.2-RC
Se corrigen inconsistencias de dependencias de tareas completadas y se endurecen los enlaces GitHub importados. Ejecutar `node tests/static-qa.cjs` para validar 11 casos. La prueba E2E sigue pendiente.

## v0.7.0-RC — QA automatizado para Windows

- Ejecuta `EJECUTAR_QA_WINDOWS.bat` para instalar Playwright si falta, obtener Chromium y lanzar `tests/e2e.py`.
- El conjunto E2E usa un servidor local en un puerto libre y un perfil de navegador aislado. No modifica tu navegador cotidiano ni datos reales.
- Para ejecutar la validación estática también puedes usar `node tests/static-qa.cjs` (requiere Node.js).
- **No es v1.0.0 estable:** falta ejecutar las pruebas funcionales y subsanar lo que encuentren. Consulta `QA-REPORT.md`.
