#===================================
# BACK-END FLASK: ROTAS DA API REST
#===================================

from flask import Flask, jsonify, request
from flask_cors import CORS
from database import init_bd, get_connection

# Cria uma instância da aplicação Flash
app = Flask(__name__, static_folder='static', static_url_path='')

# Habilitar os CORS
CORS(app)

# Rota N1 - Página Inicial
@app.route('/')
def index():
    # ALIMENTAR O ARQUIVO INDEX.HTML DA PASTA STATIC
    return app.send_static_file('index.html')

# Rota N2 - Status API
@app.route('/status')
def status():
    '''
    ROTA DE VERIFICAÇÃO DA API(SAÚDE)
    RETORNAR UM JSON INFORMANDO QUE O SERVIDOR ESTA ATIVO
    '''
    return jsonify({
        "status": "online",
        "sistema": "Sistema de ordem de Produção",
        "versao": "1.0.0",
        "mensagem": "Ola, Fabrica, API FUNCIONANDO!"
    })

# Rota N3 - Listar todas as Ordens(GET)
@app.route('/ordens', methods=['GET'])
def listar_ordens():
    '''
    LISTAR TODAS AS ORDENS DE PRODUÇÃO CADASTRADAS.
    MÉTODOS http: GET
    URL: http://localhost:5000/ordens
    Retorna: Lista e ordens em formato JSON. 
    '''
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM ordens ORDER BY id DESC')
    ordens = cursor.fetchall()
    conn.close()

    # Converte cada Row do SQLite em dicionario Python para serializar em JSON
    return jsonify([dict(o) for o in ordens])

# PONTO DE PARTIDA

if __name__=='__main__':
    init_bd()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
        
# Rota oir ID - Buscar uma ordem específica pelo ID(GET)

@app.route('/ordens/<int:ordem_id>, methods=['GET']')

def buscar_ordem(ordem_id):
    '''
    Buscar uma única ordem de produção pelo ID.
    Parametros de URL:
        - ordem id(int): ID da ordem a ser buscada.
        
    Retornar:
        200 + JSON da ordem, se for encontrada
        404 + mensagem de erro, se não existir
    '''
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM ordens WHERE ID = ')
    ordem = cursor.fetchone() # ele retorna um único registro ou None
    conn.close()

