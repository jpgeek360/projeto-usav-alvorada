from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for

pets_bp = Blueprint("pets", __name__, url_prefix="/pets")


@pets_bp.route("/filtrar")
def filtrar():
    """Endpoint assíncrono que retorna apenas o fragmento HTML do grid 4x5 + paginação."""
    service = current_app.extensions["pet_service"]
    pagina = request.args.get("pagina", 1, type=int)
    especie = request.args.get("especie", default=None)
    genero = request.args.get("genero", default=None)
    porte = request.args.get("porte", default=None)

    contexto = service.obter_catalogo(
        pagina=pagina,
        por_pagina=current_app.config["ITEMS_PER_PAGE"],
        especie=especie,
        genero=genero,
        porte=porte,
    )
    contexto["filtros"] = {
        "especie": especie or "",
        "genero": genero or "",
        "porte": porte or "",
    }
    return render_template("partials/_pet_grid.html", **contexto)


@pets_bp.route("/<pet_id>")
def detalhe(pet_id: str):
    service = current_app.extensions["pet_service"]
    dados = service.obter_detalhes_pet(pet_id)
    if not dados:
        abort(404)
    return render_template("pet_detail.html", **dados)


@pets_bp.route("/cadastrar", methods=["GET", "POST"])
def cadastrar():
    service = current_app.extensions["pet_service"]
    if request.method == "POST":
        try:
            foto_principal = request.files.get("foto_principal")
            galeria = request.files.getlist("galeria")
            vacinas_selecionadas = request.form.getlist("vacinas")
            pet = service.cadastrar_pet(
                request.form,
                foto_principal,
                galeria,
                vacinas_selecionadas=vacinas_selecionadas,
            )
            flash(f"Animal '{pet.nome}' cadastrado com sucesso!", "success")
            return redirect(url_for("pets.detalhe", pet_id=pet.id))
        except ValueError as exc:
            flash(str(exc), "danger")

    opcoes = service.obter_opcoes_cadastro()
    return render_template(
        "pet_create.html",
        **opcoes,
    )


@pets_bp.route("/<pet_id>/editar", methods=["GET", "POST"])
def editar(pet_id: str):
    service = current_app.extensions["pet_service"]
    dados = service.obter_detalhes_pet(pet_id)
    if not dados:
        abort(404)

    if request.method == "POST":
        try:
            foto_principal = request.files.get("foto_principal")
            galeria = request.files.getlist("galeria")
            vacinas_selecionadas = request.form.getlist("vacinas")
            fotos_remover = request.form.getlist("fotos_remover")
            pet = service.editar_pet(
                pet_id=pet_id,
                form_data=request.form,
                foto_principal=foto_principal,
                galeria=galeria,
                vacinas_selecionadas=vacinas_selecionadas,
                fotos_remover=fotos_remover,
            )
            flash(f"Dados de '{pet.nome}' atualizados com sucesso!", "success")
            return redirect(url_for("pets.detalhe", pet_id=pet.id))
        except ValueError as exc:
            flash(str(exc), "danger")

    opcoes = service.obter_opcoes_cadastro()
    return render_template(
        "pet_edit.html",
        pet=dados["pet"],
        **opcoes,
    )


@pets_bp.route("/vacinas", methods=["GET", "POST"])
def vacinas():
    service = current_app.extensions["pet_service"]
    if request.method == "POST":
        try:
            nome = request.form.get("nome", "")
            vacina_criada = service.cadastrar_vacina(nome)
            flash(f"Vacina '{vacina_criada}' cadastrada com sucesso!", "success")
            return redirect(url_for("pets.vacinas"))
        except ValueError as exc:
            flash(str(exc), "danger")

    lista_vacinas = service.listar_vacinas()
    return render_template("vacinas.html", vacinas=lista_vacinas)


@pets_bp.route("/vacinas/editar", methods=["GET", "POST"])
def editar_vacina():
    service = current_app.extensions["pet_service"]
    lista_vacinas = service.listar_vacinas()

    if request.method == "POST":
        nome_antigo = request.form.get("nome_antigo", "")
        nome_novo = request.form.get("nome_novo", "")
        try:
            vacina_atualizada = service.editar_vacina(nome_antigo, nome_novo)
            flash(f"Vacina atualizada para '{vacina_atualizada}' com sucesso!", "success")
            return redirect(url_for("pets.vacinas"))
        except ValueError as exc:
            flash(str(exc), "danger")
            return render_template("vacina_edit.html", nome_atual=nome_antigo)

    nome_atual = request.args.get("nome", "").strip()
    if not nome_atual or nome_atual not in lista_vacinas:
        flash("Selecione uma vacina válida para alterar.", "warning")
        return redirect(url_for("pets.vacinas"))

    return render_template("vacina_edit.html", nome_atual=nome_atual)


@pets_bp.route("/vacinas/remover", methods=["POST"])
def remover_vacina():
    service = current_app.extensions["pet_service"]
    nome = request.form.get("nome", "")
    if service.remover_vacina(nome):
        flash(f"Vacina '{nome}' removida.", "success")
    else:
        flash("Vacina não encontrada.", "warning")
    return redirect(url_for("pets.vacinas"))
