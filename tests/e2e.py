"""End-to-end smoke/regression suite. Uses a disposable browser profile."""
import contextlib
import http.server
import json
import shutil
import socketserver
import threading
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True

def run():
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(*a, directory=str(ROOT), **kw)
    with Server(('127.0.0.1', 0), handler) as server:
        threading.Thread(target=server.serve_forever, daemon=True).start()
        url = f'http://127.0.0.1:{server.server_address[1]}/'
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True, executable_path=shutil.which("chromium") if shutil.which("chromium") else None, args=["--no-sandbox"] if shutil.which("chromium") else [])
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            passed = []
            backup_file = []
            def test(name, fn):
                fn(); passed.append(name); print('PASS', name)
            try:
                test('Arranque y dashboard', lambda: (page.goto(url), page.locator('#viewRoot h1').wait_for(), page.get_by_text('Tu centro de mando').wait_for()))
                test('Abrir y cancelar modal', lambda: (page.locator('#quickCreate').click(), page.locator('#projectForm').wait_for(), page.locator('[data-close]').click(), page.locator('#projectForm').wait_for(state='detached')))
                def create():
                    page.locator('#quickCreate').click()
                    page.locator('#projectName').fill('PROYECTO QA AUTOMATICO')
                    page.locator('#projectDescription').fill('Caso de regresión')
                    page.locator('#projectProgress').fill('35')
                    page.locator('#projectForm button[type=submit]').click()
                    page.get_by_text('PROYECTO QA AUTOMATICO').first.wait_for()
                test('Crear proyecto', create)
                def persist():
                    page.reload();page.get_by_text('PROYECTO QA AUTOMATICO').first.wait_for()
                test('Persistencia IndexedDB al recargar',persist)
                def search():
                    page.locator('[data-view="projects"]').click()
                    page.locator('#searchInput').fill('texto-inexistente-qa')
                    page.get_by_text('No hay coincidencias').wait_for()
                    page.locator('#searchInput').fill('PROYECTO QA AUTOMATICO')
                    page.locator('[data-open]').first.wait_for()
                test('Buscar y filtrar proyectos', search)
                def task():
                    page.locator('[data-open]').first.click()
                    page.locator('[data-action="kanban"]').click()
                    page.locator('[data-action="new-task"]').click()
                    page.locator('#taskName').fill('TAREA QA')
                    page.locator('#taskForm button[type=submit]').click()
                    page.get_by_text('TAREA QA').first.wait_for()
                    page.locator('[data-move]').first.select_option('En curso')
                    page.locator('.kanban-column').nth(2).get_by_text('TAREA QA').wait_for()
                test('Kanban: crear y mover tarea',task)
                def milestone():
                    page.locator('[data-action="new-milestone"]').click()
                    page.locator('#milestoneName').fill('HITO QA')
                    page.locator('#milestoneForm button[type=submit]').click()
                    page.get_by_text('HITO QA').first.wait_for()
                test('Crear hito',milestone)
                def quality():
                    page.locator('[data-action="back-project"]').click()
                    page.locator('[data-action="quality"]').click()
                    page.locator('[data-action="new-bug"]').click()
                    page.locator('form[id$="Form"]').first.wait_for()
                    page.locator('[data-close]').click()
                test('Centro QA y modal de bugs', quality)
                def export():
                    page.locator('[data-view="data"]').click()
                    with page.expect_download() as d:
                        page.locator('[data-action="export"]').click()
                    download=d.value
                    assert download.suggested_filename.endswith('.json')
                    tmp=tempfile.NamedTemporaryFile(prefix='project-command-e2e-',suffix='.json',delete=False)
                    tmp.close()
                    path=Path(tmp.name)
                    download.save_as(path)
                    data=json.loads(path.read_text(encoding='utf-8'))
                    assert any(p['name']=='PROYECTO QA AUTOMATICO' for p in data['projects'])
                    assert any(t['title']=='TAREA QA' for t in data['tasks'])
                    backup_file.append(path)
                test('Exportación JSON',export)
                def restore():
                    page.once('dialog',lambda dialog: dialog.accept())
                    page.locator('[data-action="erase"]').click()
                    page.get_by_text('Aún no hay proyectos').wait_for()
                    with page.expect_file_chooser() as chooser_info:
                        page.locator('[data-action="import"]').click()
                    page.once('dialog',lambda dialog: dialog.accept())
                    chooser_info.value.set_files(str(backup_file[0]))
                    page.get_by_text('Copia restaurada correctamente').wait_for()
                    page.get_by_text('PROYECTO QA AUTOMATICO').first.wait_for()
                    page.locator('[data-open]').first.click()
                    page.locator('[data-action="kanban"]').click()
                    page.get_by_text('TAREA QA').first.wait_for()
                test('Borrar y restaurar copia JSON',restore)
                def theme():
                    page.locator('#themeBtn').click()
                    assert 'theme-light' in page.locator('body').get_attribute('class')
                    page.reload()
                    assert 'theme-light' in page.locator('body').get_attribute('class')
                test('Tema y persistencia localStorage',theme)
                def github_error():
                    page.locator('[data-view="github"]').click()
                    page.locator('#githubUrl').fill('https://github.com/otro/../../admin')
                    page.locator('#githubLookup button[type=submit]').click()
                    page.get_by_text('Usa https://github.com/usuario/repositorio').wait_for()
                test('GitHub: URL inválida rechazada', github_error)
                def mobile():
                    page.set_viewport_size({'width':390,'height':844})
                    page.locator('#menuBtn').click()
                    assert 'open' in page.locator('.sidebar').get_attribute('class')
                    page.locator('[data-view="overview"]').click()
                    assert 'open' not in page.locator('.sidebar').get_attribute('class')
                test('Menú móvil',mobile)
                assert not errors, f'Errores JavaScript: {errors}'
                print(f'RESULTADO: {len(passed)}/{len(passed)} pruebas superadas; 0 errores JS')
            finally:
                context.close();browser.close();server.shutdown()
                for path in backup_file:
                    path.unlink(missing_ok=True)

if __name__ == '__main__':run()
