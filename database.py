import sqlite3
import os
from datetime import datetime

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
            data_entrada TEXT NOT NULL,
            descricao_problema TEXT,
            endereco_servico TEXT, -- Endereço específico do serviço, se diferente do cliente
            garantia TEXT, -- Ex: "30 dias", "90 dias", "Sem garantia"
            status TEXT DEFAULT 'Aberta', -- Ex: Aberta, Em Andamento, Concluída, Cancelada
            foto_path TEXT, -- Caminho relativo para a foto em 'uploads/'
            data_conclusao TEXT,
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
        # Opcional: Verificar se o tipo está em uso antes de deletar
        # count = conn.execute('SELECT COUNT(*) FROM ordens_servico WHERE tipo_servico_id = ?', (tipo_id,)).fetchone()[0]
        # if count > 0:
        #     print(f"Erro: Tipo de serviço está associado a {count} OS.")
        #     return False
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

def get_next_os_number():
    """Busca o maior número de OS numérico e retorna o próximo."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Tenta encontrar o maior valor numérico na coluna numero_os
        cursor.execute("SELECT MAX(CAST(numero_os AS INTEGER)) FROM ordens_servico WHERE numero_os GLOB '[0-9]*'")
        max_num_result = cursor.fetchone()

        if max_num_result and max_num_result[0] is not None:
            next_num = int(max_num_result[0]) + 1
        else:
            # Se não houver OS ou nenhuma começar com número, inicia em 1
            next_num = 1

        # Formata como string (opcional: adicionar zeros à esquerda, etc.)
        # Ex: return f"{next_num:06d}" # para ter 000001
        return str(next_num)

    except (sqlite3.Error, ValueError) as e:
        print(f"Erro ao obter próximo número da OS: {e}")
        # Fallback: retorna um timestamp ou UUID como string única em caso de erro grave
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
        print(f"Erro de integridade ao adicionar OS: {e}") # Pode ser numero_os duplicado ou cliente_id inválido
        return None
    except sqlite3.Error as e:
        print(f"Erro geral ao adicionar OS: {e}")
        return None
    finally:
        conn.close()

def get_all_ordens_servico():
    conn = get_db_connection()
    # Junta com clientes e tipos_servico para obter nomes
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
        # Se a foto antiga não for a mesma da nova e existir, deletar a antiga?
        # Implementar lógica para deletar foto antiga se `data['foto_path']` mudou e a original existia.
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
        # Opcional: Obter path da foto para deletar o arquivo
        os_data = get_ordem_servico_by_id(os_id)
        foto_path = os_data['foto_path'] if os_data else None

        cursor.execute('DELETE FROM ordens_servico WHERE id = ?', (os_id,))
        conn.commit()

        # Deletar arquivo da foto se existir
        if foto_path:
            full_foto_path = os.path.join(UPLOADS_DIR, os.path.basename(foto_path)) # Segurança extra com basename
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
def get_ordens_servico_filtradas(cliente_id=None, status=None, data_inicio=None, data_fim=None):
    conn = get_db_connection()
    # A query JÁ FAZ O JOIN e seleciona os campos do cliente!
    query = '''
        SELECT os.*,
               c.nome as nome_cliente,
               c.endereco as endereco_cliente,
               c.cidade as cidade_cliente,
               c.estado as estado_cliente,
               c.cep as cep_cliente,
               c.telefone as telefone_cliente,
               c.email as email_cliente,
               ts.nome as nome_tipo_servico
        FROM ordens_servico os
        LEFT JOIN clientes c ON os.cliente_id = c.id
        LEFT JOIN tipos_servico ts ON os.tipo_servico_id = ts.id
        WHERE 1=1
    '''
    params = []

    # ... (lógica de filtros) ...

    query += ' ORDER BY os.data_entrada DESC'

    # --- MODIFICAÇÃO: Adicionar try/except e debug prints ---
    oss = [] # Inicializa como lista vazia
    try:
        cursor = conn.cursor()
        print(f"--- DEBUG (database.py): Executando Query ---")
        print(f"Query: {query}")
        print(f"Params: {params}")
        cursor.execute(query, params)
        oss = cursor.fetchall() # Pega todos os resultados como sqlite3.Row

        print(f"\n--- DEBUG (database.py): Dados Retornados ({len(oss)} linhas) ---")
        if oss:
            # Imprime a primeira linha (se existir) para exemplo
            print(f"Exemplo Linha 0: {dict(oss[0])}") # Converte sqlite3.Row para dict para melhor visualização
            # Você pode iterar e imprimir todas se precisar:
            # for i, row in enumerate(oss):
            #     print(f"Linha {i}: {dict(row)}")
        else:
            print("Nenhuma linha retornada pela query.")
        print("--- FIM DEBUG (database.py) ---\n")

    except sqlite3.Error as e:
        print(f"Erro no Banco de Dados em get_ordens_servico_filtradas: {e}")
        print(f"Query que falhou: {query}")
        print(f"Parâmetros: {params}")
        # Retorna lista vazia em caso de erro
    finally:
        if conn:
            conn.close()

    return oss # Retorna a lista de resultados (sqlite3.Row objects) ou lista vazia
# --- Fim da modificação ---

# --- Inicialização ---
if __name__ == "__main__":
    # Executar apenas se este script for chamado diretamente (para testes)
    setup_database()
    print("Funções do banco de dados prontas.")
    # Exemplo de uso:
    # add_cliente({'nome': 'Cliente Teste', 'email': 'teste@teste.com'})
    # print(get_all_clientes())