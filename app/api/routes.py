from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.core.database import supabase
from app.schemas import OrdemServicoCreate, OrdemStatusUpdate, OrdemUpdatePartial, ClienteCreate, ServicoCreate, DespesaCreate, EmissaoNotaRequest, LoginRequest, ItemOrdemSchema, OrcamentoUpdate
from typing import List, Optional
import fitz
import re
from app.services import geradorNF
import os
import requests
import time
from datetime import datetime

router = APIRouter()
USUARIO_CENTI = os.getenv("USUARIO_CENTI")
SENHA_CENTI = os.getenv("SENHA_CENTI")

class OrcamentoBody(BaseModel):
    cliente_id: int
    valor_total: float
    items: Optional[List[ItemOrdemSchema]] = []

# --- ROTAS DE CLIENTES ---
@router.get("/clientes")
def get_clientes():
    response = supabase.table("clientes").select("*").execute()
    return response.data

@router.post("/clientes")
def create_cliente(cliente: ClienteCreate):
    try:
        data = cliente.dict()
        response = supabase.table("clientes").insert(data).execute()
        if response.data:
            return {"message": "Cliente cadastrado", "id": response.data[0]['id']}
        else:
            raise HTTPException(status_code=500, detail="Falha ao inserir")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/clientes/{client_id}")
def update_cliente(client_id: int, cliente: ClienteCreate):
    try:
        response = supabase.table("clientes").update(cliente.dict()).eq("id", client_id).execute()
        if response.data:
            return {"message": "Cliente atualizado"}
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/clientes/{client_id}")
def delete_cliente(client_id: int):
    try:
        response = supabase.table("clientes").delete().eq("id", client_id).execute()
        if response.data:
            return {"message": "Cliente excluído"}
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    except Exception as e:
        if "violates foreign key constraint" in str(e):
            raise HTTPException(status_code=400, detail="Cliente possui Ordens de Serviço.")
        raise HTTPException(status_code=400, detail=str(e))

# --- ROTAS DE CATÁLOGO ---
@router.get("/servicos")
def get_catalogo():
    response = supabase.table("servicos_catalogo").select("*").eq("ativo", True).execute()
    return response.data

@router.post("/servicos")
def create_servico(servico: ServicoCreate):
    try:
        data = {
            "descricao": servico.descricao,
            "custo": servico.custo,
            "valor_venda": servico.valor_venda,
            "quantidade_estoque": servico.quantidade_estoque,
            "ativo": True
        }
        response = supabase.table("servicos_catalogo").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Erro ao inserir")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/servicos/{service_id}")
def update_servico(service_id: int, servico: ServicoCreate):
    try:
        data = {
            "descricao": servico.descricao,
            "custo": servico.custo,
            "valor_venda": servico.valor_venda,
            "quantidade_estoque": servico.quantidade_estoque
        }
        response = supabase.table("servicos_catalogo").update(data).eq("id", service_id).execute()
        if response.data:
            return {"message": "Serviço atualizado"}
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/servicos/{service_id}")
def delete_servico(service_id: int):
    try:
        response = supabase.table("servicos_catalogo").delete().eq("id", service_id).execute()
        if response.data:
            return {"message": "Serviço excluído"}
        raise HTTPException(status_code=404, detail="Serviço não encontrado")
    except Exception as e:
        if "violates foreign key constraint" in str(e):
            raise HTTPException(status_code=400, detail="Serviço vinculado a ordens existentes.")
        raise HTTPException(status_code=400, detail=str(e))

# --- ROTAS DE ORDENS DE SERVIÇO ---
@router.get("/ordens")
def get_ordens():
    response = supabase.table("ordens_servico").select("*, clientes(nome), itens_ordem(*)").order("data_abertura", desc=True).execute()
    return response.data

@router.post("/ordens")
def create_ordem(ordem: OrdemServicoCreate):
    try:
        order_data = {
            "cliente_id": ordem.cliente_id,
            "valor_total": ordem.valor_total,
            "observacoes": ordem.observacoes,
            "status": ordem.status
        }
        res_ordem = supabase.table("ordens_servico").insert(order_data).execute()
        if not res_ordem.data:
            raise HTTPException(status_code=500, detail="Erro ao criar ordem")
            
        new_order_id = res_ordem.data[0]['id']

        if ordem.items:
            items_data = [
                {"ordem_id": new_order_id, **item.model_dump()}
                for item in ordem.items
            ]
            supabase.table("itens_ordem").insert(items_data).execute()

        return {"message": "Ordem criada", "id": new_order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/ordens/{order_id}")
def update_ordem(order_id: int, ordem: OrdemServicoCreate):
    try:
        supabase.table("ordens_servico").update({
            "cliente_id": ordem.cliente_id,
            "valor_total": ordem.valor_total,
            "observacoes": ordem.observacoes,
            "status": ordem.status
        }).eq("id", order_id).execute()

        supabase.table("itens_ordem").delete().eq("ordem_id", order_id).execute()

        if ordem.items:
            items_data = [
                {"ordem_id": order_id, **i.model_dump()} 
                for i in ordem.items
            ]
            supabase.table("itens_ordem").insert(items_data).execute()

        return {"message": "Ordem atualizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/ordens/{order_id}")
def patch_order(order_id: int, ordem: OrdemUpdatePartial):
    try:
        update_data = {k: v for k, v in ordem.dict().items() if v is not None}

        if not update_data:
            return {"message": "Nenhum dado para atualizar"}

        response = supabase.table("ordens_servico").update(update_data).eq("id", order_id).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/ordens/{order_id}/status")
def update_status(order_id: int, status_data: OrdemStatusUpdate):
    try:
        update_payload = {"status": status_data.status}

        if status_data.data_conclusao:
            update_payload["data_conclusao"] = status_data.data_conclusao.isoformat() 
        elif status_data.status != 'done':
             update_payload["data_conclusao"] = None

        response = supabase.table("ordens_servico").update(update_payload).eq("id", order_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- ROTAS DE ORÇAMENTOS ---
@router.get("/orcamentos")
def get_orcamentos():
    response = supabase.table("orcamentos").select("*, clientes(nome)").order("id", desc=True).execute()
    if response.data is None:
        return []
    # Remapeia o campo 'items' para 'itens_orcamento' para manter a compatibilidade com o frontend
    for item in response.data:
        if 'items' in item and item['items'] is not None:
            item['itens_orcamento'] = item['items']
    return response.data

@router.post("/orcamentos")
def create_orcamento(orcamento: OrcamentoBody):
    try:
        orcamento_data = {
            "cliente_id": orcamento.cliente_id,
            "valor_total": orcamento.valor_total,
            "items": [item.model_dump() for item in orcamento.items] if orcamento.items else []
        }
        res_orcamento = supabase.table("orcamentos").insert(orcamento_data).execute()
        if not res_orcamento.data:
            raise HTTPException(status_code=500, detail="Erro ao criar orçamento")
            
        new_orcamento_id = res_orcamento.data[0]['id']

        return {"message": "Orçamento criado", "id": new_orcamento_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/orcamentos/{orcamento_id}")
def update_orcamento(orcamento_id: int, orcamento: OrcamentoBody):
    try:
        update_data = {
            "cliente_id": orcamento.cliente_id,
            "valor_total": orcamento.valor_total,
            "items": [item.model_dump() for item in orcamento.items] if orcamento.items else []
        }
        supabase.table("orcamentos").update(update_data).eq("id", orcamento_id).execute()
        return {"message": "Orçamento atualizado"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/orcamentos/{orcamento_id}")
def delete_orcamento(orcamento_id: int):
    try:
        supabase.table("orcamentos").delete().eq("id", orcamento_id).execute()
        return {"message": "Orçamento excluído"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/orcamentos/{orcamento_id}")
def patch_orcamento(orcamento_id: int, orcamento_update: OrcamentoUpdate):
    try:
        update_data = orcamento_update.model_dump()
        response = supabase.table("orcamentos").update(update_data).eq("id", orcamento_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Orçamento não encontrado")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# --- DESPESAS ---
@router.post("/despesas")
def criar_despesa(despesa: DespesaCreate):
    dados = {
            "descricao": despesa.descricao,
            "valor": despesa.valor,
            "tipo": despesa.categoria, 
            "data_cadastro": despesa.data,
            "data_vencimento": None,
            "fixa": despesa.fixa
        }
    response = supabase.table("despesas").insert(dados).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Erro ao salvar despesa")
    return response.data[0]

@router.get("/despesas")
def listar_despesas():
    response = supabase.table("despesas").select("*").order("data_cadastro", desc=True).execute()
    return response.data

@router.delete("/despesas/{despesa_id}")
def deletar_despesa(despesa_id: int):
    supabase.table("despesas").delete().eq("id", despesa_id).execute()
    return {"message": "Deletado com sucesso"}

@router.post("/despesas/importar-extrato")
async def importar_extrato(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        doc = fitz.open(stream=contents, filetype="pdf")
        
        full_text = ""
        for page in doc:
            full_text += page.get_text()
        doc.close()

        transactions = []
        pattern = re.compile(r".*(?:PIX TRANSF|PAGTO VIA PIX|PAGAMENTO VIA PIX)[\s-]+(.+?)\s+([\d\.,]+)", re.IGNORECASE)

        for line in full_text.split('\n'):
            match = pattern.match(line)
            if match:
                description = match.group(1).strip().replace("  ", " ")
                value_str = match.group(2).replace('.', '').replace(',', '.')
                try:
                    value = float(value_str)
                    transactions.append({"descricao": description, "valor": value})
                except ValueError:
                    continue

        return {"transacoes_encontradas": transactions}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar o arquivo PDF: {str(e)}")

@router.get("/utils/cnpj/{cnpj}")
def get_cnpj_data(cnpj: str):
    try:
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        if len(cnpj_limpo) != 14:
            return {}

        url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj_limpo}"
        response = requests.get(url, timeout=5)

        if response.status_code == 404:
            return {}

        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, requests.exceptions.HTTPError):
        return {}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        return {}
# --- ROTA DE EMISSÃO COM VALIDAÇÃO ---
@router.post("/nfe/emitir")
def emitir_nota_fiscal(dados: EmissaoNotaRequest):
    try:
        ARQUIVO_CERTIFICADO = os.getenv("CERT_PATH", "etc/secrets/SCASSISTENCIATECNICAAGRICOLALTDA39623105000132.pfx")
        SENHA_CERTIFICADO = "123456"
        print(f"certificado: {ARQUIVO_CERTIFICADO}")
        response_cliente = supabase.table("clientes").select("*").eq("id", dados.cliente_id).execute()
        if not response_cliente.data:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        cliente = response_cliente.data[0]

        codigo_ibge = cliente.get('codigo_ibge')
        if not codigo_ibge:
            codigo_ibge = geradorNF.buscar_codigo_ibge(cliente.get('uf'), cliente.get('municipio'))
            if not codigo_ibge:
                codigo_ibge = "5209903"

        numero_rps = int(time.time())
        data_hoje = datetime.now().strftime('%Y-%m-%d')

        xml_string = geradorNF.gerar_xml_centi(
            rps_numero=numero_rps,
            dados_cliente=cliente,
            discriminacao=dados.discriminacao,
            valor_total=dados.valor_servico,
            data_emissao=data_hoje,
            codigo_ibge_resolvido=codigo_ibge,
            caminho_pfx=ARQUIVO_CERTIFICADO,
            senha_pfx=SENHA_CERTIFICADO
        )

        if not xml_string["sucesso"]:
            print("XML INVÁLIDO — NÃO ENVIAR À CENTI:")
            for e in xml_string["erros"]:
                print(" -", e)
                print(xml_string["xml"])
        else:
            print(xml_string["xml"]) 
            xml = xml_string["xml"]

        url_centi = "https://api.centi.com.br/nfe/gerar/go/iaciara"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload_centi = {
            "xml": xml,
            "usuario": USUARIO_CENTI,
            "senha": SENHA_CENTI
        }

        req_centi = requests.post(
            url_centi,
            json=payload_centi,
            headers=headers,
            timeout=30
        )

        response_text = req_centi.text

        if "<html" in response_text.lower() or "request rejected" in response_text.lower():
            raise HTTPException(status_code=403, detail="Firewall da Centi bloqueou a requisição (WAF)")

        if req_centi.status_code != 200:
            raise HTTPException(status_code=500, detail=f"Erro HTTP {req_centi.status_code}: {response_text}")

        if "MensagemRetorno" in response_text and "<Numero>" not in response_text:
            raise HTTPException(status_code=400, detail=f"Centi rejeitou: {response_text}")

        if "<Numero>" not in response_text and "<Protocolo>" not in response_text:
             raise HTTPException(status_code=500, detail=f"Resposta desconhecida: {response_text}")

        supabase.table("ordens_servico").update({"status": "billed"}).eq("id", dados.ordem_id).execute()

        return {
            "mensagem": "Nota Emitida com Sucesso",
            "centi_response": response_text,
            "ibge_utilizado": codigo_ibge
        }

    except requests.exceptions.Timeout:
        raise HTTPException(status_code=504, detail="Timeout ao conectar com a Centi")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/auth/login")
def login(dados: LoginRequest):
    try:
        response = supabase.table("usuarios").select("*").eq("usuario", dados.usuario).execute()
        
        user = response.data[0] if response.data else None

        if not user or user['senha'] != dados.senha:
            raise HTTPException(status_code=401, detail="Credenciais inválidas")

        return {
            "id": user['id'],
            "usuario": user['usuario'],
            "nome": user.get('nome', dados.usuario),
            "token": "session-active" 
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))