# screens/service_type_form_screen.py
import flet as ft
import database as db
from screens.home_screen import show_snackbar

def create_service_type_form_view(page: ft.Page, type_id=None):
    """Cria a View do formulário de tipo de serviço (novo ou edição)."""
    is_editing = type_id is not None
    type_data = None

    if is_editing:
        type_data = db.get_tipo_servico_by_id(type_id)
        if not type_data:
            show_snackbar(page, f"Erro: Tipo de Serviço ID {type_id} não encontrado.", ft.colors.RED)
            page.go("/tipos_servico")
            return ft.View("/tipos_servico/editar/error", [ft.Text("Redirecionando...")])

    # --- Campos ---
    nome_field = ft.TextField(label="Nome do Tipo de Serviço*", value=type_data['nome'] if is_editing else "", autofocus=True, width=400)
    descricao_field = ft.TextField(label="Descrição (Opcional)", value=type_data['descricao'] if is_editing else "", multiline=True, min_lines=3, max_lines=5, width=400)

    def save_type(e):
        nome = nome_field.value.strip()
        if not nome:
            show_snackbar(page, "O campo 'Nome' é obrigatório.", ft.colors.YELLOW_700)
            nome_field.error_text = "Campo obrigatório"
            nome_field.focus()
            page.update()
            return
        else:
            nome_field.error_text = None

        descricao = descricao_field.value.strip() or None

        success = False
        error_message = ""
        try:
            if is_editing:
                print(f"Atualizando tipo serviço ID: {type_id} com nome: {nome}")
                success = db.update_tipo_servico(type_id, nome, descricao)
                message = "Tipo de Serviço atualizado com sucesso!" if success else "Erro ao atualizar Tipo de Serviço."
                if not success: error_message = "Verifique se o nome já está em uso."
            else:
                print(f"Adicionando novo tipo serviço com nome: {nome}")
                new_id = db.add_tipo_servico(nome, descricao)
                success = new_id is not None
                message = f"Tipo de Serviço '{nome}' adicionado com sucesso!" if success else "Erro ao adicionar Tipo de Serviço."
                if not success: error_message = "Verifique se o nome já existe."

            if success:
                show_snackbar(page, message, ft.colors.GREEN)
                page.go("/tipos_servico")
            else:
                show_snackbar(page, f"{message} {error_message}", ft.colors.RED)

        except Exception as ex:
            print(f"Erro inesperado ao salvar tipo de serviço: {ex}")
            show_snackbar(page, f"Ocorreu um erro inesperado: {ex}", ft.colors.RED)
        finally:
            page.update()

    return ft.View(
        f"/tipos_servico/editar/{type_id}" if is_editing else "/tipos_servico/novo",
        [
            ft.AppBar(title=ft.Text("Editar Tipo de Serviço" if is_editing else "Novo Tipo de Serviço"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(
                [
                    nome_field,
                    descricao_field,
                    ft.Divider(height=30),
                    ft.Row(
                        [
                            ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, on_click=save_type, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
                            ft.ElevatedButton("Cancelar", icon=ft.icons.CANCEL_OUTLINED, on_click=lambda _: page.go("/tipos_servico")),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=20
                    )
                ],
                spacing=15,
                # Centraliza o formulário na tela
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        ],
        padding=20,
        # Centraliza a coluna verticalmente (opcional)
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )