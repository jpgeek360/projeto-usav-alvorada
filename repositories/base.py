from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
from models.pet import Pet


class PetRepository(ABC):
    @abstractmethod
    def listar_paginado(
        self,
        pagina: int = 1,
        por_pagina: int = 20,
        especie: Optional[str] = None,
        genero: Optional[str] = None,
        porte: Optional[str] = None,
    ) -> Tuple[List[Pet], int]:
        pass

    @abstractmethod
    def buscar_por_id(self, pet_id: str) -> Optional[Pet]:
        pass

    @abstractmethod
    def adicionar(self, pet: Pet) -> Pet:
        pass

    @abstractmethod
    def atualizar(self, pet: Pet) -> bool:
        pass

    @abstractmethod
    def remover(self, pet_id: str) -> bool:
        pass

    @abstractmethod
    def listar_especies_distintas(self) -> List[str]:
        pass

    @abstractmethod
    def listar_vacinas(self) -> List[str]:
        pass

    @abstractmethod
    def adicionar_vacina(self, nome: str) -> str:
        pass

    @abstractmethod
    def atualizar_vacina(self, nome_antigo: str, nome_novo: str) -> str:
        pass

    @abstractmethod
    def remover_vacina(self, nome: str) -> bool:
        pass

    @abstractmethod
    def listar_servicos_contato(self) -> List[dict]:
        pass
