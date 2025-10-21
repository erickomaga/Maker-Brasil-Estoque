import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('estoque.db')
    conn.row_factory = sqlite3.Row
    return conn

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
            # Educação Infantil
            ('Tapete Lúdico', 'infantil', 0, 10),
            ('Encartes', 'infantil', 0, 10),
            ('Lego 9656', 'infantil', 0, 10),
            ('Caracol', 'infantil', 0, 10),
            ('Cards', 'infantil', 0, 10),

            # Fundamental 1: 1º e 2º Ano
            ('Lego 9686', 'fundamental1-2', 0, 10),
            ('Caracol', 'fundamental1-2', 0, 10),
            ('Cards', 'fundamental1-2', 0, 10),
            ('Tipos de Maker', 'fundamental1-2', 0, 10),

            # Fundamental 1: 3º ao 5º Ano
            ('Lego WeDo', 'fundamental3-5', 0, 10),
            ('Lego We98', 'fundamental3-5', 0, 10),
            ('Educação Financeira Maker', 'fundamental3-5', 0, 10),
            ('Caneta 3D', 'fundamental3-5', 0, 10),
            ('Filamento', 'fundamental3-5', 0, 10),
            ('Tapete', 'fundamental3-5', 0, 10),
            ('Caracol', 'fundamental3-5', 0, 10),
            ('Cards', 'fundamental3-5', 0, 10)
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

@app.route('/editar')
def editar():
    return render_template('editar.html')

@app.route('/api/produtos')
def get_produtos():
    conn = get_db_connection()
    produtos = conn.execute('SELECT * FROM produtos ORDER BY categoria, nome').fetchall()
    conn.close()
    return jsonify([dict(row) for row in produtos])

@app.route('/api/atualizar', methods=['POST'])
def atualizar_produtos():
    dados = request.get_json()
    conn = get_db_connection()
    cursor = conn.cursor()

    for p in dados:
        cursor.execute(
            'UPDATE produtos SET em_estoque = ?, necessario = ? WHERE id = ?',
            (p['emEstoque'], p['necessario'], p['id'])
        )
    conn.commit()
    conn.close()
    return jsonify({'mensagem': '✅ Alterações salvas com sucesso!'})

if __name__ == '__main__':
    init_db()
    app.run(debug=True)