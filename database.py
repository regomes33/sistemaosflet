# database.py

import sqlite3
import os
from datetime import datetime
import traceback # Importar para debugging detalhado

DATABASE_NAME = 'os_database.db'
UPLOADS_DIR = 'uploads'
REPORTS_DIR = 'reports'

# Garante que os diretórios existam
os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

def get_db_connection():
    """Cria e retorna uma conexão com o banco de dados."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Retorna dicionários em vez de tuplas
    conn.execute("PRAGMA foreign_keys = ON") # Habilita chaves estrangeiras
    return conn

def setup_database():
    """Cria as tabelas do banco de dados se não existirem."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Tabela Clientes
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            cpf_cnpj TEXT UNIQUE,
            telefone TEXT,
            email TEXT,
            endereco TEXT,
            numero TEXT,
            complemento TEXT,
            bairro TEXT,
            cidade TEXT,
            estado TEXT,
            cep TEXT
        )
    ''')

    # Tabela Tipos de Serviço
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipos_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            descricao TEXT
        )
    ''')

    # Tabela Ordens de Serviço
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ordens_servico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero_os TEXT NOT NULL UNIQUE,
            cliente_id INTEGER NOT NULL,
            tipo_servico_id INTEGER,
            data_entrada TEXT NOT NULL, -- Formato recomendado: 'YYYY-MM-DD HH:MM:SS'
            descricao_problema TEXT,
            endereco_servico TEXT, -- Endereço específico do serviço, se diferente do cliente
            garantia TEXT, -- Ex: "30 dias", "90 dias", "Sem garantia"
            status TEXT DEFAULT 'Aberta', -- Ex: Aberta, Em Andamento, Concluída, Cancelada
            foto_path TEXT, -- Caminho relativo para a foto em 'uploads/'
            data_conclusao TEXT, -- Formato recomendado: 'YYYY-MM-DD' ou 'YYYY-MM-DD HH:MM:SS'
            valor REAL,
            observacoes TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE,
            FOREIGN KEY (tipo_servico_id) REFERENCES tipos_servico(id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()
    print("Banco de dados configurado.")

# --- Funções CRUD para Clientes ---
# (As funções add_cliente, get_all_clientes, get_cliente_by_id, update_cliente, delete_cliente permanecem iguais)
def add_cliente(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO clientes (nome, cpf_cnpj, telefone, email, endereco, numero, complemento, bairro, cidade, estado, cep)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['nome'], data.get('cpf_cnpj'), data.get('telefone'), data.get('email'), data.get('endereco'), data.get('numero'), data.get('complemento'), data.get('bairro'), data.get('cidade'), data.get('estado'), data.get('cep')))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao adicionar cliente: {e}")
        return None # Ou levante uma exceção personalizada
    finally:
        conn.close()

def get_all_clientes():
    conn = get_db_connection()
    clientes = conn.execute('SELECT * FROM clientes ORDER BY nome').fetchall()
    conn.close()
    return clientes

def get_cliente_by_id(cliente_id):
    conn = get_db_connection()
    cliente = conn.execute('SELECT * FROM clientes WHERE id = ?', (cliente_id,)).fetchone()
    conn.close()
    return cliente

def update_cliente(cliente_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE clientes
            SET nome=?, cpf_cnpj=?, telefone=?, email=?, endereco=?, numero=?, complemento=?, bairro=?, cidade=?, estado=?, cep=?
            WHERE id=?
        ''', (data['nome'], data.get('cpf_cnpj'), data.get('telefone'), data.get('email'), data.get('endereco'), data.get('numero'), data.get('complemento'), data.get('bairro'), data.get('cidade'), data.get('estado'), data.get('cep'), cliente_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao atualizar cliente: {e}")
        return False
    finally:
        conn.close()

def delete_cliente(cliente_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM clientes WHERE id = ?', (cliente_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar cliente: {e}")
        conn.rollback() # Desfaz a transação em caso de erro
        return False
    finally:
        conn.close()

# --- Funções CRUD para Tipos de Serviço ---
# (As funções add_tipo_servico, get_all_tipos_servico, get_tipo_servico_by_id, update_tipo_servico, delete_tipo_servico permanecem iguais)
def add_tipo_servico(nome, descricao=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO tipos_servico (nome, descricao) VALUES (?, ?)', (nome, descricao))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        print(f"Erro: Tipo de serviço '{nome}' já existe.")
        return None
    finally:
        conn.close()

def get_all_tipos_servico():
    conn = get_db_connection()
    tipos = conn.execute('SELECT * FROM tipos_servico ORDER BY nome').fetchall()
    conn.close()
    return tipos

def get_tipo_servico_by_id(tipo_id):
    conn = get_db_connection()
    tipo = conn.execute('SELECT * FROM tipos_servico WHERE id = ?', (tipo_id,)).fetchone()
    conn.close()
    return tipo

def update_tipo_servico(tipo_id, nome, descricao=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('UPDATE tipos_servico SET nome = ?, descricao = ? WHERE id = ?', (nome, descricao, tipo_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        print(f"Erro: Nome de tipo de serviço '{nome}' já está em uso.")
        return False
    finally:
        conn.close()

def delete_tipo_servico(tipo_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM tipos_servico WHERE id = ?', (tipo_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar tipo de serviço: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

# --- Funções CRUD para Ordens de Serviço ---
# (As funções get_next_os_number, add_ordem_servico, get_all_ordens_servico, get_ordem_servico_by_id, update_ordem_servico, delete_ordem_servico permanecem iguais)
def get_next_os_number():
    """Busca o maior número de OS numérico e retorna o próximo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(CAST(numero_os AS INTEGER)) FROM ordens_servico WHERE numero_os GLOB '[0-9]*'")
        max_num_result = cursor.fetchone()

        if max_num_result and max_num_result[0] is not None:
            next_num = int(max_num_result[0]) + 1
        else:
            next_num = 1
        return str(next_num)

    except (sqlite3.Error, ValueError) as e:
        print(f"Erro ao obter próximo número da OS: {e}")
        return f"ERR-{datetime.now().timestamp()}"
    finally:
        conn.close()

def add_ordem_servico(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO ordens_servico (numero_os, cliente_id, tipo_servico_id, data_entrada,
                                        descricao_problema, endereco_servico, garantia, status, foto_path,
                                        data_conclusao, valor, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['numero_os'], data['cliente_id'], data.get('tipo_servico_id'), data.get('data_entrada', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
            data.get('descricao_problema'), data.get('endereco_servico'), data.get('garantia'), data.get('status', 'Aberta'),
            data.get('foto_path'), data.get('data_conclusao'), data.get('valor'), data.get('observacoes')
        ))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao adicionar OS: {e}")
        return None
    except sqlite3.Error as e:
        print(f"Erro geral ao adicionar OS: {e}")
        return None
    finally:
        conn.close()

def get_all_ordens_servico():
    conn = get_db_connection()
    oss = conn.execute('''
        SELECT os.*, c.nome as nome_cliente, ts.nome as nome_tipo_servico
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN tipos_servico ts ON os.tipo_servico_id = ts.id
        ORDER BY os.data_entrada DESC
    ''').fetchall()
    conn.close()
    return oss

def get_ordem_servico_by_id(os_id):
    conn = get_db_connection()
    os_data = conn.execute('''
        SELECT os.*, c.nome as nome_cliente, ts.nome as nome_tipo_servico
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN tipos_servico ts ON os.tipo_servico_id = ts.id
        WHERE os.id = ?
    ''', (os_id,)).fetchone()
    conn.close()
    return os_data

def update_ordem_servico(os_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE ordens_servico
            SET numero_os=?, cliente_id=?, tipo_servico_id=?, data_entrada=?, descricao_problema=?,
                endereco_servico=?, garantia=?, status=?, foto_path=?, data_conclusao=?, valor=?, observacoes=?
            WHERE id=?
        ''', (
            data['numero_os'], data['cliente_id'], data.get('tipo_servico_id'), data['data_entrada'],
            data.get('descricao_problema'), data.get('endereco_servico'), data.get('garantia'), data.get('status'),
            data.get('foto_path'), data.get('data_conclusao'), data.get('valor'), data.get('observacoes'), os_id
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade ao atualizar OS: {e}")
        return False
    except sqlite3.Error as e:
        print(f"Erro geral ao atualizar OS: {e}")
        return False
    finally:
        conn.close()


def delete_ordem_servico(os_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        os_data = get_ordem_servico_by_id(os_id)
        foto_path = os_data['foto_path'] if os_data else None

        cursor.execute('DELETE FROM ordens_servico WHERE id = ?', (os_id,))
        conn.commit()

        if foto_path:
            full_foto_path = os.path.join(UPLOADS_DIR, os.path.basename(foto_path))
            if os.path.exists(full_foto_path):
                try:
                    os.remove(full_foto_path)
                    print(f"Arquivo de foto {full_foto_path} removido.")
                except OSError as e:
                    print(f"Erro ao remover arquivo de foto {full_foto_path}: {e}")

        return True
    except sqlite3.Error as e:
        print(f"Erro ao deletar OS: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()


# --- Funções para Relatórios ---

# ==============================================================
# FUNÇÃO CORRIGIDA get_ordens_servico_filtradas
# ==============================================================
def get_ordens_servico_filtradas(cliente_id=None, status=None, data_inicio=None, data_fim=None):
    """
    Busca ordens de serviço no banco de dados com filtros opcionais.

    Args:
        cliente_id (int | str, optional): ID do cliente para filtrar. Pode vir como string do frontend. Defaults to None.
        status (str, optional): Status da OS para filtrar. Defaults to None.
        data_inicio (str, optional): Data de início ('YYYY-MM-DD') para filtrar pela data_entrada. Defaults to None.
        data_fim (str, optional): Data de fim ('YYYY-MM-DD') para filtrar pela data_entrada. Defaults to None.

    Returns:
        list: Uma lista de objetos sqlite3.Row representando as OS filtradas,
              incluindo dados do cliente e tipo de serviço. Retorna lista vazia se nada for encontrado ou em caso de erro.
    """
    conn = None # Inicializa a conexão como None fora do try
    oss = []    # Inicializa a lista de resultados como vazia
    try:
        conn = get_db_connection()
        # Query base com JOINs para buscar dados relacionados (cliente, tipo de serviço)
        query = '''
            SELECT os.*,
                   c.nome as nome_cliente,
                   c.endereco as endereco_cliente,
                   c.numero as numero_cliente,       -- Adicionado campo numero do cliente
                   c.complemento as complemento_cliente, -- Adicionado campo complemento do cliente
                   c.bairro as bairro_cliente,       -- Adicionado campo bairro do cliente
                   c.cidade as cidade_cliente,
                   c.estado as estado_cliente,
                   c.cep as cep_cliente,
                   c.telefone as telefone_cliente,
                   c.email as email_cliente,
                   ts.nome as nome_tipo_servico
            FROM ordens_servico os
            LEFT JOIN clientes c ON os.cliente_id = c.id
            LEFT JOIN tipos_servico ts ON os.tipo_servico_id = ts.id
            WHERE 1=1 -- Condição inicial verdadeira para facilitar a adição de filtros com AND
        '''
        params = [] # Lista para armazenar os parâmetros da query de forma segura

        # --- Adiciona os filtros à query dinamicamente ---

        # Filtro por Cliente
        if cliente_id:
            try:
                # Tenta converter para int, pois o ID é inteiro no banco
                cliente_id_int = int(cliente_id)
                query += ' AND os.cliente_id = ?' # Adiciona a condição à query
                params.append(cliente_id_int)     # Adiciona o valor à lista de parâmetros
                print(f"DEBUG (BD): Aplicando filtro cliente_id = {cliente_id_int}")
            except (ValueError, TypeError):
                # Se a conversão falhar (ex: veio string vazia ou texto), ignora o filtro
                print(f"AVISO (BD): Filtro de cliente_id inválido ou não numérico ignorado: '{cliente_id}'")

        # Filtro por Status
        if status: # Se um status foi fornecido (não é None nem string vazia)
            query += ' AND os.status = ?' # Adiciona a condição à query
            params.append(status)         # Adiciona o valor à lista de parâmetros
            print(f"DEBUG (BD): Aplicando filtro status = '{status}'")

        # Filtro por Data de Início
        # Assume que data_inicio está no formato 'YYYY-MM-DD'
        if data_inicio:
            # Usa DATE() do SQLite para comparar apenas a parte da data da coluna data_entrada
            query += ' AND DATE(os.data_entrada) >= ?'
            params.append(data_inicio)
            print(f"DEBUG (BD): Aplicando filtro data_inicio >= '{data_inicio}'")

        # Filtro por Data de Fim
        # Assume que data_fim está no formato 'YYYY-MM-DD'
        if data_fim:
            # Usa DATE() do SQLite para comparar apenas a parte da data
            query += ' AND DATE(os.data_entrada) <= ?'
            params.append(data_fim)
            print(f"DEBUG (BD): Aplicando filtro data_fim <= '{data_fim}'")

        # --- Fim da adição de filtros ---

        query += ' ORDER BY os.data_entrada DESC' # Ordena os resultados pela data de entrada, mais recentes primeiro

        cursor = conn.cursor()
        print(f"--- DEBUG (BD): Executando Query ---")
        print(f"Query Final Montada: {query}")
        print(f"Parâmetros Finais: {params}")

        cursor.execute(query, tuple(params)) # Executa a query passando os parâmetros como tupla
        oss = cursor.fetchall() # Obtém todos os resultados

        print(f"\n--- DEBUG (BD): Dados Retornados ({len(oss)} linhas) ---")
        if oss:
            # Mostra um exemplo da primeira linha retornada (convertida para dict para facilitar leitura)
            print(f"Exemplo Linha 0: {dict(oss[0])}")
        else:
            print("Nenhuma ordem de serviço encontrada com os filtros aplicados.")
        print("--- FIM DEBUG (BD) ---\n")

    except sqlite3.Error as e:
        # Erro específico do SQLite
        print(f"Erro no Banco de Dados ao buscar OS filtradas: {e}")
        print(f"Query que falhou: {query}")
        print(f"Parâmetros usados: {params}")
        oss = [] # Garante que retorne uma lista vazia em caso de erro de BD
    except Exception as ex:
        # Captura qualquer outro erro inesperado
        print(f"Erro inesperado ao buscar OS filtradas: {ex}")
        traceback.print_exc() # Imprime o rastreamento completo do erro
        oss = [] # Garante que retorne uma lista vazia
    finally:
        # Garante que a conexão seja fechada, mesmo se ocorrer erro
        if conn:
            conn.close()
            # print("DEBUG (BD): Conexão com o banco de dados fechada.") # Opcional

    return oss # Retorna a lista de resultados (objetos sqlite3.Row) ou uma lista vazia
# ==============================================================
# FIM DA FUNÇÃO CORRIGIDA
# ==============================================================


# --- Inicialização ---
if __name__ == "__main__":
    # Executar apenas se este script for chamado diretamente (para testes)
    setup_database()
    print("Funções do banco de dados prontas.")
    # Exemplo de uso para testar a função de filtro:
    # print("\n--- Teste Filtro ---")
    # teste_filtro = get_ordens_servico_filtradas(cliente_id=1, status='Concluída') # Substitua por IDs e status válidos
    # if teste_filtro:
    #     for ordem in teste_filtro:
    #         print(dict(ordem))
    # else:
    #     print("Nenhuma OS encontrada no teste de filtro.")
    # print("--- Fim Teste Filtro ---")