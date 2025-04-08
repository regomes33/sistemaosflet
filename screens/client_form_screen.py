# screens/client_form_screen.py
import traceback
import flet as ft
import database as db
# Importa a show_snackbar simplificada que aceita page
from screens.home_screen import show_snackbar

# *** page É O OBJETO PRINCIPAL PASSADO AQUI ***
def create_client_form_view(page: ft.Page, client_id=None):
    """Cria a View do formulário de cliente (novo ou edição)."""
    is_editing = client_id is not None
    client_data = None

    if is_editing:
        client_data = db.get_cliente_by_id(client_id)
        if not client_data:
             # CORRETO: Usa 'page' da assinatura
             show_snackbar(page, f"Erro: Cliente ID {client_id} não encontrado.", ft.colors.RED)
             page.go("/clientes")
             return ft.View("/clientes/editar/error", [ft.Text("Redirecionando...")])

    # --- Campos do Formulário ---
    # ... (definição dos campos como antes) ...
    nome_field = ft.TextField(label="Nome Completo*", value=client_data['nome'] if is_editing else "", autofocus=True, width=400)
    cpf_cnpj_field = ft.TextField(label="CPF/CNPJ", value=client_data['cpf_cnpj'] if is_editing else "", width=200)
    telefone_field = ft.TextField(label="Telefone", value=client_data['telefone'] if is_editing else "", keyboard_type=ft.KeyboardType.PHONE, width=200)
    email_field = ft.TextField(label="Email", value=client_data['email'] if is_editing else "", keyboard_type=ft.KeyboardType.EMAIL, width=300)
    endereco_field = ft.TextField(label="Endereço (Rua, Av.)", value=client_data['endereco'] if is_editing else "", width=400)
    numero_field = ft.TextField(label="Número", value=client_data['numero'] if is_editing else "", width=100)
    complemento_field = ft.TextField(label="Complemento", value=client_data['complemento'] if is_editing else "", width=200)
    bairro_field = ft.TextField(label="Bairro", value=client_data['bairro'] if is_editing else "", width=250)
    cidade_field = ft.TextField(label="Cidade", value=client_data['cidade'] if is_editing else "", width=250)
    estado_field = ft.TextField(label="Estado (UF)", value=client_data['estado'] if is_editing else "", width=100, max_length=2, capitalization=ft.TextCapitalization.CHARACTERS)
    cep_field = ft.TextField(label="CEP", value=client_data['cep'] if is_editing else "", keyboard_type=ft.KeyboardType.NUMBER, width=150, max_length=9)


    def format_cep(e): # 'e' aqui é ok, só usamos para o update
        value = ''.join(filter(str.isdigit, cep_field.value))
        if len(value) > 5:
            value = f"{value[:5]}-{value[5:8]}"
        cep_field.value = value
        # Poderia usar page.update() aqui também, mas e.page.update() geralmente funciona
        if hasattr(e, 'page') and e.page:
            e.page.update()

    cep_field.on_change = format_cep

    # A função save_client AINDA recebe 'e', mas NÃO VAMOS USAR e.page
    def save_client(e: ft.ControlEvent):
        # *** USAREMOS 'page' DA FUNÇÃO EXTERNA create_client_form_view ***
        print(f"\n--- save_client: Usando 'page' ID: {id(page)} ---")

        nome = nome_field.value.strip()
        if not nome:
            nome_field.error_text = "Campo obrigatório"
            nome_field.focus()
            print("--- save_client: Validação falhou ---")
            try:
                # *** USA 'page' ***
                show_snackbar(page, "O campo 'Nome Completo' é obrigatório.", ft.colors.YELLOW_700)
            except Exception as snack_err:
                 print(f"!!! Erro ao chamar show_snackbar (validação): {snack_err}")
                 print(traceback.format_exc())
            # *** USA 'page' ***
            page.update()
            return
        else:
             nome_field.error_text = None

        # Coleta dados ...
        data = {
            'nome': nome,
            'cpf_cnpj': cpf_cnpj_field.value.strip() or None,
            'telefone': telefone_field.value.strip() or None,
            'email': email_field.value.strip() or None,
            'endereco': endereco_field.value.strip() or None,
            'numero': numero_field.value.strip() or None,
            'complemento': complemento_field.value.strip() or None,
            'bairro': bairro_field.value.strip() or None,
            'cidade': cidade_field.value.strip() or None,
            'estado': estado_field.value.strip() or None,
            'cep': cep_field.value.strip() or None,
        }

        success = False
        error_message = ""

        try:
            print(f"--- save_client: Antes DB. Usando page ID: {id(page)} ---")
            if is_editing:
                success = db.update_cliente(client_id, data)
                message = "Cliente atualizado com sucesso!" if success else "Erro ao atualizar cliente."
                if not success: error_message = "Verifique se o CPF/CNPJ já está em uso."
            else:
                print(f"Adicionando novo cliente com dados: {data}")
                new_id = db.add_cliente(data)
                success = new_id is not None
                print(f"Resultado de add_cliente (new_id): {new_id}, Sucesso: {success}")
                message = f"Cliente '{nome}' adicionado com sucesso!" if success else "Erro ao adicionar cliente."
                if not success: error_message = "Verifique se o CPF/CNPJ já existe."
            print(f"--- save_client: Após DB. Usando page ID: {id(page)} ---")

            if success:
                print("--- save_client: Sucesso DB ---")
                try:
                    # *** USA 'page' ***
                    show_snackbar(page, message, ft.colors.GREEN)
                except Exception as snack_err:
                    print(f"!!! Erro ao chamar show_snackbar (sucesso): {snack_err}")
                    print(traceback.format_exc())
                # *** USA 'page' ***
                page.go("/clientes")
            else:
                full_message = f"{message} {error_message}"
                print("--- save_client: Falha DB ---")
                try:
                    # *** USA 'page' ***
                    show_snackbar(page, full_message, ft.colors.RED)
                except Exception as snack_err:
                    print(f"!!! Erro ao chamar show_snackbar (falha): {snack_err}")
                    print(traceback.format_exc())

        except Exception as ex:
             print(f"--- save_client: Exceção Principal ---")
             print(f"Erro inesperado capturado: {ex}")
             full_message = f"Ocorreu um erro inesperado: {ex}"
             try:
                # *** USA 'page' ***
                 show_snackbar(page, full_message, ft.colors.RED)
             except Exception as snack_err:
                 print(f"!!! Erro ao chamar show_snackbar (exceção): {snack_err}")
                 print(traceback.format_exc())
        finally:
            print(f"--- save_client: Finally Block. Usando page ID: {id(page)} ---")
            try:
                # *** USA 'page' ***
                page.update()
                print("Update final OK.")
            except Exception as final_update_err:
                 print(f"!!! Erro no update final: {final_update_err}")
                 print(traceback.format_exc())

    # --- Retorno da View ---
    # O 'on_click=save_client' ainda funciona, passando 'e' para save_client,
    # mas save_client agora ignora 'e.page' e usa a 'page' do escopo externo.
    # O 'on_click' do botão Cancelar também usa a 'page' do escopo externo.
    return ft.View(
        f"/clientes/editar/{client_id}" if is_editing else "/clientes/novo",
        [
            ft.AppBar(title=ft.Text("Editar Cliente" if is_editing else "Novo Cliente"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT),
            ft.Column(
                 [
                    ft.Text("Dados Pessoais", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    nome_field,
                    ft.Row([cpf_cnpj_field, telefone_field]),
                    email_field,
                    ft.Divider(height=20),
                    ft.Text("Endereço", style=ft.TextThemeStyle.TITLE_MEDIUM),
                    endereco_field,
                    ft.Row([numero_field, complemento_field]),
                    bairro_field,
                    ft.Row([cidade_field, estado_field, cep_field]),
                    ft.Divider(height=30),
                    ft.Row(
                        [
                            ft.ElevatedButton("Salvar", icon=ft.icons.SAVE, on_click=save_client, bgcolor=ft.colors.GREEN_700, color=ft.colors.WHITE),
                            ft.ElevatedButton("Cancelar", icon=ft.icons.CANCEL_OUTLINED, on_click=lambda _: page.go("/clientes")),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER, spacing=20
                    )
                ],
                scroll=ft.ScrollMode.ADAPTIVE,
                spacing=15,
                expand=True
            )
        ],
        padding=20
    )