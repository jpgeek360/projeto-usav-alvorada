import math
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import quote
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from models.pet import GENEROS_VALIDOS, PORTES_VALIDOS, Pet
from repositories.base import PetRepository


class PetService:
    MAX_NOME = 60
    MAX_IDADE = 30
    MAX_PESO = 30
    MAX_TEMPO_ABRIGO = 60
    MAX_HISTORIA = 1000
    MAX_VACINA_NOME = 60

    def __init__(
        self,
        repository: PetRepository,
        upload_folder: Path,
        allowed_extensions: Set[str],
        whatsapp_adocao: str,
    ) -> None:
        self.repository = repository
        self.upload_folder = Path(upload_folder)
        self.allowed_extensions = {ext.lower() for ext in allowed_extensions}
        self.whatsapp_adocao = "".join(ch for ch in str(whatsapp_adocao) if ch.isdigit())
        self.upload_folder.mkdir(parents=True, exist_ok=True)

    def _extensao_permitida(self, filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in self.allowed_extensions

    def _salvar_imagem(self, arquivo: FileStorage) -> str:
        if not arquivo or not arquivo.filename:
            raise ValueError("Arquivo de imagem inválido.")
        if not self._extensao_permitida(arquivo.filename):
            permitidas = ", ".join(sorted(self.allowed_extensions))
            raise ValueError(f"Formato de imagem não suportado. Use: {permitidas}.")

        nome_seguro = secure_filename(arquivo.filename)
        ext = nome_seguro.rsplit(".", 1)[1].lower()
        nome_final = f"{uuid.uuid4().hex}.{ext}"
        destino = self.upload_folder / nome_final
        arquivo.save(destino)
        return f"/static/uploads/{nome_final}"

    def _validar_campos_pet(self, form_data: Dict[str, Any]) -> Dict[str, str]:
        nome = str(form_data.get("nome", "")).strip()
        especie = str(form_data.get("especie", "")).strip()
        genero = str(form_data.get("genero", "")).strip()
        porte = str(form_data.get("porte", "")).strip()
        idade = str(form_data.get("idade", "")).strip()
        peso = str(form_data.get("peso", "")).strip()
        tempo_abrigo = str(form_data.get("tempo_abrigo", "")).strip()
        historia = str(form_data.get("historia", "")).strip()

        if not all([nome, especie, genero, porte, idade, peso, tempo_abrigo, historia]):
            raise ValueError("Preencha todos os campos obrigatórios.")

        if len(nome) > self.MAX_NOME:
            raise ValueError(f"O campo Nome deve ter no máximo {self.MAX_NOME} caracteres.")
        if len(idade) > self.MAX_IDADE:
            raise ValueError(f"O campo Idade deve ter no máximo {self.MAX_IDADE} caracteres.")
        if len(peso) > self.MAX_PESO:
            raise ValueError(f"O campo Peso deve ter no máximo {self.MAX_PESO} caracteres.")
        if len(tempo_abrigo) > self.MAX_TEMPO_ABRIGO:
            raise ValueError(f"O campo Tempo no abrigo deve ter no máximo {self.MAX_TEMPO_ABRIGO} caracteres.")
        if len(historia) > self.MAX_HISTORIA:
            raise ValueError(f"O campo História deve ter no máximo {self.MAX_HISTORIA} caracteres.")

        especies_validas = self.repository.listar_especies_distintas()
        if especie not in especies_validas:
            raise ValueError("Selecione uma espécie válida da lista.")
        if genero not in GENEROS_VALIDOS:
            raise ValueError("Gênero inválido.")
        if porte not in PORTES_VALIDOS:
            raise ValueError("Porte inválido.")

        return {
            "nome": nome,
            "especie": especie,
            "genero": genero,
            "porte": porte,
            "idade": idade,
            "peso": peso,
            "tempo_abrigo": tempo_abrigo,
            "historia": historia,
        }

    def obter_catalogo(
        self,
        pagina: int = 1,
        por_pagina: int = 20,
        especie: Optional[str] = None,
        genero: Optional[str] = None,
        porte: Optional[str] = None,
    ) -> Dict[str, Any]:
        pagina = max(1, pagina)
        por_pagina = max(1, por_pagina)

        pets, total = self.repository.listar_paginado(
            pagina=pagina,
            por_pagina=por_pagina,
            especie=especie or None,
            genero=genero or None,
            porte=porte or None,
        )
        total_paginas = max(1, math.ceil(total / por_pagina)) if total > 0 else 1
        if pagina > total_paginas:
            pagina = total_paginas
            pets, total = self.repository.listar_paginado(
                pagina=pagina,
                por_pagina=por_pagina,
                especie=especie or None,
                genero=genero or None,
                porte=porte or None,
            )

        especies = self.repository.listar_especies_distintas()

        return {
            "pets": pets,
            "total": total,
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "especies": especies,
        }

    def obter_opcoes_cadastro(self) -> Dict[str, List[str]]:
        return {
            "especies": self.repository.listar_especies_distintas(),
            "vacinas": self.repository.listar_vacinas(),
            "generos": GENEROS_VALIDOS,
            "portes": PORTES_VALIDOS,
        }

    def listar_vacinas(self) -> List[str]:
        return self.repository.listar_vacinas()

    def cadastrar_vacina(self, nome: str) -> str:
        nome_limpo = str(nome or "").strip()
        if not nome_limpo:
            raise ValueError("Informe o nome da vacina.")
        if len(nome_limpo) > self.MAX_VACINA_NOME:
            raise ValueError(f"O nome da vacina deve ter no máximo {self.MAX_VACINA_NOME} caracteres.")
        return self.repository.adicionar_vacina(nome_limpo)

    def editar_vacina(self, nome_antigo: str, nome_novo: str) -> str:
        antigo_limpo = str(nome_antigo or "").strip()
        novo_limpo = str(nome_novo or "").strip()
        if not antigo_limpo:
            raise ValueError("Vacina original não informada.")
        if not novo_limpo:
            raise ValueError("Informe o novo nome da vacina.")
        if len(novo_limpo) > self.MAX_VACINA_NOME:
            raise ValueError(f"O nome da vacina deve ter no máximo {self.MAX_VACINA_NOME} caracteres.")
        return self.repository.atualizar_vacina(antigo_limpo, novo_limpo)

    def remover_vacina(self, nome: str) -> bool:
        return self.repository.remover_vacina(nome)

    def obter_detalhes_pet(self, pet_id: str) -> Optional[Dict[str, Any]]:
        pet = self.repository.buscar_por_id(pet_id)
        if not pet:
            return None

        todas_fotos: List[str] = []
        if pet.foto_principal:
            todas_fotos.append(pet.foto_principal)
        for foto in pet.galeria:
            if foto and foto not in todas_fotos:
                todas_fotos.append(foto)

        mensagem = (
            f"Olá! Tenho interesse em adotar o(a) {pet.nome} "
            f"(Código: #{pet.id[:8]}), que vi no portal AUAUVORADA."
        )
        link_whatsapp = f"https://wa.me/{self.whatsapp_adocao}?text={quote(mensagem)}"

        return {
            "pet": pet,
            "todas_fotos": todas_fotos,
            "link_whatsapp": link_whatsapp,
        }

    def cadastrar_pet(
        self,
        form_data: Dict[str, Any],
        foto_principal: Optional[FileStorage],
        galeria: Optional[List[FileStorage]] = None,
        vacinas_selecionadas: Optional[List[str]] = None,
    ) -> Pet:
        campos = self._validar_campos_pet(form_data)
        if not foto_principal or not foto_principal.filename:
            raise ValueError("A foto principal é obrigatória.")

        vacinas_cadastradas = set(self.repository.listar_vacinas())
        vacinas = [v.strip() for v in (vacinas_selecionadas or []) if v.strip() in vacinas_cadastradas]

        url_principal = self._salvar_imagem(foto_principal)
        urls_galeria: List[str] = []
        for item in galeria or []:
            if item and item.filename:
                urls_galeria.append(self._salvar_imagem(item))

        novo_pet = Pet(
            nome=campos["nome"],
            especie=campos["especie"],
            genero=campos["genero"],
            idade=campos["idade"],
            porte=campos["porte"],
            peso=campos["peso"],
            historia=campos["historia"],
            tempo_abrigo=campos["tempo_abrigo"],
            vacinas=vacinas,
            foto_principal=url_principal,
            galeria=urls_galeria,
        )
        return self.repository.adicionar(novo_pet)

    def editar_pet(
        self,
        pet_id: str,
        form_data: Dict[str, Any],
        foto_principal: Optional[FileStorage] = None,
        galeria: Optional[List[FileStorage]] = None,
        vacinas_selecionadas: Optional[List[str]] = None,
        fotos_remover: Optional[List[str]] = None,
    ) -> Pet:
        pet_existente = self.repository.buscar_por_id(pet_id)
        if not pet_existente:
            raise ValueError("Animal não encontrado.")

        campos = self._validar_campos_pet(form_data)

        vacinas_cadastradas = set(self.repository.listar_vacinas())
        vacinas = [v.strip() for v in (vacinas_selecionadas or []) if v.strip() in vacinas_cadastradas]

        url_principal = pet_existente.foto_principal
        if foto_principal and foto_principal.filename:
            url_principal = self._salvar_imagem(foto_principal)

        remover_set = set(fotos_remover or [])
        galeria_atualizada = [f for f in pet_existente.galeria if f not in remover_set]

        for item in galeria or []:
            if item and item.filename:
                galeria_atualizada.append(self._salvar_imagem(item))

        adotado = form_data.get("adotado") == "1"

        pet_atualizado = Pet(
            id=pet_existente.id,
            nome=campos["nome"],
            especie=campos["especie"],
            genero=campos["genero"],
            idade=campos["idade"],
            porte=campos["porte"],
            peso=campos["peso"],
            historia=campos["historia"],
            tempo_abrigo=campos["tempo_abrigo"],
            vacinas=vacinas,
            foto_principal=url_principal,
            galeria=galeria_atualizada,
            adotado=adotado,
        )
        self.repository.atualizar(pet_atualizado)
        return pet_atualizado

    def obter_servicos_contato(self) -> List[Dict[str, str]]:
        servicos_raw = self.repository.listar_servicos_contato()
        resultado: List[Dict[str, str]] = []

        for srv in servicos_raw:
            titulo = str(srv.get("titulo", "Atendimento")).strip()
            descricao = str(srv.get("descricao", "")).strip()
            icone = str(srv.get("icone", "bi-chat-dots")).strip()
            numero = "".join(ch for ch in str(srv.get("whatsapp", self.whatsapp_adocao)) if ch.isdigit())
            mensagem = str(
                srv.get("mensagem")
                or f"Olá! Gostaria de informações sobre o serviço: {titulo}."
            ).strip()
            whatsapp_url = srv.get("whatsapp_url") or f"https://wa.me/{numero}?text={quote(mensagem)}"

            resultado.append(
                {
                    "titulo": titulo,
                    "descricao": descricao,
                    "icone": icone,
                    "whatsapp_url": whatsapp_url,
                }
            )
        return resultado
