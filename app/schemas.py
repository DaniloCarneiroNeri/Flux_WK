from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class ItemOrdemSchema(BaseModel):
    produto_id: Optional[int] = None
    descricao_item: str
    valor_unitario: float
    quantidade: int

class OrdemServicoCreate(BaseModel):
    cliente_id: int
    valor_total: float
    observacoes: Optional[str] = ""
    status: str = "pending"
    items: List[ItemOrdemSchema] = []

class OrdemUpdatePartial(BaseModel):
    nf_emitida: Optional[bool] = None
    link_nf: Optional[str] = None
    status: Optional[str] = None

class OrcamentoUpdate(BaseModel):
    os_criada: bool

class OrdemStatusUpdate(BaseModel):
    status: str
    data_conclusao: Optional[datetime] = None

class ClienteCreate(BaseModel):
    nome: str
    documento: str
    tipo_pessoa: str
    inscricao_estadual: str
    telefone: str
    email: str
    endereco: str
    municipio: str
    cep: str
    numero: str
    bairro: str
    uf: str

class ServicoCreate(BaseModel):
    descricao: str
    custo: float
    valor_venda: float
    quantidade_estoque: int = 1  

class DespesaCreate(BaseModel):
    descricao: str
    valor: float
    categoria: str 
    data: str
    fixa: bool = False

class EmissaoNotaRequest(BaseModel):
    ordem_id: int 
    cliente_id: int
    valor_servico: float
    discriminacao: str

class LoginRequest(BaseModel):
    usuario: str
    senha: str