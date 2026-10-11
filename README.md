# PROJECT COMMAND 404

[![Quality checks](https://github.com/ivan7800/PROJECT-COMMAND-404/actions/workflows/quality.yml/badge.svg?branch=main)](https://github.com/ivan7800/PROJECT-COMMAND-404/actions/workflows/quality.yml)

**Panel local para organizar el ciclo de vida de tus proyectos**, desde la idea hasta la publicación. Registra tareas y dependencias, hitos, incidencias, decisiones, checklist QA y releases en un solo espacio.

> **Estado:** release candidate (v0.7.0). Las pruebas estáticas están superadas; las pruebas funcionales E2E en navegador aún están pendientes. Consulta [QA-REPORT.md](QA-REPORT.md) antes de tratar esta versión como estable.

## Funciones

- **Registro de proyectos:** estado, progreso, descripción y enlace al repositorio.
- **Planificación:** tablero Kanban, tareas, prioridades, hitos y dependencias entre tareas.
- **Seguimiento de calidad:** bugs, decisiones técnicas, comprobaciones QA y releases por proyecto.
- **Radar:** indicadores locales de actividad, bloqueos, riesgos y preparación para revisión.
- **GitHub Connect:** consulta explícita de información de repositorios públicos; no sincroniza cambios.
- **Copias de seguridad:** exportación e importación JSON con validación de estructura.
- **Experiencia local:** tema claro/oscuro, menú móvil y almacenamiento en IndexedDB.

## Captura de pantalla

No se incluye una captura validada en el repositorio. Añádela aquí cuando exista un archivo revisado, por ejemplo `docs/screenshot.png`.

## Requisitos

- Navegador moderno con JavaScript, IndexedDB y HTTPS o localhost.
- Para servir la aplicación localmente: Python 3, o cualquier servidor estático equivalente.
- Para ejecutar QA estático: Node.js.
- Para ejecutar QA E2E: Python y conexión a Internet la primera vez, para instalar Playwright y Chromium.

## Inicio rápido

### Windows

1. Descarga o clona este repositorio.
2. Abre una terminal en la carpeta del proyecto.
3. Ejecuta:

   ```bat
   py -m http.server 8765 --bind 127.0.0.1
   ```

4. Abre [http://127.0.0.1:8765/](http://127.0.0.1:8765/) en el navegador.

Si `py` no está disponible, usa `python -m http.server 8765 --bind 127.0.0.1`.

### Linux y macOS

Desde la carpeta del proyecto:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Abre [http://127.0.0.1:8765/](http://127.0.0.1:8765/).

### GitHub Pages

El proyecto es estático. En la configuración del repositorio, activa **Settings → Pages**, elige la rama `main` y la carpeta `/ (root)`. Cuando Pages termine de desplegar, abre la URL que GitHub indique.

## Pruebas

GitHub Actions ejecuta automáticamente las comprobaciones en cada push a `main` y en pull requests dirigidas a `main`. También puede iniciarse manualmente desde la pestaña **Actions**. El badge superior muestra el resultado de la última ejecución aplicable.

Validación estática (Node.js):

```bash
node --check assets/app.js
node tests/static-qa.cjs
```

Prueba E2E en Windows:

1. Ejecuta `EJECUTAR_QA_WINDOWS.bat`.
2. El script instala Playwright y Chromium si hacen falta y lanza `tests/e2e.py`.
3. Comprueba que el resultado indique que todos los casos han pasado.

La prueba E2E usa un servidor local y un contexto temporal de Chromium. La suite cubre creación, persistencia, filtros, Kanban, hitos, copias JSON (incluida restauración), tema, validación de URL GitHub y menú móvil. Su resultado no está certificado hasta que la ejecución de GitHub Actions termine correctamente. El estado comprobado de esta entrega está descrito en [QA-REPORT.md](QA-REPORT.md).

## Datos y privacidad

- Los proyectos y registros se guardan en IndexedDB del navegador de ese dispositivo.
- No hay cuenta, backend, sincronización automática ni telemetría declarada por la aplicación.
- GitHub Connect realiza consultas solo cuando el usuario las solicita; el navegador puede comunicarse con GitHub.
- Los datos locales no están cifrados. Protege el dispositivo y exporta copias JSON con cuidado: pueden contener información privada.
- Borrar los datos del navegador puede eliminar los registros. Usa **Datos y copias** para exportar una copia periódicamente.

## Limitaciones conocidas

- No existe sincronización entre navegadores o dispositivos.
- La información de GitHub depende de la API pública y de sus límites; no es una integración autenticada.
- El radar presenta indicadores orientativos calculados con los datos registrados. No certifica calidad ni sustituye pruebas ejecutadas.
- La certificación E2E y una revisión visual completa siguen pendientes, según el informe QA.

## Estructura principal

- `index.html`: punto de entrada.
- `assets/app.js`: lógica de la aplicación.
- `assets/styles.css`: estilos y diseño adaptable.
- `tests/static-qa.cjs`: validaciones estáticas.
- `tests/e2e.py`: pruebas funcionales con Playwright.
- `EJECUTAR_QA_WINDOWS.bat`: instalación y ejecución guiada de E2E en Windows.
- `QA-REPORT.md`: resultados y pendientes de QA.

## Contribuciones y licencia

Las contribuciones pueden proponerse mediante issues o pull requests. Aún no se ha especificado una licencia de código en este repositorio; hasta que se añada una, no se debe asumir que el contenido puede reutilizarse, modificarse o redistribuirse libremente.

## Historial

Las correcciones y notas de auditoría de versiones anteriores están documentadas en el historial de commits y en [QA-REPORT.md](QA-REPORT.md). Este README describe la versión que contiene la rama principal actualmente.
