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

class OrcamentoBody(BaseModel):
    cliente_id: int
    valor_total: float
    items: Optional[List[ItemOrdemSchema]] = []

class ProdutoCreate(BaseModel):
    cst: str
    cfop: str
    descricao: str
    unid: str

class ParcelaBody(BaseModel):
    valor: float
    data_vencimento: str
    status: str = 'pendente'

class PromissoriaBody(BaseModel):
    cliente_id: int
    produto_id: int
    valor_unitario: float
    quantidade: float
    valor_total: float
    num_parcelas: int
    primeiro_vencimento: str
    parcelas: List[ParcelaBody] = []

class ParcelaUpdateStatus(BaseModel):
    status: str

@router.get("/clientes")
def get_clientes():
    response = supabase.table("clientes").select("*").execute()
    return response.data

@router.post("/clientes")
def create_cliente(cliente: ClienteCreate):
    try:
        data = cliente.dict()
        
        if "id" in data:
            del data["id"]
            
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

@router.get("/produtos")
def get_produtos():
    try:
        response = supabase.table("produtos").select("*").execute()
        data = response.data
        for item in data:
            if item.get('unid'):
                hex_val = item['unid'].replace('\\x', '')
                try:
                    item['unid'] = bytes.fromhex(hex_val).decode('utf-8')
                except:
                    pass
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/produtos")
def create_produto(produto: ProdutoCreate):
    try:
        data = produto.dict()
        if data.get('unid'):
            data['unid'] = '\\x' + data['unid'].encode('utf-8').hex()
        response = supabase.table("produtos").insert(data).execute()
        if response.data:
            return response.data[0]
        raise HTTPException(status_code=500, detail="Erro ao inserir")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/produtos/{produto_id}")
def update_produto(produto_id: int, produto: ProdutoCreate):
    try:
        data = produto.dict()
        if data.get('unid'):
            data['unid'] = '\\x' + data['unid'].encode('utf-8').hex()
        response = supabase.table("produtos").update(data).eq("id", produto_id).execute()
        if response.data:
            return {"message": "Produto atualizado"}
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/produtos/{produto_id}")
def delete_produto(produto_id: int):
    try:
        response = supabase.table("produtos").delete().eq("id", produto_id).execute()
        if response.data:
            return {"message": "Produto excluído"}
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/ordens")
def get_ordens():
    try:
        response = supabase.table("ordens_servico").select("*, clientes(nome), itens_ordem(*)").order("data_abertura", desc=True).execute()
        return response.data
    except Exception as e:
        print(f"Erro Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar ordens: {str(e)}")
    
@router.post("/ordens")
def create_ordem(ordem: OrdemServicoCreate):
    try:
        order_data = ordem.dict()
        order_data.pop("id", None)
        items = order_data.pop("items", [])
        
        res_ordem = supabase.table("ordens_servico").insert(order_data).execute()
        if not res_ordem.data:
            raise HTTPException(status_code=500, detail="Erro ao criar ordem")
            
        new_order_id = res_ordem.data[0]['id']

        if items:
            items_data = []
            for item in items:
                item.pop("id", None)
                items_data.append({"ordem_id": new_order_id, **item})
            supabase.table("itens_ordem").insert(items_data).execute()

        return {"message": "Ordem criada", "id": new_order_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/ordens/{order_id}")
def update_ordem(order_id: int, ordem: OrdemServicoCreate):
    try:
        update_data = {
            "cliente_id": ordem.cliente_id,
            "valor_total": ordem.valor_total,
            "observacoes": ordem.observacoes,
            "status": ordem.status,
            "desconto": ordem.dict().get("desconto", 0),
            "nf_emitida": ordem.dict().get("nf_emitida", False),
            "link_nf": ordem.dict().get("link_nf", "")
        }
        
        supabase.table("ordens_servico").update(update_data).eq("id", order_id).execute()

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

@router.get("/orcamentos")
def get_orcamentos():
    try:
        response = supabase.table("orcamentos").select("*, clientes(nome)").order("id", desc=True).execute()
        if response.data is None:
            return []
        
        data = response.data
        for item in data:
            if 'items' in item and item['items'] is not None:
                item['itens_orcamento'] = item['items']
        return data
    except Exception as e:
        print(f"Erro Supabase: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao buscar orçamentos: {str(e)}")

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

@router.post("/despesas")
def criar_despesa(despesa: DespesaCreate):
    try:
        dados = {
            "descricao": despesa.descricao,
            "valor": despesa.valor,
            "tipo": despesa.categoria if hasattr(despesa, 'categoria') else "Outros", 
            "data_cadastro": despesa.data,
            "fixa": despesa.fixa
        }
        response = supabase.table("despesas").insert(dados).execute()
        if not response.data:
            raise HTTPException(status_code=400, detail="Erro ao salvar despesa")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.post("/nfe/emitir")
def emitir_nota_fiscal(dados: EmissaoNotaRequest):
    try:
        ARQUIVO_CERTIFICADO = os.getenv("CERT_PATH", "etc/secrets/LUCASABRAAONERIDEMELO55952245000100.pfx")
        SENHA_CERTIFICADO = "123456"
        
        response_cliente = supabase.table("clientes").select("*").eq("id", dados.cliente_id).execute()
        if not response_cliente.data:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")

        cliente = response_cliente.data[0]

        codigo_ibge = cliente.get('codigo_ibge')
        if not codigo_ibge:
            codigo_ibge = geradorNF.buscar_codigo_ibge(cliente.get('uf'), cliente.get('municipio'))
            if not codigo_ibge:
                codigo_ibge = "5209903"

        response_ordem = supabase.table("ordens_servico").select("*, itens_ordem(*)").eq("id", dados.ordem_id).execute()
        if not response_ordem.data:
            raise HTTPException(status_code=404, detail="Ordem de Serviço não encontrada")
            
        ordem = response_ordem.data[0]
        itens_ordem = ordem.get("itens_ordem", [])
        
        if not itens_ordem:
            raise HTTPException(status_code=400, detail="A Ordem de Serviço não possui itens.")
            
        itens_nfe = []
        for i, item in enumerate(itens_ordem):
            cfop = "5102"
            cst = "102"
            unid = item.get("unid", "UN")
            produto_id = item.get("produto_id") or item.get("servico_id")
            
            if produto_id:
                resp_prod = supabase.table("produtos").select("*").eq("id", produto_id).execute()
                if resp_prod.data:
                    prod = resp_prod.data[0]
                    cfop = prod.get("cfop") or "5102"
                    cst = prod.get("cst") or "102"
                    if not item.get("unid"):
                        hex_val = (prod.get('unid') or '').replace('\\x', '')
                        if hex_val:
                            try:
                                unid = bytes.fromhex(hex_val).decode('utf-8')
                            except:
                                unid = "UN"

            qtd_nfe = float(item.get("m2", 0)) if unid == 'MT²' else float(item.get("quantidade", 1))

            itens_nfe.append({
                "nItem": str(i + 1),
                "descricao": item.get("descricao_item", "Item sem descrição"),
                "quantidade": qtd_nfe,
                "valor_unitario": item.get("valor_unitario", 0),
                "cfop": cfop,
                "cst": cst,
                "unid": unid
            })

        numero_nfe = int(time.time()) % 1000000000
        data_emissao = datetime.now().strftime('%Y-%m-%dT%H:%M:%S-03:00')

        resultado_emissao = geradorNF.gerar_xml_centi(
            rps_numero=numero_nfe,
            dados_cliente=cliente,
            discriminacao=dados.discriminacao,
            valor_total=dados.valor_servico,
            data_emissao=data_emissao,
            codigo_ibge_resolvido=codigo_ibge,
            caminho_pfx=ARQUIVO_CERTIFICADO,
            senha_pfx=SENHA_CERTIFICADO,
            itens=itens_nfe
        )

        if not resultado_emissao["sucesso"]:
            raise HTTPException(status_code=500, detail=f"Erro na geração/assinatura: {resultado_emissao['erros']}")

        sefaz_response = resultado_emissao["xml"]

        if "<cStat>100</cStat>" not in sefaz_response:
            raise HTTPException(
                status_code=400, 
                detail=f"SEFAZ não autorizou a nota. Resposta: {sefaz_response}"
            )

        supabase.table("ordens_servico").update({"status": "billed"}).eq("id", dados.ordem_id).execute()

        return {
            "mensagem": "Nota Fiscal de Produto Emitida e Autorizada",
            "protocolo_sefaz": sefaz_response,
            "chave_acesso": numero_nfe,
            "ambiente": "Produção"
        }

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

@router.get("/promissorias")
def get_promissorias():
    try:
        response = supabase.table("promissorias").select("*, parcelas:promissorias_parcelas(*), clientes(nome), produtos(descricao)").order("id", desc=True).execute()
        return response.data if response.data else []
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/promissorias")
def create_promissoria(promissoria: PromissoriaBody):
    try:
        promissoria_data = {
            "cliente_id": promissoria.cliente_id,
            "produto_id": promissoria.produto_id,
            "valor_unitario": promissoria.valor_unitario,
            "quantidade": promissoria.quantidade,
            "valor_total": promissoria.valor_total,
            "num_parcelas": promissoria.num_parcelas,
            "primeiro_vencimento": promissoria.primeiro_vencimento
        }
        
        res_prom = supabase.table("promissorias").insert(promissoria_data).execute()
        if not res_prom.data:
            raise HTTPException(status_code=500, detail="Erro ao criar promissória")
            
        new_id = res_prom.data[0]['id']

        if promissoria.parcelas:
            parcelas_data = [
                {
                    "promissoria_id": new_id,
                    "valor": p.valor,
                    "data_vencimento": p.data_vencimento,
                    "status": p.status
                } for p in promissoria.parcelas
            ]
            supabase.table("promissorias_parcelas").insert(parcelas_data).execute()

        return {"message": "Promissória criada", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/promissorias/parcelas/{parcela_id}")
def update_parcela_status(parcela_id: int, status_update: ParcelaUpdateStatus):
    try:
        response = supabase.table("promissorias_parcelas").update({"status": status_update.status}).eq("id", parcela_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="Parcela não encontrada")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.put("/promissorias/{promissoria_id}")
def update_promissoria(promissoria_id: int, promissoria: PromissoriaBody):
    try:
        update_data = {
            "cliente_id": promissoria.cliente_id,
            "produto_id": promissoria.produto_id,
            "valor_unitario": promissoria.valor_unitario,
            "quantidade": promissoria.quantidade,
            "valor_total": promissoria.valor_total,
            "num_parcelas": promissoria.num_parcelas,
            "primeiro_vencimento": promissoria.primeiro_vencimento
        }

        supabase.table("promissorias").update(update_data).eq("id", promissoria_id).execute()
        supabase.table("promissorias_parcelas").delete().eq("promissoria_id", promissoria_id).execute()

        if promissoria.parcelas:
            parcelas_data = [
                {
                    "promissoria_id": promissoria_id,
                    "valor": p.valor,
                    "data_vencimento": p.data_vencimento,
                    "status": p.status
                } for p in promissoria.parcelas
            ]
            supabase.table("promissorias_parcelas").insert(parcelas_data).execute()

        return {"message": "Promissória atualizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/promissorias/{promissoria_id}")
def delete_promissoria(promissoria_id: int):
    try:
        response = supabase.table("promissorias").delete().eq("id", promissoria_id).execute()
        if response.data:
            return {"message": "Promissória excluída"}
        raise HTTPException(status_code=404, detail="Promissória não encontrada")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))