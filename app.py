from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Cliente, Veiculo, OrdemServico, ItemEstoque, ItemOrdemServico

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///oficina.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecret'
db.init_app(app)

@app.route('/')
def inicio():
    avisos_estoque = ItemEstoque.query.filter(ItemEstoque.quantidade <= ItemEstoque.estoque_minimo).all()
    return render_template('inicio.html', avisos_estoque=avisos_estoque)

# ----------- CLIENTES --------------

@app.route('/clientes')
def clientes():
    lista = Cliente.query.all()
    return render_template('clientes.html', clientes=lista)

@app.route('/clientes/novo', methods=['GET', 'POST'])
def cliente_novo():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        novo_cliente = Cliente(nome=nome, telefone=telefone, email=email)
        db.session.add(novo_cliente)
        db.session.commit()
        flash('Cliente cadastrado com sucesso!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', acao='Novo', cliente=None)

@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def cliente_editar(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == 'POST':
        cliente.nome = request.form['nome']
        cliente.telefone = request.form['telefone']
        cliente.email = request.form['email']
        db.session.commit()
        flash('Cliente atualizado com sucesso!', 'success')
        return redirect(url_for('clientes'))
    return render_template('cliente_form.html', acao='Editar', cliente=cliente)

@app.route('/clientes/deletar/<int:id>', methods=['POST'])
def cliente_deletar(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash('Cliente removido com sucesso!', 'success')
    return redirect(url_for('clientes'))

# ----------- VEICULOS --------------

@app.route('/veiculos')
def veiculos():
    lista = Veiculo.query.all()
    return render_template('veiculos.html', veiculos=lista)

@app.route('/veiculos/novo', methods=['GET', 'POST'])
def veiculo_novo():
    clientes = Cliente.query.all()
    if request.method == 'POST':
        modelo = request.form['modelo']
        placa = request.form['placa']
        ano = request.form['ano']
        cliente_id = request.form['cliente_id']
        novo_veiculo = Veiculo(modelo=modelo, placa=placa, ano=ano, cliente_id=cliente_id)
        db.session.add(novo_veiculo)
        db.session.commit()
        flash('Veículo cadastrado com sucesso!', 'success')
        return redirect(url_for('veiculos'))
    return render_template('veiculo_form.html', acao='Novo', veiculo=None, clientes=clientes)

@app.route('/veiculos/editar/<int:id>', methods=['GET', 'POST'])
def veiculo_editar(id):
    veiculo = Veiculo.query.get_or_404(id)
    clientes = Cliente.query.all()
    if request.method == 'POST':
        veiculo.modelo = request.form['modelo']
        veiculo.placa = request.form['placa']
        veiculo.ano = request.form['ano']
        veiculo.cliente_id = request.form['cliente_id']
        db.session.commit()
        flash('Veículo atualizado com sucesso!', 'success')
        return redirect(url_for('veiculos'))
    return render_template('veiculo_form.html', acao='Editar', veiculo=veiculo, clientes=clientes)

@app.route('/veiculos/deletar/<int:id>', methods=['POST'])
def veiculo_deletar(id):
    veiculo = Veiculo.query.get_or_404(id)
    db.session.delete(veiculo)
    db.session.commit()
    flash('Veículo removido com sucesso!', 'success')
    return redirect(url_for('veiculos'))

# ----------- ORDEM DE SERVIÇO --------------

@app.route('/ordens')
def ordens():
    lista = OrdemServico.query.all()
    return render_template('ordens.html', ordens=lista)

@app.route('/ordens/novo', methods=['GET', 'POST'])
def ordem_nova():
    veiculos = Veiculo.query.all()
    itens_estoque = ItemEstoque.query.all()
    if request.method == 'POST':
        descricao = request.form['descricao']
        status = request.form['status']
        valor_total = request.form['valor_total']
        veiculo_id = request.form['veiculo_id']
        nova_ordem = OrdemServico(descricao=descricao, status=status, valor_total=valor_total, veiculo_id=veiculo_id)
        db.session.add(nova_ordem)
        db.session.flush()  # Para pegar o id da ordem antes de commit

        # Peças/insumos usados
        itens_ids = request.form.getlist('item_id')
        quantidades = request.form.getlist('quantidade_usada')
        for item_id, quantidade in zip(itens_ids, quantidades):
            if item_id and quantidade and int(quantidade) > 0:
                item_usado = ItemOrdemServico(
                    ordem_servico_id=nova_ordem.id,
                    item_estoque_id=int(item_id),
                    quantidade_usada=int(quantidade)
                )
                db.session.add(item_usado)
        db.session.commit()
        flash('Ordem de Serviço cadastrada com sucesso!', 'success')
        return redirect(url_for('ordens'))
    return render_template('ordem_form.html', acao='Nova', ordem=None, veiculos=veiculos, itens_estoque=itens_estoque)

@app.route('/ordens/editar/<int:id>', methods=['GET', 'POST'])
def ordem_editar(id):
    ordem = OrdemServico.query.get_or_404(id)
    veiculos = Veiculo.query.all()
    itens_estoque = ItemEstoque.query.all()
    if request.method == 'POST':
        status_atual = ordem.status
        ordem.descricao = request.form['descricao']
        ordem.status = request.form['status']
        ordem.valor_total = request.form['valor_total']
        ordem.veiculo_id = request.form['veiculo_id']
        db.session.commit()

        # Atualizar itens usados: remove todos e adiciona novamente conforme formulário
        ItemOrdemServico.query.filter_by(ordem_servico_id=ordem.id).delete()
        itens_ids = request.form.getlist('item_id')
        quantidades = request.form.getlist('quantidade_usada')
        for item_id, quantidade in zip(itens_ids, quantidades):
            if item_id and quantidade and int(quantidade) > 0:
                item_usado = ItemOrdemServico(
                    ordem_servico_id=ordem.id,
                    item_estoque_id=int(item_id),
                    quantidade_usada=int(quantidade)
                )
                db.session.add(item_usado)
        db.session.commit()

        # BAIXA AUTOMÁTICA NO ESTOQUE AO FINALIZAR
        if status_atual != "Finalizada" and ordem.status == "Finalizada":
            for item_usado in ordem.itens_usados:
                item_estoque = item_usado.item_estoque
                item_estoque.quantidade -= item_usado.quantidade_usada
                if item_estoque.quantidade < 0:
                    item_estoque.quantidade = 0
            db.session.commit()
            flash('Ordem finalizada e estoque atualizado!', 'success')
        else:
            flash('Ordem atualizada com sucesso!', 'success')
        return redirect(url_for('ordens'))
    return render_template('ordem_form.html', acao='Editar', ordem=ordem, veiculos=veiculos, itens_estoque=itens_estoque)

@app.route('/ordens/deletar/<int:id>', methods=['POST'])
def ordem_deletar(id):
    ordem = OrdemServico.query.get_or_404(id)
    ItemOrdemServico.query.filter_by(ordem_servico_id=ordem.id).delete()
    db.session.delete(ordem)
    db.session.commit()
    flash('Ordem de Serviço removida com sucesso!', 'success')
    return redirect(url_for('ordens'))

# ----------- ESTOQUE --------------

@app.route('/estoque')
def estoque():
    itens = ItemEstoque.query.all()
    return render_template('estoque.html', itens=itens)

@app.route('/estoque/novo', methods=['GET', 'POST'])
def estoque_novo():
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = int(request.form['quantidade'])
        estoque_minimo = int(request.form['estoque_minimo'])
        item = ItemEstoque(nome=nome, descricao=descricao, quantidade=quantidade, estoque_minimo=estoque_minimo)
        db.session.add(item)
        db.session.commit()
        flash('Item cadastrado com sucesso!', 'success')
        return redirect(url_for('estoque'))
    return render_template('estoque_form.html', acao='Novo', item=None)

@app.route('/estoque/editar/<int:id>', methods=['GET', 'POST'])
def estoque_editar(id):
    item = ItemEstoque.query.get_or_404(id)
    if request.method == 'POST':
        item.nome = request.form['nome']
        item.descricao = request.form['descricao']
        item.quantidade = int(request.form['quantidade'])
        item.estoque_minimo = int(request.form['estoque_minimo'])
        db.session.commit()
        flash('Item atualizado com sucesso!', 'success')
        return redirect(url_for('estoque'))
    return render_template('estoque_form.html', acao='Editar', item=item)

@app.route('/estoque/deletar/<int:id>', methods=['POST'])
def estoque_deletar(id):
    item = ItemEstoque.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Item removido com sucesso!', 'success')
    return redirect(url_for('estoque'))

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)