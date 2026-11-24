from flask import Blueprint, current_app, render_template, request

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
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
    return render_template("index.html", **contexto)


@main_bp.route("/como-funciona")
def como_funciona():
    return render_template("como_funciona.html")


@main_bp.route("/sobre")
def sobre():
    return render_template("sobre.html")


@main_bp.route("/contato")
def contato():
    service = current_app.extensions["pet_service"]
    servicos = service.obter_servicos_contato()
    return render_template("contato.html", servicos=servicos)
