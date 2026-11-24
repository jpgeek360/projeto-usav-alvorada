from contextlib import contextmanager
import json
import os
from pathlib import Path
import tempfile
from typing import List, Optional, Tuple
from models.pet import Pet
from repositories.base import PetRepository

if os.name == "nt":
    import msvcrt
else:
    import fcntl


class JsonPetRepository(PetRepository):
    """Implementação concreta baseada em arquivo JSON com escrita atômica e lock de SO."""

    def __init__(self, filepath: Path) -> None:
        self.filepath = Path(filepath)
        self.lockfile = self.filepath.with_suffix(".lock")
        self.filepath.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _file_lock(self):
        with open(self.lockfile, "a+") as lock_fd:
            if os.name == "nt":
                msvcrt.locking(lock_fd.fileno(), msvcrt.LK_LOCK, 1)
            else:
                fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                if os.name == "nt":
                    lock_fd.seek(0)
                    msvcrt.locking(lock_fd.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)

    def _read_raw(self) -> dict:
        if not self.filepath.exists():
            return {"animais": [], "servicos_contato": []}
        with open(self.filepath, "r", encoding="utf-8") as f:
            return json.load(f)

    def _write_atomic(self, payload: dict) -> None:
        fd, temp_path = tempfile.mkstemp(dir=str(self.filepath.parent), suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as tmp_file:
                json.dump(payload, tmp_file, ensure_ascii=False, indent=2)
            os.replace(temp_path, self.filepath)
        except Exception:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def listar_paginado(
        self,
        pagina: int = 1,
        por_pagina: int = 20,
        especie: Optional[str] = None,
        genero: Optional[str] = None,
        porte: Optional[str] = None,
    ) -> Tuple[List[Pet], int]:
        with self._file_lock():
            raw = self._read_raw()

        pets = [Pet.from_dict(item) for item in raw.get("animais", []) if not item.get("adotado", False)]

        if especie:
            pets = [p for p in pets if p.especie.lower() == especie.strip().lower()]
        if genero:
            pets = [p for p in pets if p.genero.lower() == genero.strip().lower()]
        if porte:
            pets = [p for p in pets if p.porte.lower() == porte.strip().lower()]

        total = len(pets)
        inicio = max(0, (pagina - 1) * por_pagina)
        fim = inicio + por_pagina
        return pets[inicio:fim], total

    def buscar_por_id(self, pet_id: str) -> Optional[Pet]:
        with self._file_lock():
            raw = self._read_raw()
        for item in raw.get("animais", []):
            if item.get("id") == pet_id:
                return Pet.from_dict(item)
        return None

    def adicionar(self, pet: Pet) -> Pet:
        with self._file_lock():
            raw = self._read_raw()
            raw.setdefault("animais", []).insert(0, pet.to_dict())
            self._write_atomic(raw)
        return pet

    def atualizar(self, pet: Pet) -> bool:
        with self._file_lock():
            raw = self._read_raw()
            animais = raw.get("animais", [])
            for idx, item in enumerate(animais):
                if item.get("id") == pet.id:
                    animais[idx] = pet.to_dict()
                    self._write_atomic(raw)
                    return True
        return False

    def remover(self, pet_id: str) -> bool:
        with self._file_lock():
            raw = self._read_raw()
            animais = raw.get("animais", [])
            filtrados = [item for item in animais if item.get("id") != pet_id]
            if len(filtrados) == len(animais):
                return False
            raw["animais"] = filtrados
            self._write_atomic(raw)
            return True

    def listar_especies_distintas(self) -> List[str]:
        with self._file_lock():
            raw = self._read_raw()
        especies = {item["especie"] for item in raw.get("animais", []) if item.get("especie")}
        return sorted(especies)

    def listar_servicos_contato(self) -> List[dict]:
        with self._file_lock():
            raw = self._read_raw()
        return raw.get("servicos_contato", [])