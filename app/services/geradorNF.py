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
import random

PRESTADOR_CNPJ = "55952245000100"
PRESTADOR_IE = "201690195"
NFE_NAMESPACE = "http://www.portalfiscal.inf.br/nfe"
URL_SEFAZ = "https://homolog.sefaz.go.gov.br/nfe/services/NFeAutorizacao4"
NS_MAP = {None: NFE_NAMESPACE}

def normalizar_texto(texto):
    if not texto: return ""
    return ''.join(c for c in unicodedata.normalize('NFD', str(texto))
                   if unicodedata.category(c) != 'Mn')

def carregar_certificado(caminho_dummy, senha):
    b64_data = os.getenv("CERTIFICADO_BASE64")
    if not b64_data:
        return None, None
    try:
        pfx_data = base64.b64decode(b64_data)
        with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as temp_pfx:
            temp_pfx.write(pfx_data)
            temp_pfx_path = temp_pfx.name
        cmd_cert = ["openssl", "pkcs12", "-in", temp_pfx_path, "-nokeys", "-passin", f"pass:{senha}"]
        cert_pem = subprocess.run(cmd_cert, capture_output=True, check=True).stdout
        cmd_key = ["openssl", "pkcs12", "-in", temp_pfx_path, "-nocerts", "-nodes", "-passin", f"pass:{senha}"]
        key_pem = subprocess.run(cmd_key, capture_output=True, check=True).stdout
        os.unlink(temp_pfx_path)
        return cert_pem, key_pem
    except:
        return None, None

def calcular_dv(chave_43):
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = 0
    for i, char in enumerate(reversed(chave_43)):
        soma += int(char) * pesos[i % len(pesos)]
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto

def gerar_chave_acesso(uf, data, cnpj, serie, numero):
    ano_mes = data[2:4] + data[5:7]
    modelo = "55"
    serie_format = str(serie).zfill(3)
    numero_format = str(numero).zfill(9)
    tipo_emissao = "1"
    codigo_num = str(random.randint(10000000, 99999999))
    chave_parcial = f"{uf}{ano_mes}{cnpj}{modelo}{serie_format}{numero_format}{tipo_emissao}{codigo_num}"
    dv = calcular_dv(chave_parcial)
    return f"{chave_parcial}{dv}", codigo_num, dv

class NFeBuilder:
    def __init__(self):
        self.root = None

    def montar_nfe(self, dados):
        chave, cnf, dv = gerar_chave_acesso("52", dados["data_emissao"], PRESTADOR_CNPJ, "1", dados["rps_numero"])
        self.root = etree.Element(f"{{{NFE_NAMESPACE}}}NFe", nsmap=NS_MAP)
        infNFe = etree.SubElement(self.root, f"{{{NFE_NAMESPACE}}}infNFe")
        infNFe.set("versao", "4.00")
        infNFe.set("Id", f"NFe{chave}")
        ide = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}ide")
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}cUF").text = "52"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}cNF").text = cnf
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}natOp").text = "VENDAS"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}mod").text = "55"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}serie").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}nNF").text = str(dados["rps_numero"])
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}dhEmi").text = dados["data_emissao"]
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}tpNF").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}idDest").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}cMunFG").text = "5209707"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}tpImp").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}tpEmis").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}cDV").text = str(dv)
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}tpAmb").text = "2"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}finNFe").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}indFinal").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}indPres").text = "1"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}procEmi").text = "0"
        etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}verProc").text = "1.0"
        emit = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}emit")
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CNPJ").text = PRESTADOR_CNPJ
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}xNome").text = "WILMANIO VIEIRA DE MELO-ME"
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}IE").text = PRESTADOR_IE
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CRT").text = "1"
        enderEmit = etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}enderEmit")
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}xLgr").text = "AV 21 DE ABRIL"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}n").text = "01"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}xBairro").text = "SOLON AMARAL"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}cMun").text = "5209707"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}xMun").text = "Iaciara"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}UF").text = "GO"
        etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}CEP").text = "73920000"
        dest = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}dest")
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}CPF").text = dados["documento_tomador"]
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}xNome").text = dados["nome"]
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}indIEDest").text = "9"
        enderDest = etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}enderDest")
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}xLgr").text = dados["endereco"]
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}n").text = dados["numero"]
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}xBairro").text = dados["bairro"]
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}cMun").text = dados["codigo_ibge"]
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}xMun").text = "IACIARA"
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}UF").text = dados["uf"]
        etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}CEP").text = dados["cep"]
        det = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}det")
        det.set("nItem", "1")
        prod = etree.SubElement(det, f"{{{NFE_NAMESPACE}}}prod")
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}cProd").text = "000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}cEAN").text = "SEM GTIN"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}xProd").text = "FORRO PVC 10MM"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}NCM").text = "39162000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}CFOP").text = "5102"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}uCom").text = "MT"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}qCom").text = "28.0000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}vUnCom").text = "50.0000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}vProd").text = f"{dados['valor_total']:.2f}"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}cEANTrib").text = "SEM GTIN"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}uTrib").text = "MT"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}qTrib").text = "28.0000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}vUnTrib").text = "50.0000"
        etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}indTot").text = "1"
        imposto = etree.SubElement(det, f"{{{NFE_NAMESPACE}}}imposto")
        icms = etree.SubElement(imposto, f"{{{NFE_NAMESPACE}}}ICMS")
        icms_sn = etree.SubElement(icms, f"{{{NFE_NAMESPACE}}}ICMSSN102")
        etree.SubElement(icms_sn, f"{{{NFE_NAMESPACE}}}orig").text = "0"
        etree.SubElement(icms_sn, f"{{{NFE_NAMESPACE}}}CSOSN").text = "102"
        total = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}total")
        icms_tot = etree.SubElement(total, f"{{{NFE_NAMESPACE}}}ICMSTot")
        for f in ["vBC", "vICMS", "vICMSDeson", "vFCP", "vBCST", "vST", "vFCPST", "vFCPSTRet", "vProd", "vFrete", "vSeg", "vDesc", "vII", "vIPI", "vIPIDevol", "vPIS", "vCOFINS", "vOutro", "vNF"]:
            etree.SubElement(icms_tot, f"{{{NFE_NAMESPACE}}}{f}").text = f"{dados['valor_total']:.2f}" if f in ["vProd", "vNF"] else "0.00"
        transp = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}transp")
        etree.SubElement(transp, f"{{{NFE_NAMESPACE}}}modFrete").text = "9"
        pag = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}pag")
        detPag = etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}detPag")
        etree.SubElement(detPag, f"{{{NFE_NAMESPACE}}}tPag").text = "01"
        etree.SubElement(detPag, f"{{{NFE_NAMESPACE}}}vPag").text = f"{dados['valor_total']:.2f}"
        return infNFe.get("Id")

    def assinar_e_transmitir(self, cert_pem, key_pem, nfe_id):
        signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha1", digest_algorithm="sha1", c14n_algorithm="http://www.w3.org/TR/2001/REC-xml-c14n-20010315")
        signed_nfe = signer.sign(self.root, key=key_pem, cert=cert_pem, reference_uri=f"#{nfe_id}")
        xml_assinado = etree.tostring(signed_nfe, encoding="unicode")
        
        envio = etree.Element(f"{{{NFE_NAMESPACE}}}enviNFe", nsmap=NS_MAP, versao="4.00")
        etree.SubElement(envio, f"{{{NFE_NAMESPACE}}}idLote").text = "1"
        etree.SubElement(envio, f"{{{NFE_NAMESPACE}}}indSinc").text = "1"
        envio.append(signed_nfe)
        xml_final = etree.tostring(envio, encoding="unicode")

        soap = f"""<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
            <soap12:Body>
                <nfeDadosMsg xmlns="{NFE_NAMESPACE}">{xml_final}</nfeDadosMsg>
            </soap12:Body>
        </soap12:Envelope>"""

        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as c_file, tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as k_file:
            c_file.write(cert_pem); k_file.write(key_pem)
            c_path = c_file.name; k_path = k_file.name
        
        response = requests.post(URL_SEFAZ, data=soap, headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, cert=(c_path, k_path), timeout=30)
        os.unlink(c_path); os.unlink(k_path)
        return response.text

def gerar_xml_centi(rps_numero, dados_cliente, discriminacao, valor_total, data_emissao, codigo_ibge_resolvido, caminho_pfx, senha_pfx):
    cert, key = carregar_certificado(caminho_pfx, senha_pfx)
    if not cert: return {"sucesso": False, "erros": ["Falha no certificado"]}
    doc = dados_cliente.get("documento", "").replace(".", "").replace("-", "").replace("/", "")
    builder = NFeBuilder()
    nfe_id = builder.montar_nfe({"rps_numero": rps_numero, "valor_total": valor_total, "data_emissao": data_emissao, "codigo_ibge": codigo_ibge_resolvido, "documento_tomador": doc, "nome": dados_cliente.get("nome"), "endereco": dados_cliente.get("endereco"), "numero": dados_cliente.get("numero") or "SN", "bairro": dados_cliente.get("bairro"), "uf": dados_cliente.get("uf"), "cep": dados_cliente.get("cep", "").replace("-", "")})
    try:
        resultado_sefaz = builder.assinar_e_transmitir(cert, key, nfe_id)
        return {"sucesso": True, "xml": resultado_sefaz}
    except Exception as e:
        return {"sucesso": False, "erros": [str(e)]}

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