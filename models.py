from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Cliente(db.Model):
    __tablename__ = "cliente"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100))
    veiculos = db.relationship('Veiculo', backref='cliente', lazy=True)

class Veiculo(db.Model):
    __tablename__ = "veiculo"
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(100), nullable=False)
    placa = db.Column(db.String(20), nullable=False)
    ano = db.Column(db.String(10))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    ordens = db.relationship('OrdemServico', backref='veiculo', lazy=True)

class OrdemServico(db.Model):
    __tablename__ = "ordem_servico"
    id = db.Column(db.Integer, primary_key=True)
    descricao = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    valor_total = db.Column(db.Float)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)
    itens_usados = db.relationship('ItemOrdemServico', backref='ordem_servico', lazy=True)

class ItemEstoque(db.Model):
    __tablename__ = "item_estoque"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(200))
    quantidade = db.Column(db.Integer, default=0, nullable=False)
    estoque_minimo = db.Column(db.Integer, default=1, nullable=False)

class ItemOrdemServico(db.Model):
    __tablename__ = "item_ordem_servico"
    id = db.Column(db.Integer, primary_key=True)
    ordem_servico_id = db.Column(db.Integer, db.ForeignKey('ordem_servico.id'), nullable=False)
    item_estoque_id = db.Column(db.Integer, db.ForeignKey('item_estoque.id'), nullable=False)
    quantidade_usada = db.Column(db.Integer, nullable=False)
    item_estoque = db.relationship('ItemEstoque')