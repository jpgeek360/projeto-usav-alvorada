from dataclasses import dataclass, field
from typing import Any, Dict, List
import uuid

GENEROS_VALIDOS = ["Macho", "Fêmea"]
PORTES_VALIDOS = ["Pequeno", "Médio", "Grande"]


@dataclass
class Pet:
    nome: str
    especie: str
    genero: str
    idade: str
    porte: str
    peso: str
    historia: str
    tempo_abrigo: str
    foto_principal: str
    vacinas: List[str] = field(default_factory=list)
    galeria: List[str] = field(default_factory=list)
    adotado: bool = False
    id: str = field(default_factory=lambda: uuid.uuid4().hex)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "nome": self.nome,
            "especie": self.especie,
            "genero": self.genero,
            "idade": self.idade,
            "porte": self.porte,
            "peso": self.peso,
            "historia": self.historia,
            "tempo_abrigo": self.tempo_abrigo,
            "vacinas": list(self.vacinas),
            "foto_principal": self.foto_principal,
            "galeria": list(self.galeria),
            "adotado": bool(self.adotado),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Pet":
        return cls(
            id=str(data.get("id") or uuid.uuid4().hex),
            nome=str(data.get("nome", "")).strip(),
            especie=str(data.get("especie", "")).strip(),
            genero=str(data.get("genero", "")).strip(),
            idade=str(data.get("idade", "")).strip(),
            porte=str(data.get("porte", "")).strip(),
            peso=str(data.get("peso", "")).strip(),
            historia=str(data.get("historia", "")).strip(),
            tempo_abrigo=str(data.get("tempo_abrigo", "")).strip(),
            foto_principal=str(data.get("foto_principal", "")).strip(),
            vacinas=list(data.get("vacinas") or []),
            galeria=list(data.get("galeria") or []),
            adotado=bool(data.get("adotado", False)),
        )
