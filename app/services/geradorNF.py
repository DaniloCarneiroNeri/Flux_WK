from lxml import etree
import unicodedata
import requests
from signxml import XMLSigner, methods
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import serialization
import base64
import os
import subprocess
import tempfile

# --- CONFIGURAÇÕES ---
PRESTADOR_CNPJ = "39623105000132"
PRESTADOR_IM = "890455"
CODIGO_SERVICO = "85"
CNAE = "2539001"
ALIQUOTA = 2.00
CENTI_NAMESPACE = "http://www.centi.com.br/files/nfse.xsd"

NS_MAP = {None: CENTI_NAMESPACE}

def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                   if unicodedata.category(c) != 'Mn')

def carregar_certificado(caminho_dummy, senha):
    print("Iniciando carregamento via BASE64 (Método Blindado)...")
    
    b64_data = os.getenv("CERTIFICADO_BASE64")
    if not b64_data:
        print("ERRO: Variável CERTIFICADO_BASE64 não encontrada ou vazia!")
        return None, None

    try:
        pfx_data = base64.b64decode(b64_data)
        
        with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as temp_pfx:
            temp_pfx.write(pfx_data)
            temp_pfx_path = temp_pfx.name
        
        print(f"Arquivo temporário criado em: {temp_pfx_path}")

        cmd_cert = [
            "openssl", "pkcs12", 
            "-in", temp_pfx_path, 
            "-nokeys", 
            "-passin", f"pass:{senha}"
        ]
        cert_pem = subprocess.run(cmd_cert, capture_output=True, check=True).stdout

        cmd_key = [
            "openssl", "pkcs12", 
            "-in", temp_pfx_path, 
            "-nocerts", 
            "-nodes", 
            "-passin", f"pass:{senha}"
        ]
        key_pem = subprocess.run(cmd_key, capture_output=True, check=True).stdout

        os.unlink(temp_pfx_path)

        print("SUCESSO! Certificado reconstruído e lido corretamente.")
        return cert_pem, key_pem

    except Exception as e:
        print(f"Erro fatal no método Base64: {e}")
        if 'cmd_cert' in locals() and isinstance(e, subprocess.CalledProcessError):
             print(f"Stderr: {e.stderr.decode('utf-8', errors='ignore')}")
        return None, None

class CentiNFSeBuilder:
    def __init__(self):
        self.rps_element = None 
        self.root = None

    def _add(self, parent, tag_name, value):
        el = etree.SubElement(parent, f"{{{CENTI_NAMESPACE}}}{tag_name}")
        el.text = str(value) if value is not None else ""
        return el

    def montar_rps_separado(self, dados):
        self.rps_element = etree.Element(f"{{{CENTI_NAMESPACE}}}Rps", nsmap=NS_MAP)
        
        inf = etree.SubElement(self.rps_element, f"{{{CENTI_NAMESPACE}}}InfDeclaracaoPrestacaoServico")
        
        rps_inner = etree.SubElement(inf, f"{{{CENTI_NAMESPACE}}}Rps")
        
        # Define o ID no Rps interno
        rps_id_val = f"RPS{dados['rps_numero']}"
        rps_inner.set("Id", rps_id_val)
        
        # --- Preenchimento dos dados do RPS Interno ---
        ident = etree.SubElement(rps_inner, f"{{{CENTI_NAMESPACE}}}IdentificacaoRps")
        self._add(ident, "Numero", dados["rps_numero"])
        self._add(ident, "Serie", "2")
        self._add(ident, "Tipo", "1")

        self._add(rps_inner, "DataEmissao", dados["data_emissao"])
        self._add(rps_inner, "Status", "1")

        # --- Continuação dos dados em InfDeclaracao (Irmãos do Rps interno) ---
        self._add(inf, "Competencia", dados["data_emissao"].split('T')[0])

        # Serviço
        servico = etree.SubElement(inf, f"{{{CENTI_NAMESPACE}}}Servico")
        valores = etree.SubElement(servico, f"{{{CENTI_NAMESPACE}}}Valores")
        self._add(valores, "ValorServicos", f"{dados['valor_total']:.2f}")
        self._add(valores, "ValorDeducoes", "0.00")
        self._add(valores, "ValorPis", "0.00")
        self._add(valores, "ValorCofins", "0.00")
        self._add(valores, "ValorInss", "0.00")
        self._add(valores, "ValorIr", "0.00")
        self._add(valores, "ValorCsll", "0.00")
        self._add(valores, "OutrasRetencoes", "0.00")
        self._add(valores, "ValorIss", f"{dados['valor_iss']:.2f}")
        self._add(valores, "Aliquota", f"{ALIQUOTA:.2f}")
        self._add(valores, "DescontoIncondicionado", "0.00")
        self._add(valores, "DescontoCondicionado", "0.00")

        self._add(servico, "IssRetido", "2")
        self._add(servico, "ResponsavelRetencao", "1")
        self._add(servico, "ItemListaServico", CODIGO_SERVICO)
        #self._add(servico, "CodigoCnae", CNAE)
        #self._add(servico, "CodigoTributacaoMunicipio", dados["codigo_ibge"])
        self._add(servico, "Discriminacao", dados["discriminacao"])
        self._add(servico, "CodigoMunicipio", dados["codigo_ibge"])
        self._add(servico, "CodigoPais", "1058")
        self._add(servico, "ExigibilidadeISS", "1")
        self._add(servico, "MunicipioIncidencia", dados["codigo_ibge"])
        
        # Prestador
        prest = etree.SubElement(inf, f"{{{CENTI_NAMESPACE}}}Prestador")
        pj = etree.SubElement(prest, f"{{{CENTI_NAMESPACE}}}CpfCnpj")
        self._add(pj, "Cnpj", PRESTADOR_CNPJ)
        self._add(prest, "InscricaoMunicipal", PRESTADOR_IM)

        # Tomador
        tom = etree.SubElement(inf, f"{{{CENTI_NAMESPACE}}}Tomador")
        ident_t = etree.SubElement(tom, f"{{{CENTI_NAMESPACE}}}IdentificacaoTomador")
        doc_t = etree.SubElement(ident_t, f"{{{CENTI_NAMESPACE}}}CpfCnpj")
        self._add(doc_t, dados["doc_tipo"], dados["documento_tomador"])
        self._add(tom, "RazaoSocial", dados["nome"])
        
        end = etree.SubElement(tom, f"{{{CENTI_NAMESPACE}}}Endereco")
        self._add(end, "Endereco", dados["endereco"])
        self._add(end, "Numero", dados["numero"])
        self._add(end, "Complemento", dados.get("complemento", ""))
        self._add(end, "Bairro", dados["bairro"])
        self._add(end, "CodigoMunicipio", dados["codigo_ibge"])
        self._add(end, "Uf", dados["uf"])
        self._add(end, "CodigoPais", "1058")
        self._add(end, "Cep", dados["cep"])

        contato = etree.SubElement(tom, f"{{{CENTI_NAMESPACE}}}Contato")
        self._add(contato, "Telefone", dados.get("telefone", ""))
        self._add(contato, "Email", dados.get("email", ""))

        self._add(inf, "OptanteSimplesNacional", "1")
        self._add(inf, "RegimeEspecialTributacao", "6")
        self._add(inf, "IncentivoFiscal", "2")

    def assinar_e_gerar_final(self, cert_pem, key_pem):
        inf = self.rps_element.find(f"{{{CENTI_NAMESPACE}}}InfDeclaracaoPrestacaoServico")
        rps_inner = inf.find(f"{{{CENTI_NAMESPACE}}}Rps")
        rps_id = rps_inner.get("Id")

        rps_tree = etree.ElementTree(self.rps_element)

        signer = XMLSigner(
            method=methods.enveloped,
            signature_algorithm="rsa-sha1",
            digest_algorithm="sha1",
            c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315"
        )

        signed_element = signer.sign(
            rps_tree,
            key=key_pem,
            cert=cert_pem,
            reference_uri=f"#{rps_id}" 
        )

        self.root = etree.Element(f"{{{CENTI_NAMESPACE}}}GerarNfseEnvio", nsmap=NS_MAP)
        
        self.root.append(signed_element)

        xml_str = etree.tostring(self.root, encoding="unicode")

        xml_str = xml_str.replace('xmlns:ds="http://www.w3.org/2000/09/xmldsig#"',
                                'xmlns="http://www.w3.org/2000/09/xmldsig#"')
        xml_str = xml_str.replace('<ds:', '<').replace('</ds:', '</')

        return xml_str

def validar_xml_centi(xml_str):
    try:
        root = etree.fromstring(xml_str.encode('utf-8'))
    except Exception as e:
        return False, [f"Erro ao ler XML gerado: {e}"]

    ns = CENTI_NAMESPACE
    tag = lambda t: f"{{{ns}}}{t}"
    erros = []

    if root.tag != tag("GerarNfseEnvio"):
        erros.append("Tag raiz incorreta (esperado GerarNfseEnvio)")

    rps = root.find(tag("Rps"))
    if rps is None:
        return False, ["<Rps> não encontrado no XML final"]
    
    sig = rps.find(f"{{http://www.w3.org/2000/09/xmldsig#}}Signature")
    if sig is None:
        erros.append("Assinatura digital (<Signature>) NÃO encontrada dentro do <Rps>")

    if erros:
        return False, erros

    return True, None

def gerar_xml_centi(rps_numero, dados_cliente, discriminacao, valor_total, data_emissao, codigo_ibge_resolvido, caminho_pfx, senha_pfx):
    cert, key = carregar_certificado(caminho_pfx, senha_pfx)
    if not cert:
        return {"sucesso": False, "erros": ["Falha ao carregar certificado PFX (Verifique caminho e senha)"]}

    valor_iss = round(valor_total * (ALIQUOTA / 100.0), 2)
    doc_raw = dados_cliente.get("documento", "")
    doc = doc_raw.replace(".", "").replace("-", "").replace("/", "")
    doc_tipo = "Cnpj" if len(doc) > 11 else "Cpf"

    builder = CentiNFSeBuilder()

    builder.montar_rps_separado({
        "rps_numero": rps_numero,
        "valor_total": valor_total,
        "valor_iss": valor_iss,
        "data_emissao": data_emissao,
        "codigo_ibge": codigo_ibge_resolvido,
        "discriminacao": discriminacao,
        "documento_tomador": doc,
        "doc_tipo": doc_tipo,
        "nome": dados_cliente.get("nome"),
        "endereco": dados_cliente.get("endereco"),
        "numero": dados_cliente.get("numero") or "SN",
        "complemento": dados_cliente.get("complemento"),
        "bairro": dados_cliente.get("bairro"),
        "uf": dados_cliente.get("uf"),
        "cep": dados_cliente.get("cep", "").replace("-", ""),
        "telefone": dados_cliente.get("telefone"),
        "email": dados_cliente.get("email")
    })

    try:
        xml = builder.assinar_e_gerar_final(cert, key)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"sucesso": False, "erros": [f"Erro crítico na assinatura: {str(e)}"]}

    return {"sucesso": True, "xml": xml}

# Função auxiliar de busca codigo ibge
def buscar_codigo_ibge(uf, nome_cidade):
    if not uf or not nome_cidade: return None
    try:
        url = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{uf}/municipios"
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            busca = normalizar_texto(nome_cidade).lower()
            for item in res.json():
                if normalizar_texto(item['nome']).lower() == busca: return str(item['id'])
    except: pass
    return None