# PROJECT COMMAND 404 — Informe QA v0.7.0-RC

Fecha: 2026-10-10.

## Resultado confirmado

- `node --check assets/app.js`: SUPERADO.
- `node tests/static-qa.cjs`: 11/11 casos SUPERADOS.
- `python -m py_compile tests/e2e.py`: SUPERADO (sintaxis de pruebas).
- Paquete ZIP: comprobación CRC realizada al empaquetar.

## Resultado NO confirmado

- La ejecución de `python tests/e2e.py` NO ha podido completar pruebas interactivas en este entorno: Chromium del sistema se inicia, pero la navegación a http://127.0.0.1 devuelve `net::ERR_BLOCKED_BY_ADMINISTRATOR`. Esto **no** implica fallo de la aplicación ni que pase la prueba.
- Las pruebas E2E (dashboard, altas, recarga IndexedDB, filtros, Kanban, hitos, QA, exportación, temas, GitHub inválido, menú móvil y errores JS) quedan PENDIENTES de ejecutarse en Windows.
- Pruebas de importación y restauración, drag-and-drop, integración GitHub real, seguridad y regresión visual completa: PENDIENTES.

## Ejecutar en Windows

Descomprimir ZIP; doble clic en `EJECUTAR_QA_WINDOWS.bat`. Requiere Python, conexión para descargar Playwright y Chromium en la primera ejecución. Usa navegador temporal separado del perfil personal. Si falla cualquier caso, no etiquetar como estable. El script devuelve código de salida no cero.

**Veredicto**: Release candidate, sin certificación v1.0.0 ni nota 9,5/10.


## Actualización de CI — 2026-10-11

- Se añadió `.github/workflows/quality.yml` para ejecutar en GitHub Actions la revisión de sintaxis JavaScript y Python, los casos estáticos y la suite E2E con Chromium en push a `main`, pull request o ejecución manual.
- La E2E ahora incluye un ciclo de exportación, borrado y restauración de copia JSON y comprueba que sobreviven el proyecto y una tarea.
- **Comprobaciones realizadas en esta revisión:** `node --check assets/app.js`, `node tests/static-qa.cjs` (11/11) y `python -m py_compile tests/e2e.py`: superadas sobre los archivos publicados.
- **E2E en Chromium y primera ejecución CI: pendientes de confirmación.** El entorno local de revisión no tiene Playwright instalado y GitHub aún no muestra un estado para el workflow. No se afirma que los casos E2E estén superados hasta que GitHub Actions termine en verde.
