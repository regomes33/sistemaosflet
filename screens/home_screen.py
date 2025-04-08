# screens/home_screen.py
import flet as ft

def create_home_view(page: ft.Page):
    """Cria a View da tela inicial/menu."""
    return ft.View(
        "/",  # Rota raiz
        [
            ft.AppBar(title=ft.Text("Sistema de OS - Início"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Container(height=50), # Espaçamento
            ft.Row(
                [
                    ft.ElevatedButton(
                        "Gerenciar Clientes",
                        icon=ft.icons.PEOPLE_OUTLINE,
                        on_click=lambda _: page.go("/clientes"),
                        width=250,
                        height=50,
                    )
                ], alignment=ft.MainAxisAlignment.CENTER
            ),
            ft.Container(height=20),
             ft.Row(
                [
                    ft.ElevatedButton(
                        "Tipos de Serviço",
                        icon=ft.icons.CONSTRUCTION_OUTLINED,
                        on_click=lambda _: page.go("/tipos_servico"),
                        width=250,
                        height=50,
                    )
                ], alignment=ft.MainAxisAlignment.CENTER
            ),
             ft.Container(height=20),
             ft.Row(
                [
                    ft.ElevatedButton(
                        "Ordens de Serviço",
                        icon=ft.icons.RECEIPT_LONG_OUTLINED,
                        on_click=lambda _: page.go("/os"),
                        width=250,
                        height=50,
                    )
                ], alignment=ft.MainAxisAlignment.CENTER
            ),
             ft.Container(height=20),
             ft.Row(
                [
                    ft.ElevatedButton(
                        "Gerar Relatórios",
                        icon=ft.icons.ASSESSMENT_OUTLINED,
                        on_click=lambda _: page.go("/relatorios"),
                        width=250,
                        height=50,
                    )
                ], alignment=ft.MainAxisAlignment.CENTER
            ),
        ],
        vertical_alignment=ft.MainAxisAlignment.START, # Alinha os botões ao topo após AppBar
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        padding=20,
    )

# Funções utilitárias (podem ser movidas para main.py ou utils.py se usadas em mais lugares)
def show_snackbar(page: ft.Page, message: str, color: str = ft.colors.BLACK):
    """Exibe uma SnackBar na página fornecida."""
    if page and isinstance(page, ft.Page): # Adiciona verificação de tipo por segurança
        try:
            page.show_snack_bar(ft.SnackBar(
                content=ft.Text(message),
                bgcolor=color
            ))
        except Exception as snack_err:
            print(f"Erro ao tentar mostrar SnackBar: {snack_err}")
            # Fallback: Imprimir no console se falhar
            print(f"SNACKBAR FALLBACK ({color}): {message}")
    else:
        print(f"WARN: Página inválida ou não fornecida para show_snackbar: {message}")


# Função close_dialog permanece a mesma (espera 'e')
def close_dialog(e: ft.ControlEvent):
    page = e.page
    if hasattr(page, 'dialog') and page.dialog:
        page.dialog.open = False
        # Use e.page.update() para segurança
        if page: page.update()


# Função show_confirmation_dialog permanece a mesma (passa 'e' para os callbacks)
def show_confirmation_dialog(page: ft.Page, title: str, content: str, on_confirm):
    confirm_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text(title),
        content=ft.Text(content),
        actions=[
            ft.TextButton("Confirmar", on_click=lambda e_btn: (on_confirm(e_btn), close_dialog(e_btn)), style=ft.ButtonStyle(color=ft.colors.RED)),
            ft.TextButton("Cancelar", on_click=close_dialog),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
        on_dismiss=lambda e_dismiss: print("Diálogo de confirmação fechado"),
    )
    page.dialog = confirm_dialog
    confirm_dialog.open = True
    page.update()