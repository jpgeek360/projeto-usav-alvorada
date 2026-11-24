from flask import Flask
from blueprints.main import main_bp
from blueprints.pets import pets_bp
from config import Config
from repositories.json_pet_repository import JsonPetRepository
from services.pet_service import PetService


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Injeção de Dependência (para migrar para BD, basta trocar JsonPetRepository)
    pet_repository = JsonPetRepository(app.config["DATA_FILE"])
    pet_service = PetService(
        repository=pet_repository,
        upload_folder=app.config["UPLOAD_FOLDER"],
        allowed_extensions=app.config["ALLOWED_EXTENSIONS"],
        whatsapp_adocao=app.config["WHATSAPP_ADOCAO_PADRAO"],
    )
    app.extensions["pet_service"] = pet_service

    app.register_blueprint(main_bp)
    app.register_blueprint(pets_bp)

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=False, host="0.0.0.0", port=5001)