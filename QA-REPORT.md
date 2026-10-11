# PROJECT COMMAND 404 — Informe QA

**Estado actual:** release candidate v0.7.0. La CI anterior aparece verde en la captura de GitHub (**Quality checks #10**, ejecución manual en `main`), pero después se ampliaron las pruebas E2E. Esa ampliación aún debe ejecutarse antes de certificar la release.

## Comprobaciones locales de código

- `node --check assets/app.js`: superada.
- `node tests/static-qa.cjs`: 11/11 casos superados.
- `python -m py_compile tests/e2e.py`: se vuelve a ejecutar para la versión actualizada.
- Los resultados de sintaxis y pruebas estáticas no sustituyen la ejecución del navegador.

## Alcance E2E actual

La suite `tests/e2e.py` comprueba:

- Inicio, modal, altas, edición y borrado de proyectos.
- Persistencia, búsqueda y filtros.
- Crear/mover tareas; dependencias bloqueantes y desbloqueo.
- Arrastrar una tarjeta Kanban.
- Crear hitos y abrir el centro QA.
- Exportar, borrar y restaurar una copia válida con proyecto y tareas.
- Rechazar un JSON inválido sin sustituir los datos actuales.
- Tema claro, menú móvil y ausencia de errores JavaScript.
- GitHub Connect: URL inválida, respuestas simuladas 404 y 403 para comprobar los mensajes de error y límite de API.

Las respuestas HTTP de GitHub se simulan deliberadamente en E2E para hacer la prueba reproducible y no depender de Internet ni de los límites de la API. No equivalen a una validación de conectividad en producción.

## Pendiente para declarar v1.0.0

1. Ejecutar la versión actual de la suite en GitHub Actions y corregir cualquier fallo.
2. Hacer una revisión visual y de teclado en móvil y en otro navegador además de Chromium.
3. Confirmar que la documentación y los textos visibles de la aplicación dejan de indicar RC al preparar la release.

## Ejecución local en Windows

Descomprime el proyecto y ejecuta `EJECUTAR_QA_WINDOWS.bat`. La primera ejecución instala Playwright y Chromium; requiere Python y conexión a Internet. El navegador usa un contexto temporal. Si alguna prueba falla, no publiques la versión como estable.

**No se afirma que v1.0.0 esté certificada hasta superar los puntos pendientes.**
