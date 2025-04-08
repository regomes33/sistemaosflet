# screens/os_list_screen.py
import flet as ft
import database as db
from screens.home_screen import show_snackbar, show_confirmation_dialog
import os # Para verificar existência da foto

def create_os_list_view(page: ft.Page):
    """Cria a View de listagem de Ordens de Serviço."""

    os_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Nº OS")),
            ft.DataColumn(ft.Text("Cliente")),
            ft.DataColumn(ft.Text("Tipo Serviço")),
            ft.DataColumn(ft.Text("Data Entrada")),
            ft.DataColumn(ft.Text("Status")),
            ft.DataColumn(ft.Text("Foto")),
            ft.DataColumn(ft.Text("Ações"), numeric=True),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.BLACK26),
        vertical_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        sort_column_index=3, # Ordenar por Data Entrada inicialmente
        sort_ascending=False, # Mais recentes primeiro
        heading_row_color=ft.colors.BLACK12,
        width=page.width - 40 if page.width else 1200,
        expand=False,
    )

    def load_os():
        print("Carregando Ordens de Serviço...")
        try:
            oss = db.get_all_ordens_servico()
            os_table.rows.clear()
            if oss:
                for os_item in oss:
                     # Verifica se a foto existe
                    foto_icon = ft.icons.IMAGE_NOT_SUPPORTED_OUTLINED
                    foto_tooltip = "Sem foto"
                    if os_item['foto_path']:
                        # Usa o caminho relativo armazenado para construir o caminho completo
                        # Assume que UPLOADS_DIR está na raiz do projeto
                        full_foto_path = os.path.join(db.UPLOADS_DIR, os.path.basename(os_item['foto_path']))
                        if os.path.exists(full_foto_path):
                             foto_icon = ft.icons.IMAGE_OUTLINED
                             foto_tooltip = f"Ver foto: {os.path.basename(os_item['foto_path'])}" # Mostrar nome do arquivo no tooltip
                        else:
                             foto_icon = ft.icons.BROKEN_IMAGE_OUTLINED
                             foto_tooltip = f"Foto não encontrada: {os.path.basename(os_item['foto_path'])}"


                    os_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(os_item['numero_os'])),
                                ft.DataCell(ft.Text(os_item['nome_cliente'] or "Cliente Excluído", color=ft.colors.RED if not os_item['nome_cliente'] else None)),
                                ft.DataCell(ft.Text(os_item['nome_tipo_servico'] or "N/A")),
                                ft.DataCell(ft.Text(os_item['data_entrada'])),
                                ft.DataCell(ft.Text(os_item['status'])),
                                ft.DataCell(ft.IconButton(icon=foto_icon, tooltip=foto_tooltip, disabled=foto_icon != ft.icons.IMAGE_OUTLINED)), # Ícone indicando foto
                                ft.DataCell(ft.Row([
                                    ft.IconButton(ft.icons.EDIT_OUTLINED, tooltip="Editar", on_click=lambda _, o=os_item: page.go(f"/os/editar/{o['id']}")),
                                    ft.IconButton(ft.icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, o=os_item: confirm_delete_os(o['id'], o['numero_os'])),
                                ])),
                            ]
                        )
                    )
            else:
                 os_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Nenhuma Ordem de Serviço cadastrada.", italic=True), col_span=7)]))
            page.update()
            print("OS carregadas.")
        except Exception as e:
            print(f"Erro ao carregar OS: {e}")
            show_snackbar(page, f"Erro ao carregar Ordens de Serviço: {e}", ft.colors.RED)

    def confirm_delete_os(os_id, os_numero):
        def on_delete(e):
            print(f"Tentando excluir OS ID: {os_id}")
            # A função delete_ordem_servico em database.py já tenta deletar a foto associada
            if db.delete_ordem_servico(os_id):
                show_snackbar(page, f"Ordem de Serviço Nº {os_numero} excluída com sucesso!", ft.colors.GREEN)
                load_os()
            else:
                show_snackbar(page, f"Erro ao excluir Ordem de Serviço Nº {os_numero}.", ft.colors.RED)
            # close_dialog(e)

        show_confirmation_dialog(
            page,
            title="Confirmar Exclusão",
            content=f"Tem certeza que deseja excluir a Ordem de Serviço Nº {os_numero} (ID: {os_id})?\nEsta ação não pode ser desfeita.",
            on_confirm=on_delete
        )

    table_container = ft.Container(
        content=ft.Row([os_table], scroll=ft.ScrollMode.ADAPTIVE),
        padding=10,
        border_radius=5,
    )

    view = ft.View(
        "/os",
        [
            ft.AppBar(title=ft.Text("Ordens de Serviço"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Row(
                [
                    ft.ElevatedButton("Abrir Nova OS", icon=ft.icons.ADD, on_click=lambda _: page.go("/os/nova")),
                    ft.Container(expand=True),
                    ft.IconButton(ft.icons.REFRESH, tooltip="Atualizar Lista", on_click=lambda _: load_os()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            ft.Column([table_container], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
        ],
        padding=20,
        vertical_alignment=ft.MainAxisAlignment.START,
    )

    def on_view_mount(e):
        load_os()

    view.on_mount = on_view_mount
    return view