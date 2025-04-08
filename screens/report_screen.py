# screens/report_screen.py
import flet as ft
import database as db
import utils
# Importa a show_snackbar simplificada que aceita 'page'
from screens.home_screen import show_snackbar
from datetime import datetime
import os
import traceback
import time # Importar time para gerar IDs únicos rapidamente

# 'page' AQUI É A INSTÂNCIA PRINCIPAL PASSADA
def create_report_view(page: ft.Page, report_save_picker: ft.FilePicker):
    """Cria a View para geração de relatórios."""

    # Refs internas para DatePicker...
    date_picker_ref = ft.Ref[ft.DatePicker]()
    target_date_field_ref = ft.Ref[ft.TextField]()

    # Carregar dados...
    try: clientes = db.get_all_clientes()
    except Exception as e: show_snackbar(page, f"Erro ao carregar clientes: {e}", ft.colors.RED); clientes = []
    cliente_options = [ft.dropdown.Option(key="", text="-- Todos os Clientes --")]
    cliente_options.extend([ft.dropdown.Option(key=c['id'], text=c['nome']) for c in clientes])
    status_options = [ft.dropdown.Option(key="", text="-- Todos os Status --"), ft.dropdown.Option("Aberta"), ft.dropdown.Option("Em Andamento"), ft.dropdown.Option("Aguardando Peças"), ft.dropdown.Option("Concluída"), ft.dropdown.Option("Cancelada"),]

    # Controles de Filtro...
    cliente_filter_dd = ft.Dropdown(label="Filtrar por Cliente", options=cliente_options, value="", width=350)
    status_filter_dd = ft.Dropdown(label="Filtrar por Status", options=status_options, value="", width=250)
    data_inicio_field = ft.TextField(label="Data Início", hint_text="DD/MM/YYYY", width=180, read_only=True)
    data_fim_field = ft.TextField(label="Data Fim", hint_text="DD/MM/YYYY", width=180, read_only=True)

    # Callback DatePicker (usa e.page que funciona para update aqui)
    def on_date_selected(e):
        date_picker = date_picker_ref.current; target_field = target_date_field_ref.current; page_from_event = e.page
        if date_picker and target_field and page_from_event:
            selected_date = date_picker.value
            if selected_date: formatted_date = selected_date.strftime('%d/%m/%Y'); target_field.value = formatted_date; print(f"Data selecionada ({target_field.label}): {formatted_date}")
            date_picker.open = False; page_from_event.update()
        else: print("Erro on_date_selected: Refs ou Page não encontrados.")

    # Cria DatePicker...
    date_picker = ft.DatePicker(ref=date_picker_ref, on_change=on_date_selected, on_dismiss=lambda e: print("DatePicker fechado."), first_date=datetime(2020, 1, 1), last_date=datetime.now().replace(year=datetime.now().year + 5), help_text="Selecione a data", cancel_text="Cancelar", confirm_text="Confirmar")
    if date_picker not in page.overlay: page.overlay.append(date_picker)

    # Abre DatePicker (usa e.page que funciona para update aqui)
    def open_date_picker(e, target_field: ft.TextField):
        page_from_event = e.page
        if not page_from_event: print("Erro open_date_picker: Page não encontrada."); return
        print(f"Abrindo DatePicker para o campo: {target_field.label}"); target_date_field_ref.current = target_field
        if date_picker_ref.current: date_picker_ref.current.open = True; page_from_event.update()
        else: print("Erro open_date_picker: Referência do DatePicker não encontrada.")

    # Botões Calendário...
    btn_pick_inicio = ft.IconButton(ft.icons.CALENDAR_MONTH, tooltip="Selecionar Data Início", on_click=lambda e: open_date_picker(e, data_inicio_field))
    btn_pick_fim = ft.IconButton(ft.icons.CALENDAR_MONTH, tooltip="Selecionar Data Fim", on_click=lambda e: open_date_picker(e, data_fim_field))

    # Feedback...
    progress_ring = ft.ProgressRing(visible=False, width=20, height=20, stroke_width=3)
    status_text = ft.Text("")

    # --- Botão Gerar Relatório ---
    def generate_report(e: ft.ControlEvent):
        if not page: print("ERRO CRÍTICO generate_report: Page principal não encontrada."); return

        progress_ring.visible = True; status_text.value = "Gerando..."; page.update()

        cliente_id = cliente_filter_dd.value or None; status = status_filter_dd.value or None
        data_inicio_str = data_inicio_field.value.strip(); data_fim_str = data_fim_field.value.strip()
        data_inicio_db = None; data_fim_db = None
        try:
            if data_inicio_str: data_inicio_db = datetime.strptime(data_inicio_str, '%d/%m/%Y').strftime('%Y-%m-%d')
            if data_fim_str: data_fim_db = datetime.strptime(data_fim_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            show_snackbar(page, "Formato data inválido (DD/MM/YYYY).", ft.colors.RED)
            status_text.value = "Erro: Data inválida."; progress_ring.visible = False; page.update(); return

        try:
            print(f"Filtros (DB): Cli={cliente_id}, Sts={status}, DtIni={data_inicio_db}, DtFim={data_fim_db}")
            ordens_filtradas = db.get_ordens_servico_filtradas(cliente_id, status, data_inicio_db, data_fim_db)

            # <<< --- INÍCIO DO BLOCO DE DEBUG --- >>>
            if ordens_filtradas:
                print("\n--- DEBUG: Dados recebidos de db.get_ordens_servico_filtradas ---")
                for index, os_data in enumerate(ordens_filtradas):
                    # Imprime cada dicionário/objeto retornado pelo banco de dados
                    print(f"OS #{index+1}: {os_data}")
                print("--- FIM DEBUG ---\n")
            else:
                print("\n--- DEBUG: Nenhuma OS encontrada pelos filtros (db.get_ordens_servico_filtradas retornou vazio). ---\n")
            # <<< --- FIM DO BLOCO DE DEBUG --- >>>

            if not ordens_filtradas:
                show_snackbar(page, "Nenhuma OS encontrada com os filtros aplicados.", ft.colors.AMBER) # Mensagem mais específica
                status_text.value = "Nenhum resultado."; progress_ring.visible = False; page.update(); return

            print(f"{len(ordens_filtradas)} OS encontradas. Gerando PDF..."); status_text.value = f"{len(ordens_filtradas)} OS. Gerando PDF..."; page.update()

            # --- GERAÇÃO DO NOME DO ARQUIVO SUGESTIVO (CORRIGIDO) ---
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cliente_nome_display = "Desconhecido" # Default
            if cliente_filter_dd.value: # Se um cliente específico foi selecionado
                 selected_option = next((opt for opt in cliente_options if opt.key == cliente_filter_dd.value), None)
                 if selected_option:
                     # Usar o texto da opção selecionada que já deve ser o nome
                     cliente_nome_display = selected_option.text
                 else:
                     # Fallback se a opção não for encontrada (improvável mas seguro)
                     cliente_nome_display = f"Cliente_{cliente_filter_dd.value}"
            else: # Se "-- Todos os Clientes --" foi selecionado
                 cliente_nome_display = "TodosClientes"

            status_nome = status_filter_dd.value if status_filter_dd.value else "TodosStatus"
            safe_cliente_nome = utils.sanitize_filename(cliente_nome_display)[:30] # Sanitiza e limita

            pdf_suggested_filename = f"RelatorioOS_{safe_cliente_nome}_{status_nome}_{timestamp}.pdf"
            # ----------------------------------------------------------

            # --- NOME DO ARQUIVO TEMPORÁRIO ÚNICO ---
            temp_pdf_filename = f"temp_report_{int(time.time() * 1000)}.pdf"
            # --------------------------------------

            # Chama a função de geração de PDF com os dados filtrados
            pdf_filepath = utils.generate_os_pdf_report(ordens_filtradas, filename=temp_pdf_filename) # Usa nome temp

            if pdf_filepath and os.path.exists(pdf_filepath):
                 print(f"PDF temporário gerado: {pdf_filepath}")
                 status_text.value = "PDF gerado! Escolha onde salvar."; progress_ring.visible = False; page.update()

                 page.session.set("temp_report_path", pdf_filepath) # Guarda caminho temp na sessão
                 print(f"Caminho temp salvo na sessão: {page.session.get('temp_report_path')}")

                 report_save_picker.save_file(
                     dialog_title="Salvar Relatório PDF Como...",
                     file_name=pdf_suggested_filename, # Usa o nome sugestivo
                     allowed_extensions=["pdf"]
                 )
            else:
                # Se pdf_filepath for None ou o arquivo não existir após a chamada
                raise Exception(f"Falha ao gerar ou localizar o arquivo PDF temporário: {temp_pdf_filename}")

        except Exception as ex:
            print(f"Erro ao gerar relatório: {ex}"); print(traceback.format_exc())
            show_snackbar(page, f"Erro ao gerar relatório: {ex}", ft.colors.RED) # Exibe erro para o usuário
            status_text.value = f"Erro ao gerar."; progress_ring.visible = False; page.update() # Atualiza status na tela

    # --- Layout da View ---
    return ft.View(
        "/relatorios",
        [
             ft.AppBar(title=ft.Text("Relatório de Ordens de Serviço"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Text("Selecione os filtros:", style=ft.TextThemeStyle.TITLE_MEDIUM),
            ft.Divider(),
            ft.Row([cliente_filter_dd, status_filter_dd], alignment=ft.MainAxisAlignment.START, spacing=20),
            ft.Row( # Datas
                [
                    ft.Row([data_inicio_field, btn_pick_inicio], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([data_fim_field, btn_pick_fim], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                ], alignment=ft.MainAxisAlignment.START, spacing=20
            ),
            ft.Divider(height=30),
            ft.Row( # Botão e Status
                [
                    ft.ElevatedButton("Gerar Relatório PDF", icon=ft.icons.PICTURE_AS_PDF, on_click=generate_report, height=50),
                    progress_ring, status_text,
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=15
            )
        ], padding=20, vertical_alignment=ft.MainAxisAlignment.START,
    )