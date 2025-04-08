# main.py
import flet as ft
import os
import shutil
from datetime import datetime
import uuid
import traceback
import functools

import database as db
import utils

# Imports de telas e Refs...
from screens.home_screen import create_home_view, show_snackbar
from screens.client_list_screen import create_client_list_view
from screens.client_form_screen import create_client_form_view
from screens.service_type_list_screen import create_service_type_list_view
from screens.service_type_form_screen import create_service_type_form_view
from screens.os_list_screen import create_os_list_view
from screens.os_form_screen import create_os_form_view
from screens.os_form_screen import (
    photo_image_ref, photo_container_ref, photo_relative_path_text_ref,
    no_photo_text_ref, remove_photo_button_ref
)
from screens.report_screen import create_report_view


# --- Função principal da aplicação Flet ---
def main(page: ft.Page):
    page.title = "Sistema de Ordem de Serviço"
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.theme_mode = ft.ThemeMode.LIGHT

    # --- FilePicker Fotos (sem alterações) ---
    def on_photo_picked(e: ft.FilePickerResultEvent):
        if not page: print("Erro crítico: page principal não definida."); return
        if e.files:
            selected_file = e.files[0]; source_path = selected_file.path; original_name = selected_file.name; extension = os.path.splitext(original_name)[1].lower(); unique_filename = f"os_foto_{uuid.uuid4().hex[:10]}{extension}"; destination_path = os.path.join(db.UPLOADS_DIR, unique_filename)
            try:
                shutil.copy2(source_path, destination_path)
                print("Cópia da foto concluída.")
                current_view = page.views[-1] if page.views else None
                if current_view and (current_view.route == "/os/nova" or current_view.route.startswith("/os/editar/")):
                    try:
                        img = photo_image_ref.current; container = photo_container_ref.current; path_storage = photo_relative_path_text_ref.current; no_photo = no_photo_text_ref.current; remove_btn = remove_photo_button_ref.current
                        if img and container and path_storage and no_photo and remove_btn:
                            relative_path = os.path.relpath(destination_path, start=db.UPLOADS_DIR).replace("\\", "/")
                            img.src = destination_path; img.visible = True; container.visible = True; no_photo.visible = False; remove_btn.visible = True; path_storage.value = relative_path
                            page.update()
                            print("Preview atualizado (Snackbar removido).")
                        else: print("Erro callback foto: Refs não encontradas.")
                    except Exception as update_err: print(f"Erro update preview: {update_err}"); print(traceback.format_exc())
                else: print("Callback foto: View OS Form não ativa.")
            except Exception as copy_ex: print(f"Erro cópia foto: {copy_ex}"); print(traceback.format_exc()); print(f"ERRO AO COPIAR FOTO: {copy_ex}")
        elif e.path is None and not e.files: print("Seleção de foto cancelada.")
        else: print(f"Evento FilePicker inesperado: {e}")
    photo_picker = ft.FilePicker(on_result=on_photo_picked)
    page.overlay.append(photo_picker)

    # --- FilePicker Relatórios (MODIFICADO para usar page.session) ---
    def on_report_saved(e: ft.FilePickerResultEvent):
        if not page: print("Erro crítico: page principal não definida."); return

        destination_path = e.path
        source_path = None # Reset source path

        try:
            if destination_path:
                # --- Pega o caminho do arquivo temporário da SESSÃO ---
                source_path = page.session.get("temp_report_path")
                print(f"Tentando obter source_path da sessão: {source_path}") # Debug

                if source_path and os.path.exists(source_path):
                    try:
                        print(f"Copiando relatório de '{source_path}' para '{destination_path}'")
                        shutil.copy2(source_path, destination_path)
                        print(f"Relatório salvo com sucesso em: {destination_path}") # Print em vez de Snackbar

                        # Opcional: Remover arquivo temporário
                        try: os.remove(source_path); print(f"Arquivo temporário removido: {source_path}")
                        except Exception as del_err: print(f"Aviso: Não removeu temp {source_path}: {del_err}")

                    except Exception as copy_err: print(f"Erro ao copiar relatório: {copy_err}"); print(traceback.format_exc())
                else:
                    error_msg = f"Erro: Caminho temp da sessão ('{source_path}') não encontrado ou inválido."
                    print(error_msg)

            else: # Usuário cancelou
                print("Salvamento cancelado pelo usuário.")

        finally:
            # Garante a limpeza da SESSÃO
             if page.session.contains_key("temp_report_path"):
                print(f"Limpando sessão['temp_report_path']: {page.session.get('temp_report_path')}")
                page.session.remove("temp_report_path")


    report_save_picker = ft.FilePicker(on_result=on_report_saved)
    page.overlay.append(report_save_picker)

    # --- DatePicker (sem alterações) ---
    report_date_picker_ref = ft.Ref[ft.DatePicker]()
    report_target_date_field_ref = ft.Ref[ft.TextField]()
    # ... (definição on_report_date_selected e report_date_picker como antes) ...
    def on_report_date_selected(e):
        if not page: print("Erro crítico: page principal não definida."); return
        date_picker = report_date_picker_ref.current; target_field = report_target_date_field_ref.current
        if date_picker and target_field:
            selected_date = date_picker.value
            if selected_date: formatted_date = selected_date.strftime('%d/%m/%Y'); target_field.value = formatted_date; print(f"Data selecionada ({target_field.label}): {formatted_date}")
            date_picker.open = False; page.update()
        else: print("Erro on_report_date_selected: Refs não encontradas.")
    report_date_picker = ft.DatePicker(ref=report_date_picker_ref, on_change=on_report_date_selected, on_dismiss=lambda e: print("DatePicker fechado."), first_date=datetime(2020, 1, 1), last_date=datetime.now().replace(year=datetime.now().year + 5), help_text="Selecione a data", cancel_text="Cancelar", confirm_text="Confirmar")
    if report_date_picker not in page.overlay: page.overlay.append(report_date_picker)


    # --- Roteamento (sem alterações) ---
    def route_change(route):
        print(f"Mudança de rota para: {page.route}"); page.views.clear(); page.views.append(create_home_view(page))
        if page.route == "/clientes": page.views.append(create_client_list_view(page))
        elif page.route == "/clientes/novo": page.views.append(create_client_form_view(page))
        elif page.route.startswith("/clientes/editar/"):
            try: client_id = int(page.route.split("/")[-1]); page.views.append(create_client_form_view(page, client_id=client_id))
            except (ValueError, IndexError): show_snackbar(page, "ID de cliente inválido.", ft.colors.RED); page.go("/clientes")
        elif page.route == "/tipos_servico": page.views.append(create_service_type_list_view(page))
        elif page.route == "/tipos_servico/novo": page.views.append(create_service_type_form_view(page))
        elif page.route.startswith("/tipos_servico/editar/"):
             try: type_id = int(page.route.split("/")[-1]); page.views.append(create_service_type_form_view(page, type_id=type_id))
             except (ValueError, IndexError): show_snackbar(page, "ID de Tipo Serviço inválido.", ft.colors.RED); page.go("/tipos_servico")
        elif page.route == "/os": page.views.append(create_os_list_view(page))
        elif page.route == "/os/nova": page.views.append(create_os_form_view(page, photo_picker))
        elif page.route.startswith("/os/editar/"):
            try: os_id = int(page.route.split("/")[-1]); page.views.append(create_os_form_view(page, photo_picker, os_id=os_id))
            except (ValueError, IndexError): show_snackbar(page, "ID de OS inválido.", ft.colors.RED); page.go("/os")
        elif page.route == "/relatorios": page.views.append(create_report_view(page, report_save_picker))
        page.update()

    # --- view_pop (sem alterações) ---
    def view_pop(e: ft.ViewPopEvent):
        page_from_event = e.page
        if not page_from_event:
            print("view_pop: Erro - page_from_event não encontrado.")
            return

        view_saindo = None  # Inicializa a variável
        route_saindo_str = "N/A" # String padrão para o log

        try:
            # 1. Verifica se há views ANTES de tentar acessar a última
            if page_from_event.views:
                view_saindo = page_from_event.views[-1] # Pega a view que vai sair
                if view_saindo and hasattr(view_saindo, 'route'):
                    route_saindo_str = view_saindo.route # Guarda a rota para o log
                else:
                    route_saindo_str = "[View inválida ou sem rota]"
                print(f"View pop: Rota saindo = {route_saindo_str}")

                # 2. Realiza o pop SOMENTE se a lista não estiver vazia
                page_from_event.views.pop()
            else:
                # Se a lista já estava vazia, não há o que fazer pop ou logar rota saindo
                print("View pop: Tentativa de pop em lista de views vazia.")
                # Neste caso, talvez apenas navegar para a raiz seja apropriado
                page_from_event.go("/")
                return # Sai da função

            # 3. Navega para a view que ficou no topo (ou raiz) APÓS o pop
            if not page_from_event.views:
                print("View pop: Lista ficou vazia, voltando para '/'")
                page_from_event.go("/")
            else:
                top_view = page_from_event.views[-1]
                # Verifica se a view do topo é válida antes de navegar
                if top_view and hasattr(top_view, 'route'):
                    print(f"View pop: Voltando para = {top_view.route}")
                    page_from_event.go(top_view.route)
                else:
                    print(f"View pop: View no topo inválida ({top_view}), voltando para '/'")
                    page_from_event.go("/")

        except IndexError:
             # Captura erro caso a lista fique vazia entre a checagem e o acesso page.views[-1] (improvável mas seguro)
             print("View pop: Erro de índice ao acessar views (concorrência?). Voltando para '/'.")
             if page_from_event: page_from_event.go("/")
        except Exception as pop_err:
            print(f"ERRO INESPERADO em view_pop: {pop_err}")
            print(traceback.format_exc())
            # Tenta um fallback seguro
            try:
                if page_from_event: page_from_event.go("/")
            except Exception as fallback_err: print(f"ERRO no fallback de view_pop: {fallback_err}")


    page.on_route_change = route_change
    page.on_view_pop = view_pop

    # --- Inicialização (sem alterações) ---
    print("Configurando banco de dados..."); db.setup_database(); print("Banco de dados pronto.")
    print("Iniciando aplicação..."); page.go(page.route or "/")

# --- Execução ---
if __name__ == "__main__":
    ft.app(target=main)