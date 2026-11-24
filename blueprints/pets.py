from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, url_for
from models.pet import GENEROS_VALIDOS, PORTES_VALIDOS

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
            pet = service.cadastrar_pet(request.form, foto_principal, galeria)
            flash(f"Animal '{pet.nome}' cadastrado com sucesso!", "success")
            return redirect(url_for("pets.detalhe", pet_id=pet.id))
        except ValueError as exc:
            flash(str(exc), "danger")

    return render_template(
        "pet_create.html",
        generos=GENEROS_VALIDOS,
        portes=PORTES_VALIDOS,
    )