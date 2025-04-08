# utils.py
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.units import cm
from reportlab.lib import colors
from PIL import Image as PILImage
import traceback # Para logs
import sqlite3 # Para poder usar dict() em sqlite3.Row

import database as db

def sanitize_filename(filename):
    """Remove caracteres inválidos para nomes de arquivo."""
    return "".join(c for c in filename if c.isalnum() or c in (' ', '.', '_')).rstrip()

# --- FUNÇÃO CORRIGIDA NOVAMENTE ---
def generate_os_pdf_report(ordens_servico, filename="relatorio_os.pdf"):
    """Gera um PDF com os detalhes das Ordens de Serviço fornecidas."""
    filepath = os.path.join(db.REPORTS_DIR, filename)
    doc = SimpleDocTemplate(filepath, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Estilos
    title_style = styles['h1']; title_style.alignment = TA_CENTER; title_style.fontSize = 18
    normal_style = styles['Normal']; normal_style.fontSize = 10; normal_style.leading = 12
    normal_style_right = styles['Normal']; normal_style_right.fontSize = 10; normal_style_right.alignment = TA_RIGHT; normal_style_right.leading = 12
    header_style = styles['h2']; header_style.fontSize = 12; header_style.spaceAfter = 6

    story.append(Paragraph("Relatório de Ordens de Serviço", title_style))
    story.append(Spacer(1, 1*cm))

    if not ordens_servico:
        # (Código para PDF vazio permanece o mesmo)
        story.append(Paragraph("Nenhuma OS encontrada para os filtros.", normal_style))
        try:
            doc.build(story)
        except Exception as e:
             print(f"Erro ao gerar PDF vazio: {e}")
             print(traceback.format_exc())
             return None
        return filepath

    # Helper para acesso seguro a sqlite3.Row
    def safe_get(row, key, default=None):
         try:
             # Verifica se a chave existe ANTES de tentar acessar
             # As chaves de sqlite3.Row são obtidas com .keys()
             if key in row.keys():
                 return row[key] # Acessa se a chave existe
             else:
                 return default
         except (KeyError, IndexError): # Segurança extra
             return default

    for i, os_data in enumerate(ordens_servico): # Usando enumerate para índice

        # --- DEBUG PRINT (Mantido) ---
        # Usa safe_get para o ID no print também, por segurança
        print(f"\n--- DEBUG (utils.py): Processando OS #{i+1} (ID: {safe_get(os_data, 'id', '??')}) ---")
        if isinstance(os_data, sqlite3.Row):
            # Tenta converter para dict para visualização (pode falhar se houver nomes duplicados)
             try:
                print(dict(os_data))
             except Exception as dict_err:
                 print(f"Erro ao converter Row para dict no debug: {dict_err}")
                 print(f"Conteúdo da Row (via keys): {[ (key, safe_get(os_data, key)) for key in os_data.keys() ]}")

        else:
            print(os_data) # Se não for Row, imprime como está
        print("--- FIM DEBUG (utils.py) ---\n")
        # --- FIM DEBUG PRINT ---

        try:
            # Verifica se é um sqlite3.Row ou similar antes de continuar
            if not isinstance(os_data, sqlite3.Row):
                 raise TypeError(f"Esperado um objeto sqlite3.Row, mas recebeu {type(os_data)}")

            # --- Usando safe_get() helper para acesso seguro ---
            numero_os_str = str(safe_get(os_data, 'numero_os', 'N/A'))
            story.append(Paragraph(f"Ordem de Serviço Nº: {numero_os_str}", header_style))

            # --- Dados do Cliente ---
            nome_cli = safe_get(os_data, 'nome_cliente') or 'N/A'
            end_cli = safe_get(os_data, 'endereco_cliente') or ''
            cid_cli = safe_get(os_data, 'cidade_cliente') or ''
            est_cli = safe_get(os_data, 'estado_cliente') or ''
            tel_cli = safe_get(os_data, 'telefone_cliente') or 'N/A'
            email_cli = safe_get(os_data, 'email_cliente') or 'N/A'

            # (Formatação do endereço permanece a mesma)
            endereco_parts = [part for part in [end_cli, cid_cli] if part]
            endereco_completo_cli = ", ".join(endereco_parts)
            if est_cli:
                endereco_completo_cli += f" - {est_cli}"
            if not endereco_completo_cli:
                endereco_completo_cli = "N/A"

            cliente_data = [
                [Paragraph("<b>Cliente:</b>", normal_style), Paragraph(nome_cli, normal_style)],
                [Paragraph("<b>Endereço:</b>", normal_style), Paragraph(endereco_completo_cli, normal_style)],
                [Paragraph("<b>Telefone:</b>", normal_style), Paragraph(tel_cli, normal_style)],
                [Paragraph("<b>Email:</b>", normal_style), Paragraph(email_cli, normal_style)],
            ]
            # (Código da tabela de cliente permanece o mesmo)
            cliente_table = Table(cliente_data, colWidths=[4*cm, None])
            cliente_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 0),
            ]))
            story.append(cliente_table)
            story.append(Spacer(1, 0.2*cm))

            # --- Dados da OS ---
            data_entrada_str = safe_get(os_data, 'data_entrada') or 'N/A'
            tipo_serv = safe_get(os_data, 'nome_tipo_servico') or 'N/A'
            end_serv = safe_get(os_data, 'endereco_servico') or 'Mesmo do cliente'
            garantia = safe_get(os_data, 'garantia') or 'N/A'
            status_str = safe_get(os_data, 'status') or 'N/A'
            dt_conclusao = safe_get(os_data, 'data_conclusao') or 'Pendente'

            valor_os_str = 'N/A' # Default
            valor_db = safe_get(os_data, 'valor') # Pega o valor usando helper
            if valor_db is not None:
                try:
                    valor_os_str = f"R$ {float(valor_db):,.2f}".replace(",", "v").replace(".", ",").replace("v", ".")
                except (ValueError, TypeError):
                    valor_os_str = 'Inválido'

            os_details_data = [
                [Paragraph("<b>Data Entrada:</b>", normal_style), Paragraph(data_entrada_str, normal_style)],
                [Paragraph("<b>Tipo Serviço:</b>", normal_style), Paragraph(tipo_serv, normal_style)],
                [Paragraph("<b>Endereço Serviço:</b>", normal_style), Paragraph(end_serv, normal_style)],
                [Paragraph("<b>Garantia:</b>", normal_style), Paragraph(garantia, normal_style)],
                [Paragraph("<b>Status:</b>", normal_style), Paragraph(status_str, normal_style)],
                [Paragraph("<b>Data Conclusão:</b>", normal_style), Paragraph(dt_conclusao, normal_style)],
                [Paragraph("<b>Valor:</b>", normal_style), Paragraph(valor_os_str, normal_style_right)],
            ]
            # (Código da tabela OS permanece o mesmo)
            os_table = Table(os_details_data, colWidths=[4*cm, None])
            os_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 0),
             ]))
            story.append(os_table)
            story.append(Spacer(1, 0.3*cm))

            # --- Descrição e Observações ---
            desc_prob = safe_get(os_data, 'descricao_problema') or 'Nenhuma descrição.'
            obs = safe_get(os_data, 'observacoes') or 'Nenhuma observação.'

            # (Código da Descrição/Obs permanece o mesmo)
            story.append(Paragraph("<b>Descrição do Problema/Serviço:</b>", normal_style))
            story.append(Paragraph(desc_prob, normal_style))
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph("<b>Observações:</b>", normal_style))
            story.append(Paragraph(obs, normal_style))
            story.append(Spacer(1, 0.3*cm))


            # --- Foto ---
            foto_path = safe_get(os_data, 'foto_path') # Usa helper
            # (Código da foto permanece o mesmo, usando foto_path obtido)
            if foto_path:
                base_filename = os.path.basename(foto_path)
                full_image_path = os.path.join(db.UPLOADS_DIR, base_filename)

                if os.path.exists(full_image_path):
                    try:
                        max_width = 15 * cm; max_height = 8 * cm
                        img = PILImage.open(full_image_path)
                        img.verify()
                        img = PILImage.open(full_image_path)
                        img_width, img_height = img.size

                        if img_width <= 0 or img_height <= 0: raise ValueError("Dimensões inválidas")

                        ratio = min(max_width / img_width, max_height / img_height, 1.0)
                        new_width = img_width * ratio
                        new_height = img_height * ratio

                        rl_image = Image(full_image_path, width=new_width, height=new_height)
                        rl_image.hAlign = 'CENTER'
                        story.append(Paragraph("<b>Foto Anexada:</b>", normal_style))
                        story.append(Spacer(1, 0.1*cm))
                        story.append(rl_image)
                        story.append(Spacer(1, 0.3*cm))
                    except Exception as e:
                        print(f"Erro ao processar imagem {full_image_path} para PDF: {e}")
                        story.append(Paragraph(f"<i>Erro ao carregar/processar imagem: {base_filename}</i>", normal_style))
                        story.append(Spacer(1, 0.3*cm))
                else:
                     story.append(Paragraph(f"<i>Arquivo da imagem não encontrado: {base_filename}</i>", normal_style))
                     story.append(Spacer(1, 0.3*cm))


            # (Separador e bloco except loop_err permanecem os mesmos)
            if i < len(ordens_servico) - 1:
                 story.append(Spacer(1, 0.3*cm))
                 story.append(Paragraph("------------------------------------------------------------------", normal_style))
                 story.append(Spacer(1, 0.3*cm))

        except Exception as loop_err:
            os_id_str = safe_get(os_data, 'id', '??') # Usa helper aqui também
            print(f"Erro CRÍTICO ao processar OS ID {os_id_str} para PDF: {loop_err}")
            print(traceback.format_exc())
            story.append(Paragraph(f"<font color='red'><b>Erro ao processar dados da OS ID {os_id_str}. Verifique os logs.</b></font>", normal_style))
            story.append(Spacer(1, 0.5*cm))
            if i < len(ordens_servico) - 1:
                 story.append(Paragraph("------------------------------------------------------------------", normal_style))
                 story.append(Spacer(1, 0.5*cm))
            continue # Pula para a próxima OS

    # (Bloco try/except final para build do doc permanece o mesmo)
    try:
        doc.build(story)
        print(f"Relatório PDF gerado com sucesso: {filepath}")
        return filepath
    except Exception as e:
        print(f"Erro final ao construir o documento PDF: {e}")
        print(traceback.format_exc())
        return None

# --- FIM DA FUNÇÃO CORRIGIDA ---

# O bloco if __name__ == "__main__": permanece o mesmo
if __name__ == "__main__":
    print("Testando geração de PDF...")
    test_oss = db.get_ordens_servico_filtradas()
    if test_oss:
        print(f"Encontradas {len(test_oss)} OS para teste.")
        generate_os_pdf_report(test_oss, "relatorio_teste.pdf")
    else:
        print("Nenhuma OS no banco encontrada com get_ordens_servico_filtradas para gerar relatório de teste.")