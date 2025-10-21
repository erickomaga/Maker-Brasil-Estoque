import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('estoque.db')
    conn.row_factory = sqlite3.Row
    return conn

def get_estoque_nivel(estoque):
    if estoque <= 0: return 0  # Vazio 
    if estoque <= 50: return 1  # Preocupante
    if estoque <= 100: return 2 # Alerta
    return 3 # Tranquilo 

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            categoria TEXT NOT NULL,
            em_estoque INTEGER NOT NULL,
            necessario INTEGER NOT NULL,
            UNIQUE(nome, categoria)
        )
    ''')

    cursor.execute("SELECT COUNT(id) FROM produtos")
    count = cursor.fetchone()[0]

    if count == 0:
        produtos_iniciais = [
            ('Tapete Lúdico', 'infantil', 120, 10), # Tranquilo
            ('Encartes', 'infantil', 35, 10),      # Preocupante
            ('Lego 9656', 'infantil', 0, 10),       # Vazio
            ('Caracol', 'infantil', 80, 10),       # Alerta
            ('Cards', 'infantil', 10, 10),         # Preocupante

            # Fundamental 1: 1º e 2º Ano
            ('Lego 9686', 'fundamental1-2', 150, 10),
            ('Caracol', 'fundamental1-2', 60, 10),
            ('Cards', 'fundamental1-2', 0, 10),
            ('Tipos de Maker', 'fundamental1-2', 20, 10),

            # Fundamental 1: 3º ao 5º Ano
            ('Lego WeDo', 'fundamental3-5', 180, 10),
            ('Lego We98', 'fundamental3-5', 10, 10),
            ('Educação Financeira Maker', 'fundamental3-5', 0, 10),
            ('Caneta 3D', 'fundamental3-5', 90, 10),
            ('Filamento', 'fundamental3-5', 105, 10),
            ('Tapete', 'fundamental3-5', 45, 10),
            ('Caracol', 'fundamental3-5', 70, 10),
            ('Cards', 'fundamental3-5', 25, 10)
        ]
        
        cursor.executemany(
            'INSERT INTO produtos (nome, categoria, em_estoque, necessario) VALUES (?, ?, ?, ?)',
            produtos_iniciais
        )
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/produtos')
def get_produtos():
    conn = get_db_connection()
    sort_by = request.args.get('sort_by')
    
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()

    produtos_dict = [dict(row) for row in produtos]

    if sort_by == 'prioridade':
        for p in produtos_dict:
            p['nivel_estoque'] = get_estoque_nivel(p['em_estoque'])
        
        produtos_dict.sort(key=lambda p: (p['nivel_estoque'], p['nome']))

    else:
        produtos_dict.sort(key=lambda p: (p['categoria'], p['nome']))


    return jsonify(produtos_dict)

@app.route('/api/atualizar', methods=['POST'])
def atualizar_produtos_em_massa():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    for p in dados:
        cursor.execute(
            'UPDATE produtos SET em_estoque = ? WHERE id = ?', 
            (p['emEstoque'], p['id'])
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': '✅ Alterações salvas com sucesso!'})

@app.route('/api/atualizar/individual', methods=['POST'])
def atualizar_produto_individual():
    dados = request.get_json()
    produto_id = dados.get('id')
    em_estoque = dados.get('emEstoque')
    
    if not produto_id or em_estoque is None:
        return jsonify({'mensagem': 'Dados incompletos'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE produtos SET em_estoque = ? WHERE id = ?',
        (em_estoque, produto_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': f'✅ Estoque atualizado para {em_estoque}!'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)