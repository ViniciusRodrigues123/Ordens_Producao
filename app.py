#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
# app.py - SISTEMAS DE ORDENS DE PROGUÇÃO - C.R.U.D COMPLETO               
# SENAI JARAGUÁ DO SUL - TÉCNICO EM CIBERSISTEMAS PARA AUTOMAÇÃO - 2026/1  
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

#------------------------------------------
#--- BACK-END FLASK: ROTAS DA API REST ---
#------------------------------------------

#---------------------------IMPORTES--------------------------------
from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_bd, get_connection
import datetime
# -------------------------------------------------------------------

# Cria uma instância da aplicação Flash
app = Flask(__name__, static_folder = 'static', static_url_path='')

# Habilitar os CORS
CORS(app)

# ===============================
# ROTA Nº1 - PÁGINA INICIAL
# ===============================

@app.route('/')
def index():
    # Alimentar o arquivo INDEX.HTML da pasta STATIC
    return app.send_static_file('index.html')

# ===============================
# ROTA Nº2 - STATUS API
# ===============================

@app.route('/status')
def status():
    # Rota de verificação da API(saúde)
    # Retora um JSON informando que o servidor está ativo
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM ordens')
    resultado = cursor.fetchone()
    conn.close()
    return jsonify({
        "status": "online",
        "sistema": "Sistema de ordem de Producao",
        "versao": "2.0.0",
        "total_ordens": resultado["total"],
        "times_tamp": datetime.datetime.now().strftime("%Y-%m-%d%H:%M:%S"),
        "mensagem": "Ola, Fabrica, API FUNCIONANDO!"
    })

# ===============================
# ROTA Nº3 - LISTAR TODAS AS ORDENS(GET)
# ===============================

@app.route('/ordens', methods=['GET'])
def listar_ordens():
    '''
    | Listar todas as ordens de produção cadastradas.
    | Métodos HTTP: GET
    | URL: http://localhost:5000/ordens
    | Retorna: Lista e ordens em formato JSON.
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens ORDER BY id DESC')
    ordens = cursor.fetchall()
    conn.close()
    
    # Converte cada Row do SQLite em um dicionário Python para serializar um JSON
    return jsonify([dict(o) for o in ordens])

# ===============================
# ROTA POR ID - BUSCAR UMA ORDEM ESPECÍFICA PELO ID (GET) 
# ===============================

@app.route('/ordens/<int:ordem_id>', methods=['GET'])

def buscar_ordem(ordem_id):
    """
    |Buscar uma única ordem de produção pelo ID.
    |Parametros de URL:
        - Ordem id(int): ID da ordem a ser buscada
    
    |Retornar:
        200 + JSON da ordem, se for encontrada.
        404 + mensagem de erro, se não existir.
    """
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # O'?' é substituido pelo valor de ordem_id de forma segura
    cursor.execute('SELECT * FROM ordens WHERE id = ?', (ordem_id,))
    ordem = cursor.fetchone()  #ele retorna um unico registro ou None
    conn.close()
    
    
    if ordem is None:
        return jsonify({'erro': f'Ordem {ordem_id} nao encontrada'}), 404
    return jsonify(dict(ordem)), 200

# ===============================
# ROTA: Criar nova ordem de produção (POST) 
# ===============================

@app.route('/ordens', methods=['POST'])
def criar_ordem():
    """
    |Cria uma nova ordem de produção a partir dos dados JSON enviados.
    
    |Body esperado(JSON):
    
        produto     (str): Nome do produto      - Obrigatório
        quantidade  (int): Quantidade de peças  - Obrigatório, > 0
        status      (str): Opcional             - Padrão: 'Pendente'
        
    |Retorno:
        201 : JSON da ordem criada, em caso de sucesso.
        400 : mensagem de erro, se dados inválidos
    """
    
    dados = request.get_json()
    
    if not dados:
        return jsonify({'erro': 'Body da requisicao ausente ou invalido'}), 400
    
    # Verificação de campo obrigatório (produto)
    produto = dados.get('produto', '').strip()
    if not produto:
        return jsonify({'erro': 'Campo "Produto" e obrigatorio e nao pode ser vazio'}), 400
    
    # Verificação de campo obrigatório (produto)
    quantidade = dados.get('quantidade')
    if quantidade is None:
        return jsonify({'erro': 'Campo "Quantidade" e obrigatorio.'}), 400
    
    # Verifica se a quantidade é um número inteiro e positivo
    try:
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError()
    except (ValueError, TypeError):
        return jsonify({'erro': 'Campo "Quantidade" deve ser um numero inteiro positivo'}), 400
    
    # Status (pendente, em andamento, concluído) - Opcional
    status_validos = ['Pendente', 'Em andamento', 'Concluida'] # Criar lista/Vetor
    status = dados.get('status', 'Pendente')
    if status not in status_validos:
        return jsonify({'erro': f'Status invalido. Use {status_validos}'}), 400
    
    # Inserção dos dados no banco - toda vez que for fazer algo relacionado a banco, utiliza-se:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute( # SQL
        'INSERT INTO ordens (produto, quantidade, status ) VALUES (?, ?, ?)',
        (produto, quantidade, status)
    )
    conn.commit()
    
    # Recuperando ID que é gerado automaticamente pelo banco
    novo_id = cursor.lastrowid
    conn.close() # Sempre utilizar o 'conn.close()'
    
    # Buscar o registro que foi recem-criado
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute( # SQL
        'SELECT * FROM ordens WHERE id = ? ', (novo_id,))
    nova_ordem = cursor.fetchone() # 'fetchone' - Serve para limpar a string
    conn.close()
    
    # 201 - Retornar "created" com registro completo
    return jsonify(dict(nova_ordem)), 201

# ===============================
# ROTA: Atualizar a ordem completa (PUT)
# ===============================

@app.route('/ordens/<int:ordem_id>', methods=['PUT'])
def atualizar_ordem(ordem_id):
    ''' Atualiza produto, quantidade e status de uma ordem. '''
    dados = request.get_json()
    
    if not dados: 
        return jsonify({'erro': 'Body da requisicao ausente ou invalido.'}), 400
    
    # Pegando todos os dados do pacote
    novo_produto = dados.get('produto', '').strip()
    nova_quantidade = dados.get('quantidade')
    novo_status = dados.get('status', '').strip()

    # Validações para garantir que nada venha vazio
    if not novo_produto or not nova_quantidade or not novo_status:
        return jsonify({'erro': 'Todos os campos (produto, quantidade, status) sao obrigatorios.'}), 400

    status_validos = ['Pendente', 'Em andamento', 'Concluida']
    if novo_status not in status_validos:
        return jsonify({'erro': f'Status invalido. Use: {status_validos}'}), 400

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM ordens WHERE id = ?', (ordem_id,))
    if cursor.fetchone() is None:
        conn.close()
        return jsonify({'erro' : f'Ordem {ordem_id} nao encontrada.'}), 404

    # Atualizando a linha toda no Banco de Dados
    cursor.execute('''
        UPDATE ordens 
        SET produto = ?, quantidade = ?, status = ? 
        WHERE id = ?
    ''', (novo_produto, nova_quantidade, novo_status, ordem_id))
    
    conn.commit()
    conn.close()

    return jsonify({'mensagem': 'Ordem atualizada com sucesso!'}), 200

# ===============================
# ROTA - Remover uma ordem (DELETE)
# ===============================

@app.route('/ordens/<int:ordem_id>', methods=['DELETE'])
def remover_ordem(ordem_id):
    """
    Remover permanentemente uma ordem de producao pelo ID.
    
    Parametros de URL:
        ordem_id (int) : ID da ordem a ser removida
        
    Retorna:
        200 - confirmacao (mensagem)
        400 - erro (mensagem) se a ordem nao for encontrada
    """
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verificação de existencia antes de DELETAR o registro
    cursor.execute('SELECT id, produto FROM ordens WHERE id = ?', (ordem_id,))
    ordem = cursor.fetchone()
    
    if ordem is None:
        conn.close()
        return jsonify({'erro': f'Ordem de numero {ordem_id} nao encontrada.'}), 404
    
    # Variavel que guarda o nome do produto apagado para ser usado posteriormente na mensagem de confirmação
    nome_produto_apagado = ordem['produto']
    
    # Execução de fato da operação
    cursor.execute('DELETE FROM ordens WHERE id = ?', (ordem_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'mensagem': f'Ordem de numero {ordem_id} ({nome_produto_apagado}) removida com sucesso!', 'id_removido': ordem_id}), 200

    

# --- PONTO DE PARTIDA ---

if __name__=='__main__':
    init_bd()
    app.run(debug=True, host='0.0.0.0', port=5000)