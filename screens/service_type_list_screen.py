# screens/service_type_list_screen.py
import flet as ft
import database as db
from screens.home_screen import show_snackbar, show_confirmation_dialog

def create_service_type_list_view(page: ft.Page):
    """Cria a View de listagem de tipos de serviço."""

    types_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Descrição")),
            ft.DataColumn(ft.Text("Ações"), numeric=True),
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.BLACK26),
        vertical_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        sort_column_index=1,
        sort_ascending=True,
        heading_row_color=ft.colors.BLACK12,
        width=page.width - 40 if page.width else 800,
        expand=False,
    )

    def load_types():
        print("Carregando tipos de serviço...")
        try:
            types = db.get_all_tipos_servico()
            types_table.rows.clear()
            if types:
                for stype in types:
                    types_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(stype['id']))),
                                ft.DataCell(ft.Text(stype['nome'])),
                                ft.DataCell(ft.Text(stype['descricao'] or "-", overflow=ft.TextOverflow.ELLIPSIS, max_lines=2)),
                                ft.DataCell(ft.Row([
                                    ft.IconButton(ft.icons.EDIT_OUTLINED, tooltip="Editar", on_click=lambda _, s=stype: page.go(f"/tipos_servico/editar/{s['id']}")),
                                    ft.IconButton(ft.icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, s=stype: confirm_delete_type(s['id'], s['nome'])),
                                ])),
                            ]
                        )
                    )
            else:
                types_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Nenhum tipo de serviço cadastrado.", italic=True), col_span=4)]))
            page.update()
            print("Tipos carregados.")
        except Exception as e:
            print(f"Erro ao carregar tipos de serviço: {e}")
            show_snackbar(page, f"Erro ao carregar tipos: {e}", ft.colors.RED)

    def confirm_delete_type(type_id, type_name):
        def on_delete(e):
            print(f"Tentando excluir tipo de serviço ID: {type_id}")
            if db.delete_tipo_servico(type_id):
                show_snackbar(page, f"Tipo de Serviço '{type_name}' excluído com sucesso!", ft.colors.GREEN)
                load_types()
            else:
                # A função delete_tipo_servico no database.py pode ser modificada
                # para retornar uma mensagem mais específica se estiver em uso.
                show_snackbar(page, f"Erro ao excluir '{type_name}'. Verifique se ele não está sendo usado em alguma Ordem de Serviço.", ft.colors.RED)
            # close_dialog(e)

        show_confirmation_dialog(
            page,
            title="Confirmar Exclusão",
            content=f"Tem certeza que deseja excluir o Tipo de Serviço '{type_name}' (ID: {type_id})?",
            on_confirm=on_delete
        )

    table_container = ft.Container(
        content=ft.Row([types_table], scroll=ft.ScrollMode.ADAPTIVE),
        padding=10,
        border_radius=5,
    )

    view = ft.View(
        "/tipos_servico",
        [
            ft.AppBar(title=ft.Text("Tipos de Serviço"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Row(
                [
                    ft.ElevatedButton("Adicionar Novo Tipo", icon=ft.icons.ADD, on_click=lambda _: page.go("/tipos_servico/novo")),
                    ft.Container(expand=True),
                    ft.IconButton(ft.icons.REFRESH, tooltip="Atualizar Lista", on_click=lambda _: load_types()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            ft.Column([table_container], scroll=ft.ScrollMode.ADAPTIVE, expand=True),
        ],
        padding=20,
        vertical_alignment=ft.MainAxisAlignment.START,
    )

    def on_view_mount(e):
        load_types()

    view.on_mount = on_view_mount
    return view