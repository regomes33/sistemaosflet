# screens/client_list_screen.py
import flet as ft
import database as db
from screens.home_screen import show_snackbar, show_confirmation_dialog # Reutiliza helpers

def create_client_list_view(page: ft.Page):
    """Cria a View de listagem de clientes."""

    clients_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("ID")),
            ft.DataColumn(ft.Text("Nome")),
            ft.DataColumn(ft.Text("Telefone")),
            ft.DataColumn(ft.Text("Email")),
            ft.DataColumn(ft.Text("Cidade")),
            ft.DataColumn(ft.Text("Ações"), numeric=True), # Alinha à direita
        ],
        rows=[],
        border=ft.border.all(1, ft.colors.BLACK26),
        vertical_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        horizontal_lines=ft.border.BorderSide(1, ft.colors.BLACK12),
        sort_column_index=1, # Ordenar por nome inicialmente
        sort_ascending=True,
        heading_row_color=ft.colors.BLACK12,
        width=page.width - 40 if page.width else 1000, # Ajusta largura
        expand=False, # Não expandir automaticamente, usar width
    )

    def load_clients():
        print("Carregando clientes...")
        try:
            clients = db.get_all_clientes()
            clients_table.rows.clear()
            if clients:
                for client in clients:
                    clients_table.rows.append(
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(client['id']))),
                                ft.DataCell(ft.Text(client['nome'])),
                                ft.DataCell(ft.Text(client['telefone'] or "-")),
                                ft.DataCell(ft.Text(client['email'] or "-")),
                                ft.DataCell(ft.Text(client['cidade'] or "-")),
                                ft.DataCell(ft.Row([
                                    ft.IconButton(ft.icons.EDIT_OUTLINED, tooltip="Editar", on_click=lambda _, c=client: page.go(f"/clientes/editar/{c['id']}")),
                                    ft.IconButton(ft.icons.DELETE_OUTLINE, tooltip="Excluir", on_click=lambda _, c=client: confirm_delete_client(c['id'], c['nome'])),
                                ])),
                            ]
                        )
                    )
            else:
                 clients_table.rows.append(ft.DataRow(cells=[ft.DataCell(ft.Text("Nenhum cliente cadastrado.", italic=True), col_span=6)]))
            page.update()
            print("Clientes carregados.")
        except Exception as e:
            print(f"Erro ao carregar clientes: {e}")
            show_snackbar(page, f"Erro ao carregar clientes: {e}", ft.colors.RED)


    def confirm_delete_client(client_id, client_name):
        def on_delete(e):
            print(f"Tentando excluir cliente ID: {client_id}")
            if db.delete_cliente(client_id):
                 show_snackbar(page, f"Cliente '{client_name}' excluído com sucesso!", ft.colors.GREEN)
                 load_clients() # Recarrega a lista
            else:
                 show_snackbar(page, f"Erro ao excluir cliente '{client_name}'. Verifique se ele possui Ordens de Serviço associadas.", ft.colors.RED)
            # close_dialog(e) # Já é chamado no TextButton

        show_confirmation_dialog(
            page,
            title="Confirmar Exclusão",
            content=f"Tem certeza que deseja excluir o cliente '{client_name}' (ID: {client_id})?\n\nATENÇÃO: Todas as Ordens de Serviço associadas a este cliente também serão excluídas!",
            on_confirm=on_delete
        )

    # Container para a tabela permitir rolagem horizontal se necessário
    table_container = ft.Container(
        content=ft.Row([clients_table], scroll=ft.ScrollMode.ADAPTIVE), # Habilita rolagem horizontal
        padding=10,
        border_radius=5,
    )

    view = ft.View(
        "/clientes",
        [
            ft.AppBar(title=ft.Text("Gerenciar Clientes"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Row(
                [
                    ft.ElevatedButton("Adicionar Novo Cliente", icon=ft.icons.ADD, on_click=lambda _: page.go("/clientes/novo")),
                    ft.Container(expand=True), # Empurra o botão de refresh para a direita
                    ft.IconButton(ft.icons.REFRESH, tooltip="Atualizar Lista", on_click=lambda _: load_clients()),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            ft.Divider(),
            ft.Column([table_container], scroll=ft.ScrollMode.ADAPTIVE, expand=True), # Habilita rolagem vertical
        ],
        padding=20,
        vertical_alignment=ft.MainAxisAlignment.START,
    )

    # Carrega os dados quando a view é montada pela primeira vez
    # Usar on_mount garante que a page esteja disponível
    def on_view_mount(e):
        load_clients()

    view.on_mount = on_view_mount # Define a função a ser chamada no mount

    return view