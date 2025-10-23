import os
import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'estoque.db'))
    conn.row_factory = sqlite3.Row
    return conn

def get_estoque_nivel(estoque):
    if estoque <= 0:
        return 0
    if estoque <= 50:
        return 1
    if estoque <= 100:
        return 2
    return 3

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
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            'INSERT INTO produtos (nome, categoria, em_estoque, necessario) VALUES (?, ?, ?, ?)',
            [
                ('Tapete Lúdico', 'infantil', 120, 10),
                ('Encartes', 'infantil', 35, 10),
                ('Lego 9656', 'infantil', 0, 10),
                ('Caracol', 'infantil', 80, 10),
                ('Cards', 'infantil', 10, 10),
                ('Maker 1', 'infantil', 0, 10),
                ('Maker 2', 'infantil', 0, 10),
                ('Maker 3', 'infantil', 0, 10),
                ('box 1', 'infantil', 0, 10),
                ('box 2', 'infantil', 0, 10),
                ('box 3', 'infantil', 0, 10),

                ('Lego 9686', 'fundamental1-2', 150, 10),
                ('Caracol', 'fundamental1-2', 60, 10),
                ('Cards', 'fundamental1-2', 0, 10),
                ('Tipos de Maker', 'fundamental1-2', 20, 10),
                ('Maker 1', 'fundamental1-2', 0, 10),
                ('Maker 2', 'fundamental1-2', 0, 10),
                ('apostila 1 ano', 'fundamental1-2', 0, 10),
                ('apostila 2 ano', 'fundamental1-2', 0, 10),
                ('box 1 ano', 'fundamental1-2', 0, 10),
                ('box 2 ano', 'fundamental1-2', 0, 10),

                ('Lego WeDo', 'fundamental3-5', 180, 10),
                ('Lego We98', 'fundamental3-5', 10, 10),
                ('Educação Financeira Maker', 'fundamental3-5', 0, 10),
                ('Caneta 3D', 'fundamental3-5', 90, 10),
                ('Filamento', 'fundamental3-5', 105, 10),
                ('Tapete', 'fundamental3-5', 45, 10),
                ('Caracol', 'fundamental3-5', 70, 10),
                ('Cards', 'fundamental3-5', 25, 10),
                ('apostila 3 ano', 'fundamental3-5', 0, 10),
                ('apostila 4 ano', 'fundamental3-5', 0, 10),
                ('apostila 5 ano', 'fundamental3-5', 0, 10),
                ('Maker 3 ano', 'fundamental3-5', 0, 10),
                ('Maker 4 ano', 'fundamental3-5', 0, 10),
                ('Maker 5 ano', 'fundamental3-5', 0, 10),

                ('lego ev3', 'fundamental2', 0, 10),
                ('apostila 6 ano', 'fundamental2', 0, 10),
                ('Maker 6 ano', 'fundamental2', 0, 10),
                ('apostila 7 ano', 'fundamental2', 0, 10),
                ('Maker 7 ano', 'fundamental2', 0, 10),
                ('apostila 8 ano', 'fundamental2', 0, 10),
                ('Maker 8 ano', 'fundamental2', 0, 10),
                ('apostila 9 ano', 'fundamental2', 0, 10),
                ('Maker 9 ano', 'fundamental2', 0, 10),

                ('arduíno 1 em', 'ensino_medio', 0, 10),
                ('arduíno 2 em', 'ensino_medio', 0, 10),
                ('arduíno 3 em', 'ensino_medio', 0, 10),
                ('apostila 1 em', 'ensino_medio', 0, 10),
                ('apostila 2 em', 'ensino_medio', 0, 10),
                ('apostila 3 em', 'ensino_medio', 0, 10)
            ]
        )
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/produtos')
def get_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos').fetchall()
    conn.close()

    produtos_dict = [dict(row) for row in produtos]
    if request.args.get('sort_by') == 'prioridade':
        for p in produtos_dict:
            p['nivel_estoque'] = get_estoque_nivel(p['em_estoque'])
        produtos_dict.sort(key=lambda p: (p['nivel_estoque'], p['nome']))
    else:
        produtos_dict.sort(key=lambda p: (p['categoria'], p['nome']))
    return jsonify(produtos_dict)

@app.route('/api/atualizar', methods=['POST'])
def atualizar_produtos_em_massa():
    conn = get_db_connection()
    cursor = conn.cursor()
    for p in request.get_json():
        cursor.execute('UPDATE produtos SET em_estoque = ? WHERE id = ?', (p['emEstoque'], p['id']))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': '✅ Alterações salvas com sucesso!'})

@app.route('/api/atualizar/individual', methods=['POST'])
def atualizar_produto_individual():
    dados = request.get_json()
    if not dados.get('id') or dados.get('emEstoque') is None:
        return jsonify({'mensagem': 'Dados incompletos'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE produtos SET em_estoque = ? WHERE id = ?', (dados['emEstoque'], dados['id']))
    conn.commit()
    conn.close()
    return jsonify({'mensagem': f'✅ Estoque atualizado para {dados["emEstoque"]}!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
