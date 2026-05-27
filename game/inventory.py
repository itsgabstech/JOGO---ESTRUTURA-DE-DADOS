"""
UNIMA Survivors - Inventory System (Atividade - Estrutura de Dados)
===================================================================
Duas estruturas de dados implementadas do zero:

1. HashInventory (Hash Table com chaining)
   ─ Armazenamento por chave (item_id)  →  acesso O(1) amortizado
   ─ Buckets: array fixo de listas encadeadas (HashNode)

2. SlotList (Lista Duplamente Encadeada)
   ─ Rastreia a ORDEM visual dos slots do inventário
   ─ Permite arrastar e trocar itens de posição (drag-and-drop)
   ─ Cada nó: item_id (ou None) + ponteiros prev/next
   ─ Swap de dois slots: percorre lista em O(n), troca em O(1)

Separação de responsabilidades:
  HashInventory  →  DADOS dos itens (nome, qtd, tipo)
  SlotList       →  ORDEM dos itens na grade da UI
"""


# ──────────────────────────────────────────────────────────────────────────────
#  Nó da Hash Table
# ──────────────────────────────────────────────────────────────────────────────

class HashNode:
    """
    Nó da lista encadeada usada para resolução de colisões (chaining).

    Atributos:
        item_id  — Chave única do item (string)
        name     — Nome legível do item
        quantity — Quantidade armazenada
        extra    — Dados adicionais (tipo, descrição, etc.)
        next     — Ponteiro para o próximo nó no mesmo bucket
    """

    def __init__(self, item_id: str, name: str, quantity: int, extra: dict = None):
        self.item_id  = item_id
        self.name     = name
        self.quantity = quantity
        self.extra    = extra.copy() if extra else {}
        self.next     = None          # encadeamento para colisão

    def to_dict(self) -> dict:
        """Retorna o item como dicionário (compatível com a UI do jogo)."""
        return {
            'id':       self.item_id,
            'name':     self.name,
            'quantity': self.quantity,
            **self.extra,
        }

    def __repr__(self):
        return (f"HashNode(id={self.item_id!r}, "
                f"name={self.name!r}, qty={self.quantity})")


# ──────────────────────────────────────────────────────────────────────────────
#  Hash Table — implementação própria
# ──────────────────────────────────────────────────────────────────────────────

class HashInventory:
    """
    Hash Table para o inventário de itens do jogador.

    Características:
      • Estrutura principal: array de buckets com encadeamento (chaining)
      • Chave: ID único do item (string normalizada)
      • Acesso por ID: O(1) amortizado
      • Busca por nome: O(n) — varre todos os buckets
      • Máximo de tipos distintos de itens: max_items

    Funcionalidades implementadas:
      1. add_item    — Adiciona item; se já existir, atualiza a quantidade
      2. get_by_id   — Consulta por ID (chave do mapa)
      3. get_by_name — Consulta por nome (busca linear)
      4. display_all — Lista todos os itens armazenados
      5. remove_item — Remove quantidade específica ou o item completo
    """

    # Número de buckets — potência de 2 para distribuição uniforme
    _DEFAULT_BUCKETS = 32

    def __init__(self, max_items: int = 16, num_buckets: int = _DEFAULT_BUCKETS):
        """
        Parâmetros:
            max_items   — limite de tipos distintos de itens (tamanho do inventário)
            num_buckets — número de buckets internos da hash table
        """
        self._num_buckets = num_buckets
        self._max_items   = max_items
        self._buckets: list = [None] * num_buckets
        self._count = 0              # tipos distintos de itens armazenados

    # ── Função de Hash ────────────────────────────────────────────────────────

    def _hash(self, key: str) -> int:
        """
        Função de hash customizada — variação do algoritmo djb2.

        Fórmula: h = (h * 31 + ord(c)) mod num_buckets
          • Primo 31 distribui caracteres uniformemente
          • Máscara 0xFFFFFFFF mantém inteiro de 32 bits (sem overflow)
          • Módulo final mapeia para índice válido do array

        Complexidade: O(|key|)
        """
        h = 5381                         # semente inicial (número primo)
        for ch in str(key).lower():
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF
        return h % self._num_buckets

    # ── 1. Adicionar Item ─────────────────────────────────────────────────────

    def add_item(self, item_id: str, name: str,
                 quantity: int = 1, extra: dict = None) -> bool:
        """
        Adiciona item ao inventário.

        Regras:
          • Se o item (mesmo ID) já existir → atualiza a quantidade (empilha)
          • Se não existir e houver espaço  → cria novo registro
          • Se inventário cheio (máx. tipos distintos) → retorna False

        Retorna:
          True  — item já existia, quantidade atualizada
          False — item criado pela primeira vez  (ou inventário cheio → None)
        """
        if quantity <= 0:
            return False

        idx  = self._hash(item_id)
        node = self._buckets[idx]

        # Percorre a lista encadeada procurando o ID
        while node is not None:
            if node.item_id == item_id:
                node.quantity += quantity          # já existe → empilha
                if extra:
                    node.extra.update(extra)
                return True                        # atualizado
            node = node.next

        # Não encontrado — verifica limite de capacidade
        if self._count >= self._max_items:
            return None                            # inventário cheio

        # Insere na cabeça da lista encadeada (O(1))
        new_node       = HashNode(item_id, name, quantity, extra)
        new_node.next  = self._buckets[idx]
        self._buckets[idx] = new_node
        self._count += 1
        return False                               # criado

    # ── 2. Consultar por ID ───────────────────────────────────────────────────

    def get_by_id(self, item_id: str):
        """
        Busca item pelo ID (chave do mapa).
        Complexidade: O(1) amortizado (O(k) no pior caso com muitas colisões).

        Retorna: HashNode encontrado, ou None.
        """
        idx  = self._hash(item_id)
        node = self._buckets[idx]
        while node is not None:
            if node.item_id == item_id:
                return node
            node = node.next
        return None

    def query_by_id(self, item_id: str) -> dict:
        """
        Consulta pública por ID.
        Retorna dict com informações do item e campo 'exists' / 'status'.
        """
        node = self.get_by_id(item_id)
        if node:
            result = node.to_dict()
            result['exists'] = True
            result['status'] = (
                f"Item '{node.name}' encontrado. "
                f"Quantidade armazenada: {node.quantity}."
            )
            return result
        return {
            'exists': False,
            'status': f"Item com ID '{item_id}' não encontrado no inventário.",
        }

    # ── 3. Consultar por Nome ─────────────────────────────────────────────────

    def get_by_name(self, name: str):
        """
        Busca item pelo nome (busca linear — O(n)).
        Case-insensitive.

        Retorna: primeiro HashNode cujo nome coincide, ou None.
        """
        target = name.strip().lower()
        for bucket in self._buckets:
            node = bucket
            while node is not None:
                if node.name.lower() == target:
                    return node
                node = node.next
        return None

    def query_by_name(self, name: str) -> dict:
        """
        Consulta pública por nome.
        Retorna dict com informações do item e campo 'exists' / 'status'.
        """
        node = self.get_by_name(name)
        if node:
            result = node.to_dict()
            result['exists'] = True
            result['status'] = (
                f"Item '{node.name}' encontrado. "
                f"Quantidade armazenada: {node.quantity}."
            )
            return result
        return {
            'exists': False,
            'status': f"Item '{name}' não encontrado no inventário.",
        }

    # ── 4. Exibir Inventário ──────────────────────────────────────────────────

    def display_all(self) -> list:
        """
        Retorna lista de todos os itens armazenados.
        Cada item é um dict: {id, name, quantity, type, desc, ...}
        """
        items = []
        for bucket in self._buckets:
            node = bucket
            while node is not None:
                items.append(node.to_dict())
                node = node.next
        return items

    def display_as_slots(self, max_slots: int = 16) -> list:
        """
        Retorna lista de tamanho fixo para exibição em grade (UI).
        Slots além dos itens existentes ficam como None.
        """
        items  = self.display_all()
        result = [None] * max_slots
        for i, item in enumerate(items[:max_slots]):
            result[i] = item
        return result

    def print_inventory(self):
        """Imprime o inventário no terminal (demonstração / debug)."""
        items = self.display_all()
        sep = "─" * 60
        print(sep)
        print(f"  INVENTÁRIO  ({self._count}/{self._max_items} tipos de item)")
        print(sep)
        if not items:
            print("  (vazio)")
        else:
            print(f"  {'ID':<30}  {'Nome':<20}  Qtd")
            print("  " + "─" * 56)
            for item in items:
                print(f"  {item['id']:<30}  {item['name']:<20}  {item['quantity']}")
        print(sep)

    # ── 5. Remover Item ───────────────────────────────────────────────────────

    def remove_item(self, item_id: str, quantity: int = None) -> bool:
        """
        Remove item do inventário.

        Parâmetros:
          item_id  — ID do item a remover
          quantity — se None → remove completamente;
                     se int  → reduz a quantidade (remove se chegar a 0)

        Retorna:
          True  — remoção realizada
          False — item não encontrado
        """
        idx  = self._hash(item_id)
        node = self._buckets[idx]
        prev = None

        while node is not None:
            if node.item_id == item_id:
                if quantity is None or node.quantity <= quantity:
                    # Remove o nó completamente
                    if prev is not None:
                        prev.next = node.next
                    else:
                        self._buckets[idx] = node.next
                    self._count -= 1
                    return True
                else:
                    # Apenas reduz a quantidade
                    node.quantity -= quantity
                    return True
            prev = node
            node = node.next

        return False  # não encontrado

    # ── Utilitários ───────────────────────────────────────────────────────────

    @property
    def item_count(self) -> int:
        """Número de tipos distintos de itens no inventário."""
        return self._count

    @property
    def max_items(self) -> int:
        """Capacidade máxima de tipos distintos."""
        return self._max_items

    def is_empty(self) -> bool:
        return self._count == 0

    def is_full(self) -> bool:
        return self._count >= self._max_items

    def has_item(self, item_id: str) -> bool:
        return self.get_by_id(item_id) is not None

    def get_quantity(self, item_id: str) -> int:
        """Retorna a quantidade de um item, ou 0 se não existir."""
        node = self.get_by_id(item_id)
        return node.quantity if node else 0

    def _load_factor(self) -> float:
        """Fator de carga da hash table (diagnóstico de colisões)."""
        return self._count / self._num_buckets

    def __repr__(self):
        return (f"HashInventory(buckets={self._num_buckets}, "
                f"items={self._count}/{self._max_items}, "
                f"load={self._load_factor():.2f})")


# ──────────────────────────────────────────────────────────────────────────────
#  Lista Duplamente Encadeada — ordem dos slots do inventário
# ──────────────────────────────────────────────────────────────────────────────

class SlotNode:
    """
    Nó da Lista Duplamente Encadeada de slots.

    Cada nó representa uma posição na grade do inventário e guarda o
    item_id do item ocupando aquela posição (None = slot vazio).

    Atributos:
        item_id — ID do item neste slot (None se vazio)
        prev    — ponteiro para o nó anterior
        next    — ponteiro para o próximo nó
    """

    def __init__(self, item_id: str = None):
        self.item_id: str | None = item_id
        self.prev:  'SlotNode | None' = None
        self.next:  'SlotNode | None' = None

    def __repr__(self):
        return f"SlotNode({self.item_id!r})"


class SlotList:
    """
    Lista Duplamente Encadeada que representa a ordem visual dos
    slots do inventário.

    Responsabilidade: rastrear QUAL item está em QUAL posição da grade.
    A busca de dados de um item é delegada ao HashInventory (via item_id).

    Operações principais:
      place(item_id)          — insere ID no primeiro slot vazio
      swap(idx_a, idx_b)      — troca dois slots (drag-and-drop)
      clear_id(item_id)       — esvazia o slot que contém esse ID
      get(index)              — retorna item_id na posição index
      to_list()               — converte para lista Python

    Complexidade:
      place / clear_id / find_first_empty / find_id  →  O(n)
      swap                                           →  O(n) (percorre até os nós)
      to_list                                        →  O(n)
    """

    def __init__(self, size: int):
        self.size  = size
        self.head: SlotNode | None = None
        self.tail: SlotNode | None = None
        # Constrói a cadeia de nós vazios
        for _ in range(size):
            self._append_empty()

    # ── Construção interna ────────────────────────────────────────────────────

    def _append_empty(self):
        """Acrescenta um nó vazio no final da lista. O(1)."""
        node = SlotNode(None)
        if self.tail is None:
            self.head = self.tail = node
        else:
            node.prev      = self.tail
            self.tail.next = node
            self.tail      = node

    # ── Acesso por índice ─────────────────────────────────────────────────────

    def _get_node(self, index: int) -> 'SlotNode | None':
        """Percorre a lista até o nó no índice dado. O(n)."""
        if index < 0 or index >= self.size:
            return None
        node = self.head
        for _ in range(index):
            node = node.next
        return node

    def get(self, index: int) -> 'str | None':
        """Retorna o item_id no índice, ou None."""
        node = self._get_node(index)
        return node.item_id if node else None

    def set(self, index: int, item_id: 'str | None'):
        """Define o item_id no índice."""
        node = self._get_node(index)
        if node is not None:
            node.item_id = item_id

    # ── Operações de inventário ───────────────────────────────────────────────

    def place(self, item_id: str) -> int:
        """
        Coloca item_id no primeiro slot vazio.
        Retorna o índice usado, ou -1 se lista cheia.
        """
        node = self.head
        idx  = 0
        while node is not None:
            if node.item_id is None:
                node.item_id = item_id
                return idx
            node = node.next
            idx += 1
        return -1   # lista cheia

    def clear_id(self, item_id: str) -> bool:
        """
        Esvazia o slot que contém item_id (define como None).
        Retorna True se encontrou e limpou, False se não achou.
        """
        node = self.head
        while node is not None:
            if node.item_id == item_id:
                node.item_id = None
                return True
            node = node.next
        return False

    def find_id(self, item_id: str) -> int:
        """Retorna o índice do slot com item_id, ou -1 se ausente."""
        node = self.head
        idx  = 0
        while node is not None:
            if node.item_id == item_id:
                return idx
            node = node.next
            idx += 1
        return -1

    def find_first_empty(self) -> int:
        """Retorna o índice do primeiro slot vazio, ou -1 se cheio."""
        node = self.head
        idx  = 0
        while node is not None:
            if node.item_id is None:
                return idx
            node = node.next
            idx += 1
        return -1

    def swap(self, idx_a: int, idx_b: int) -> bool:
        """
        Troca os item_ids dos slots idx_a e idx_b.
        Implementação do drag-and-drop: apenas os IDs mudam de nó,
        os ponteiros prev/next da lista permanecem intactos.

        Retorna True se ambos os índices são válidos.
        """
        node_a = self._get_node(idx_a)
        node_b = self._get_node(idx_b)
        if node_a is None or node_b is None:
            return False
        node_a.item_id, node_b.item_id = node_b.item_id, node_a.item_id
        return True

    # ── Conversão / debug ─────────────────────────────────────────────────────

    def to_list(self) -> list:
        """Converte para lista Python de item_ids (None = vazio). O(n)."""
        result = []
        node   = self.head
        while node is not None:
            result.append(node.item_id)
            node = node.next
        return result

    def print_slots(self):
        """Imprime a lista de slots no terminal (debug)."""
        print("SlotList:", self.to_list())

    def __repr__(self):
        return f"SlotList(size={self.size}, head={self.head!r})"


# ──────────────────────────────────────────────────────────────────────────────
#  Utilitário: geração de ID de item
# ──────────────────────────────────────────────────────────────────────────────

def make_item_id(item: dict) -> str:
    """
    Gera um ID único normalizado para um item do inventário.

    Formato: '{type}_{name}' em minúsculas, sem acentos, com _ em vez de espaços.
    Exemplos:
      {'type':'health', 'name':'Kit Médico'}    → 'health_kit_medico'
      {'type':'ammo_pack', 'name':'Munição M4'} → 'ammo_pack_municao_m4'

    Algoritmo:
      1. Concatena type + name
      2. Converte para minúsculas
      3. NFD decomposition: separa cada letra acentuada em letra-base + diacrítico
      4. Remove todos os caracteres de categoria 'Mn' (diacríticos combinantes)
      5. Substitui qualquer caractere não-alfanumérico por '_'
    """
    import unicodedata

    item_type = item.get('type', 'item')
    item_name = item.get('name', item_type)
    raw = f"{item_type}_{item_name}".lower()

    # NFD: decompõe "é" → "e" + diacrítico; depois remove os diacríticos
    decomposed = unicodedata.normalize('NFD', raw)
    sem_acento = ''.join(c for c in decomposed
                         if unicodedata.category(c) != 'Mn')

    # Mantém apenas letras, dígitos e _; troca o resto por _
    resultado = ''.join(c if (c.isalnum() or c == '_') else '_'
                        for c in sem_acento)
    return resultado
