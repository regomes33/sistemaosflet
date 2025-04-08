# screens/os_form_screen.py
import flet as ft
import database as db
from screens.home_screen import show_snackbar
from datetime import datetime
import os
import traceback

# --- Refs (como antes) ---
photo_image_ref = ft.Ref[ft.Image]()
photo_container_ref = ft.Ref[ft.Container]()
photo_relative_path_text_ref = ft.Ref[ft.Text]()
no_photo_text_ref = ft.Ref[ft.Text]()
remove_photo_button_ref = ft.Ref[ft.IconButton]()
conclusion_date_picker_ref = ft.Ref[ft.DatePicker]()
conclusion_date_field_ref = ft.Ref[ft.TextField]()

def create_os_form_view(page: ft.Page, photo_picker: ft.FilePicker, os_id=None):
    # ... (lógica inicial, carregamento de dados, campos como antes) ...
    is_editing = os_id is not None; os_data = None; initial_photo_path = None; next_os_number_val = None
    if is_editing:
        os_data = db.get_ordem_servico_by_id(os_id)
        if not os_data: show_snackbar(page, f"Erro: OS ID {os_id} não encontrada.", ft.colors.RED); page.go("/os"); return ft.View("/os/editar/error", [ft.Text("...")])
        initial_photo_path = os_data['foto_path']; print(f"Editando OS: ID={os_id}, Path foto: {initial_photo_path}")
    else: next_os_number_val = db.get_next_os_number(); print(f"Próximo número OS: {next_os_number_val}")
    try: clientes = db.get_all_clientes(); tipos_servico = db.get_all_tipos_servico()
    except Exception as e: show_snackbar(page, f"Erro dados aux: {e}", ft.colors.RED); clientes = []; tipos_servico = []
    cliente_options = [ft.dropdown.Option(key=c['id'], text=f"{c['nome']} (ID: {c['id']})") for c in clientes]
    tipo_servico_options = [ft.dropdown.Option(key=ts['id'], text=ts['nome']) for ts in tipos_servico]
    status_options = [ft.dropdown.Option("Aberta"), ft.dropdown.Option("Em Andamento"), ft.dropdown.Option("Aguardando Peças"), ft.dropdown.Option("Concluída"), ft.dropdown.Option("Cancelada"),]
    numero_os_field = ft.TextField(label="Número da OS*", value=os_data['numero_os'] if is_editing else next_os_number_val, width=200, read_only=True)
    cliente_dd = ft.Dropdown(label="Cliente*", options=cliente_options, value=os_data['cliente_id'] if is_editing else None, width=400)
    tipo_servico_dd = ft.Dropdown(label="Tipo de Serviço", options=tipo_servico_options, value=os_data['tipo_servico_id'] if is_editing else None, width=300)
    data_entrada_val = os_data['data_entrada'] if is_editing else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    data_entrada_field = ft.TextField(label="Data Entrada*", value=data_entrada_val, disabled=True, width=200)
    descricao_problema_field = ft.TextField(label="Descrição", value=os_data['descricao_problema'] if is_editing else "", multiline=True, min_lines=3, width=600)
    endereco_servico_field = ft.TextField(label="Endereço Serviço", value=os_data['endereco_servico'] if is_editing else "", width=600)
    garantia_field = ft.TextField(label="Garantia", value=os_data['garantia'] if is_editing else "", width=300)
    status_dd = ft.Dropdown(label="Status*", options=status_options, value=os_data['status'] if is_editing else "Aberta", width=200)
    initial_data_conclusao_display = ""
    if is_editing and os_data['data_conclusao']:
        try: dt_obj = datetime.strptime(os_data['data_conclusao'].split(" ")[0], '%Y-%m-%d'); initial_data_conclusao_display = dt_obj.strftime('%d/%m/%Y')
        except ValueError: print(f"Aviso data_conclusao: {os_data['data_conclusao']}"); initial_data_conclusao_display = os_data['data_conclusao']
    data_conclusao_field = ft.TextField(ref=conclusion_date_field_ref, label="Data Conclusão", value=initial_data_conclusao_display, hint_text="DD/MM/YYYY", width=180, read_only=True)
    valor_field = ft.TextField(label="Valor Total (R$)", value=f"{os_data['valor']:.2f}" if is_editing and os_data['valor'] is not None else "", keyboard_type=ft.KeyboardType.NUMBER, prefix_text="R$ ", width=150)
    observacoes_field = ft.TextField(label="Observações", value=os_data['observacoes'] if is_editing else "", multiline=True, min_lines=2, width=600)
    def on_conclusion_date_selected(e):
        date_picker=conclusion_date_picker_ref.current; target_field=conclusion_date_field_ref.current; page_from_event=e.page
        if date_picker and target_field and page_from_event:
            selected_date=date_picker.value
            if selected_date: formatted_date = selected_date.strftime('%d/%m/%Y'); target_field.value = formatted_date; print(f"Dt Conclusão: {formatted_date}")
            date_picker.open = False; page_from_event.update()
        else: print("Erro on_conclusion_date_selected")
    conclusion_date_picker=ft.DatePicker(ref=conclusion_date_picker_ref, on_change=on_conclusion_date_selected, on_dismiss=lambda e: print("DatePicker Conclusão fechado."), first_date=datetime(2020, 1, 1), last_date=datetime.now().replace(year=datetime.now().year + 5), help_text="Selecione data", cancel_text="Cancelar", confirm_text="Confirmar")
    if conclusion_date_picker not in page.overlay: page.overlay.append(conclusion_date_picker)
    def open_conclusion_date_picker(e):
        page_from_event = e.page;
        if not page_from_event: print("Erro open_conclusion: Page não encontrada."); return
        if conclusion_date_picker_ref.current: conclusion_date_picker_ref.current.open = True; page_from_event.update()
        else: print("Erro open_conclusion: Ref não encontrada.")
    btn_pick_conclusion = ft.IconButton(ft.icons.CALENDAR_MONTH, tooltip="Selecionar Data Conclusão", on_click=open_conclusion_date_picker)
    # Controles da foto (sem alterações na definição)...
    full_initial_photo_path = None; initial_photo_visible = False
    if initial_photo_path: base_filename = os.path.basename(initial_photo_path); full_initial_photo_path = os.path.join(db.UPLOADS_DIR, base_filename);
    if full_initial_photo_path and os.path.exists(full_initial_photo_path): initial_photo_visible = True;
    else: print(f"Aviso: Foto inicial '{full_initial_photo_path}' não encontrada.")
    photo_image = ft.Image(ref=photo_image_ref, src=full_initial_photo_path if initial_photo_visible else None, width=200, height=200, fit=ft.ImageFit.CONTAIN, visible=initial_photo_visible)
    photo_image_preview_container = ft.Container(ref=photo_container_ref, content=photo_image, width=202, height=202, border_radius=ft.border_radius.all(5), border=ft.border.all(1, ft.colors.OUTLINE), visible=initial_photo_visible, alignment=ft.alignment.center, bgcolor=ft.colors.BACKGROUND)
    no_photo_text = ft.Text(ref=no_photo_text_ref, value="Nenhuma foto anexada.", italic=True, color=ft.colors.OUTLINE, visible=not initial_photo_visible)
    photo_stack = ft.Stack([photo_image_preview_container, no_photo_text])
    def trigger_photo_pick(e): photo_picker.pick_files(allow_multiple=False, allowed_extensions=["jpg", "jpeg", "png", "gif", "bmp"])
    pick_photo_button = ft.ElevatedButton("Selecionar/Alterar Foto", icon=ft.icons.UPLOAD_FILE, on_click=trigger_photo_pick)
    def remove_photo(e):
        if photo_image_ref.current: photo_image_ref.current.src = None; photo_image_ref.current.visible = False
        if photo_container_ref.current: photo_container_ref.current.visible = False
        if no_photo_text_ref.current: no_photo_text_ref.current.visible = True
        if photo_relative_path_text_ref.current: photo_relative_path_text_ref.current.value = ""
        if remove_photo_button_ref.current: remove_photo_button_ref.current.visible = False
        page.update(); show_snackbar(page, "Foto removida (efetivado ao salvar).", ft.colors.AMBER)
    remove_photo_button = ft.IconButton(ref=remove_photo_button_ref, icon=ft.icons.DELETE_FOREVER, tooltip="Remover Foto", icon_color=ft.colors.RED_ACCENT_700, on_click=remove_photo, visible=initial_photo_visible)
    photo_section = ft.Container(content=ft.Column([ft.Row([ft.Text("Foto Anexada", style=ft.TextThemeStyle.TITLE_SMALL), remove_photo_button], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), photo_stack, pick_photo_button, ft.Text(ref=photo_relative_path_text_ref, value=initial_photo_path or "", visible=False) ], spacing=10, horizontal_alignment=ft.CrossAxisAlignment.CENTER), padding=15, border=ft.border.all(1, ft.colors.OUTLINE_VARIANT), border_radius=ft.border_radius.all(8), width=250)


    # --- Função Salvar ---
    def save_os(e):
        # Validações...
        numero_os = numero_os_field.value.strip(); cliente_id = cliente_dd.value; status = status_dd.value; errors = False
        if not numero_os: numero_os_field.error_text = "*"; errors = True; 
        else: numero_os_field.error_text = None
        if not cliente_id: cliente_dd.error_text = "*"; errors = True; 
        else: cliente_dd.error_text = None
        if not status: status_dd.error_text = "*"; errors = True; 
        else: status_dd.error_text = None
        if errors: show_snackbar(page, "Preencha campos (*).", ft.colors.YELLOW_700); page.update(); return

        # --- Coleta e Conversão de Valor (CORRIGIDO) ---
        valor = None
        valor_str = valor_field.value.replace("R$ ", "").replace(",", ".").strip()
        if valor_str: # Processa somente se houver algo no campo
            try:
                valor = float(valor_str) # Tenta converter
            except ValueError:
                # Se a conversão falhar, mostra erro e retorna
                show_snackbar(page, "Valor Total inválido.", ft.colors.RED)
                valor_field.focus()
                page.update()
                return
        # Se valor_str for vazio, 'valor' permanecerá None, o que é ok.
        # -----------------------------------------------

        # Pega path da foto...
        foto_path_relativo = photo_relative_path_text_ref.current.value if photo_relative_path_text_ref.current else None

        # Converte Data Conclusão...
        data_conclusao_db = None
        data_conclusao_str = data_conclusao_field.value.strip()
        if data_conclusao_str:
            try: dt_conclusao = datetime.strptime(data_conclusao_str, '%d/%m/%Y'); data_conclusao_db = dt_conclusao.strftime('%Y-%m-%d')
            except ValueError: show_snackbar(page, "Data Conclusão inválida (DD/MM/YYYY).", ft.colors.RED); data_conclusao_field.focus(); page.update(); return

        # Monta dados...
        data = {
            'numero_os': numero_os, 'cliente_id': int(cliente_id),
            'tipo_servico_id': int(tipo_servico_dd.value) if tipo_servico_dd.value else None,
            'data_entrada': data_entrada_field.value,
            'descricao_problema': descricao_problema_field.value.strip() or None,
            'endereco_servico': endereco_servico_field.value.strip() or None,
            'garantia': garantia_field.value.strip() or None, 'status': status,
            'foto_path': foto_path_relativo, 'data_conclusao': data_conclusao_db,
            'valor': valor, 'observacoes': observacoes_field.value.strip() or None,
        }

        success = False; error_message = ""
        try:
            # Deletar foto antiga...
            delete_old_photo = False
            if is_editing and initial_photo_path and initial_photo_path != foto_path_relativo: delete_old_photo = True
            elif is_editing and initial_photo_path and not foto_path_relativo: delete_old_photo = True

            # Operação DB...
            if is_editing:
                success = db.update_ordem_servico(os_id, data); message = "OS atualizada!" if success else "Erro ao atualizar.";
                if not success: error_message = "Verifique Nº OS duplicado."
            else:
                new_id = db.add_ordem_servico(data); success = new_id is not None; message = f"OS Nº {numero_os} adicionada!" if success else "Erro ao adicionar.";
                if not success: error_message = "Verifique Nº OS/Cliente."

                if success:
                 # --- BLOCO CORRIGIDO ---
                 if delete_old_photo:
                     try:
                         # Constrói o caminho completo
                         old_full_path = os.path.join(db.UPLOADS_DIR, os.path.basename(initial_photo_path))
                         # Verifica se existe ANTES de tentar remover
                         if os.path.exists(old_full_path):
                             print(f"Tentando remover foto antiga: {old_full_path}")
                             os.remove(old_full_path) # Remove
                             print(f"Foto antiga removida com sucesso.")
                         else:
                             # Apenas informa se não foi encontrada
                             print(f"Foto antiga não encontrada para remover: {old_full_path}")
                     except Exception as del_err:
                         # Captura erros durante a construção do path ou remoção
                         print(f"Erro ao tentar remover foto antiga {initial_photo_path}: {del_err}")
                         print(traceback.format_exc()) # Log detalhes do erro
                 # ----------------------
                 show_snackbar(page, message, ft.colors.GREEN); page.go("/os")
                else: show_snackbar(page, f"{message} {error_message}", ft.colors.RED)
        except Exception as ex: print(f"Erro salvar OS: {ex}"); print(traceback.format_exc()); show_snackbar(page, f"Erro inesperado: {ex}", ft.colors.RED)
        finally: page.update()

    # --- Layout do Formulário ---
    form_column = ft.Column(
        [
            ft.Row([numero_os_field, data_entrada_field, status_dd], spacing=10),
            cliente_dd, tipo_servico_dd, ft.Divider(height=10),
            descricao_problema_field, endereco_servico_field, ft.Divider(height=10),
            ft.Row([ garantia_field, valor_field, ft.Row([data_conclusao_field, btn_pick_conclusion], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER) ], spacing=10),
            observacoes_field,
        ], spacing=12, width=700,
    )
    main_layout = ft.Row( [ ft.Container(content=form_column, padding=ft.padding.only(right=20)), photo_section,], vertical_alignment=ft.CrossAxisAlignment.START,)

    # --- View final ---
    return ft.View(
        f"/os/editar/{os_id}" if is_editing else "/os/nova",
        [
            ft.AppBar(title=ft.Text("Editar OS" if is_editing else "Nova OS"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container( content=ft.Column([ main_layout, ft.Divider(height=30), ft.Row([ ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, on_click=save_os, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE), ft.ElevatedButton("Cancelar", icon=ft.icons.CANCEL_OUTLINED, on_click=lambda _: page.go("/os")), ], alignment=ft.MainAxisAlignment.CENTER, spacing=20) ], scroll=ft.ScrollMode.ADAPTIVE, expand=True,), expand=True ),
        ], padding=20,
    )