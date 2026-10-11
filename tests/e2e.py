"""End-to-end smoke/regression suite. Uses a disposable browser profile."""
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
                def edit_project():
                    page.locator('[data-open]').first.click()
                    page.locator('[data-action="edit"]').click()
                    page.locator('#projectDescription').fill('Descripción editada QA')
                    page.locator('#projectProgress').fill('42')
                    page.locator('#projectForm button[type=submit]').click()
                    page.get_by_text('Descripción editada QA').wait_for()
                    assert '42%' in page.locator('.panel').first.inner_text()
                test('Editar proyecto', edit_project)
                def delete_project():
                    page.locator('[data-view="projects"]').click()
                    page.locator('[data-action="create"]').click()
                    page.locator('#projectName').fill('PROYECTO QA TEMPORAL')
                    page.locator('#projectForm button[type=submit]').click()
                    card=page.locator('.project-card').filter(has_text='PROYECTO QA TEMPORAL')
                    card.wait_for()
                    card.locator('[data-open]').click()
                    page.once('dialog',lambda dialog: dialog.accept())
                    page.locator('[data-action="delete"]').click()
                    page.get_by_text('Proyecto eliminado').wait_for()
                    assert page.locator('.project-card').filter(has_text='PROYECTO QA TEMPORAL').count()==0
                test('Eliminar proyecto', delete_project)
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
                    parent=page.locator('.task').filter(has_text='TAREA QA').get_attribute('data-drag')
                    page.locator('[data-action="new-task"]').click()
                    page.locator('#taskName').fill('TAREA DEPENDIENTE QA')
                    page.locator(f'input[name="dependency"][value="{parent}"]').check()
                    page.locator('#taskForm button[type=submit]').click()
                    page.get_by_text('TAREA DEPENDIENTE QA').first.wait_for()
                    return {
                        'TAREA QA':page.get_by_role('heading',name='TAREA QA',exact=True).locator('xpath=..').get_attribute('data-drag'),
                        'TAREA DEPENDIENTE QA':page.get_by_role('heading',name='TAREA DEPENDIENTE QA',exact=True).locator('xpath=..').get_attribute('data-drag')
                    }
                task_ids=[]
                def dependencies():
                    ids=task_ids[0]
                    page.locator(f'[data-move="{ids["TAREA DEPENDIENTE QA"]}"]').select_option('Hecho')
                    page.get_by_text('Tarea bloqueada por dependencias').wait_for()
                    assert page.locator(f'[data-move="{ids["TAREA DEPENDIENTE QA"]}"]').input_value()=='Backlog'
                    page.locator(f'[data-move="{ids["TAREA QA"]}"]').select_option('Hecho')
                    page.locator('.kanban-column').nth(4).get_by_text('TAREA QA').wait_for()
                    page.locator(f'[data-move="{ids["TAREA DEPENDIENTE QA"]}"]').select_option('Hecho')
                    page.locator('.kanban-column').nth(4).get_by_text('TAREA DEPENDIENTE QA').wait_for()
                test('Kanban: crear tareas con dependencia',lambda: task_ids.append(task()))
                test('Dependencia bloquea y libera tareas',dependencies)
                def drag_drop():
                    page.locator('[data-action="new-task"]').click()
                    page.locator('#taskName').fill('TAREA ARRASTRE QA')
                    page.locator('#taskForm button[type=submit]').click()
                    task_card=page.locator('.task').filter(has_text='TAREA ARRASTRE QA')
                    # Send the HTML5 drag events explicitly. Browser-level drag_to can miss
                    # the column drop zone in headless Chromium due to element geometry.
                    page.evaluate("""() => {
                        const source = [...document.querySelectorAll('.task')]
                            .find(el => el.innerText.includes('TAREA ARRASTRE QA'));
                        const target = document.querySelectorAll('.kanban-column')[1];
                        if (!source || !target) throw new Error('No se encontró origen o destino del arrastre');
                        const dataTransfer = new DataTransfer();
                        source.dispatchEvent(new DragEvent('dragstart', {
                            bubbles: true, cancelable: true, dataTransfer
                        }));
                        target.dispatchEvent(new DragEvent('dragover', {
                            bubbles: true, cancelable: true, dataTransfer
                        }));
                        target.dispatchEvent(new DragEvent('drop', {
                            bubbles: true, cancelable: true, dataTransfer
                        }));
                    }""")
                    page.locator('.kanban-column').nth(1).get_by_text('TAREA ARRASTRE QA').wait_for()
                test('Kanban: arrastrar tarjeta',drag_drop)
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
                    assert any(t['title']=='TAREA DEPENDIENTE QA' for t in data['tasks'])
                    backup_file.append(path)
                test('Exportación JSON',export)
                def restore():
                    page.once('dialog',lambda dialog: dialog.accept())
                    page.locator('[data-action="erase"]').click()
                    page.locator('.data-actions').wait_for()
                    assert '0 proyectos' in page.locator('.panel').inner_text()
                    with page.expect_file_chooser() as chooser_info:
                        page.locator('[data-action="import"]').click()
                    page.once('dialog',lambda dialog: dialog.accept())
                    chooser_info.value.set_files(str(backup_file[0]))
                    page.get_by_text('Copia restaurada correctamente').wait_for()
                    page.locator('[data-view="overview"]').click()
                    page.get_by_text('PROYECTO QA AUTOMATICO').first.wait_for()
                    page.locator('[data-open]').first.click()
                    page.locator('[data-action="kanban"]').click()
                    page.get_by_text('TAREA QA').first.wait_for()
                test('Borrar y restaurar copia JSON',restore)
                def invalid_backup():
                    page.locator('[data-view="data"]').click()
                    tmp=tempfile.NamedTemporaryFile(prefix='project-command-invalid-',suffix='.json',delete=False)
                    tmp.write(b'{"format":"project-command-404","version":4,"projects":[{"id":"invalid"}],"events":[]}')
                    tmp.close()
                    bad_path=Path(tmp.name)
                    backup_file.append(bad_path)
                    with page.expect_file_chooser() as chooser_info:
                        page.locator('[data-action="import"]').click()
                    chooser_info.value.set_files(str(bad_path))
                    page.wait_for_function("document.querySelector('#toast').textContent.includes('No se pudo importar')")
                    assert '0 proyectos' not in page.locator('.panel').first.inner_text()
                    page.locator('[data-view="overview"]').click()
                    page.get_by_text('PROYECTO QA AUTOMATICO').first.wait_for()
                test('Rechazar backup JSON corrupto sin borrar datos',invalid_backup)
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
                    page.unroute('https://api.github.com/**')
                    page.route('https://api.github.com/**',lambda route:route.fulfill(status=404,content_type='application/json',body='{"message":"Not Found"}'))
                    page.locator('#githubUrl').fill('https://github.com/qa/project')
                    page.locator('#githubLookup button[type=submit]').click()
                    page.get_by_text('Repositorio no encontrado o no público').wait_for()
                    page.unroute('https://api.github.com/**')
                    page.route('https://api.github.com/**',lambda route:route.fulfill(status=403,content_type='application/json',body='{"message":"API rate limit exceeded"}'))
                    page.locator('#githubLookup button[type=submit]').click()
                    page.get_by_text('Límite de GitHub alcanzado o acceso denegado').wait_for()
                    page.unroute('https://api.github.com/**')
                    page.route('https://api.github.com/**',lambda route:route.abort('failed'))
                    page.locator('#githubLookup button[type=submit]').click()
                    page.get_by_text('No se pudo consultar GitHub').wait_for()
                    assert page.locator('#githubResults .warning').inner_text().strip()
                    page.unroute('https://api.github.com/**')
                test('GitHub: URL, 404, 403 y error de red', github_error)
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
