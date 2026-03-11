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
    if not b64_data: return None, None
    try:
        pfx_data = base64.b64decode(b64_data)
        with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as temp_pfx:
            temp_pfx.write(pfx_data); temp_pfx_path = temp_pfx.name
        cert_pem = subprocess.run(["openssl", "pkcs12", "-in", temp_pfx_path, "-nokeys", "-passin", f"pass:{senha}"], capture_output=True, check=True).stdout
        key_pem = subprocess.run(["openssl", "pkcs12", "-in", temp_pfx_path, "-nocerts", "-nodes", "-passin", f"pass:{senha}"], capture_output=True, check=True).stdout
        os.unlink(temp_pfx_path)
        return cert_pem, key_pem
    except: return None, None

def calcular_dv(chave_43):
    pesos = [2, 3, 4, 5, 6, 7, 8, 9]
    soma = sum(int(char) * pesos[i % len(pesos)] for i, char in enumerate(reversed(chave_43)))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto

def gerar_chave_acesso(uf, data, cnpj, serie, numero):
    ano_mes = data[2:4] + data[5:7]
    cnf_random = str(random.randint(10000000, 99999999))
    chave_parcial = f"{uf}{ano_mes}{cnpj}55{str(serie).zfill(3)}{str(numero).zfill(9)}1{cnf_random}"
    dv = calcular_dv(chave_parcial)
    return f"{chave_parcial}{dv}", cnf_random, dv

class NFeBuilder:
    def validar_com_xsd(self, xml_element, xsd_path="nfe_v4.00.xsd"):
        try:
            with open(xsd_path, 'rb') as f:
                schema_root = etree.XML(f.read())
                schema = etree.XMLSchema(schema_root)
            schema.assertValid(xml_element)
            return True, ""
        except Exception as e:
            return False, str(e)

    def montar_nfe(self, dados):
        dh_emi = dados["data_emissao"]
        if "T" not in dh_emi:
            dh_emi += "T10:00:00-03:00"
            
        chave, cnf, dv = gerar_chave_acesso("52", dh_emi, PRESTADOR_CNPJ, "1", dados["rps_numero"])
        root = etree.Element(f"{{{NFE_NAMESPACE}}}NFe", nsmap=NS_MAP)
        infNFe = etree.SubElement(root, f"{{{NFE_NAMESPACE}}}infNFe", versao="4.00", Id=f"NFe{chave}")
        
        ide = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}ide")
        for tag, val in [("cUF", "52"), ("cNF", cnf), ("natOp", "VENDAS"), ("mod", "55"), ("serie", "1"), ("nNF", str(dados["rps_numero"])), ("dhEmi", dh_emi), ("tpNF", "1"), ("idDest", "1"), ("cMunFG", "5209903"), ("tpImp", "1"), ("tpEmis", "1"), ("cDV", str(dv)), ("tpAmb", "2"), ("finNFe", "1"), ("indFinal", "1"), ("indPres", "1"), ("indIntermed", "0"), ("procEmi", "0"), ("verProc", "1.0")]:
            etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        
        emit = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}emit")
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CNPJ").text = PRESTADOR_CNPJ
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}xNome").text = "LUCAS ABRAAO NERI DE MELO"
        enderEmit = etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}enderEmit")
        for tag, val in [("xLgr", "AV 21 DE ABRIL"), ("n", "SN"), ("xBairro", "SOLON AMARAL"), ("cMun", "5209903"), ("xMun", "Iaciara"), ("UF", "GO"), ("CEP", "73920000"), ("cPais", "1058"), ("xPais", "BRASIL")]:
            etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}IE").text = PRESTADOR_IE
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CRT").text = "1"
        
        dest = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}dest")
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}{'CPF' if len(dados['documento_tomador'])==11 else 'CNPJ'}").text = dados["documento_tomador"]
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}xNome").text = normalizar_texto(dados["nome"][:60])
        enderDest = etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}enderDest")
        for tag, val in [("xLgr", normalizar_texto(dados["endereco"])), ("n", dados["numero"]), ("xBairro", normalizar_texto(dados["bairro"])), ("cMun", dados["codigo_ibge"]), ("xMun", "IACIARA"), ("UF", dados["uf"]), ("CEP", dados["cep"]), ("cPais", "1058"), ("xPais", "BRASIL")]:
            etree.SubElement(enderDest, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}indIEDest").text = "9"
        
        det = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}det", nItem="1")
        prod = etree.SubElement(det, f"{{{NFE_NAMESPACE}}}prod")
        for tag, val in [("cProd", "000"), ("cEAN", "SEM GTIN"), ("xProd", "FORRO PVC 10MM"), ("NCM", "39162000"), ("CFOP", "5102"), ("uCom", "MT"), ("qCom", "28.0000"), ("vUnCom", "50.0000"), ("vProd", f"{dados['valor_total']:.2f}"), ("cEANTrib", "SEM GTIN"), ("uTrib", "MT"), ("qTrib", "28.0000"), ("vUnTrib", "50.0000"), ("indTot", "1")]:
            etree.SubElement(prod, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        
        imp = etree.SubElement(det, f"{{{NFE_NAMESPACE}}}imposto")
        icms = etree.SubElement(imp, f"{{{NFE_NAMESPACE}}}ICMS")
        sn = etree.SubElement(icms, f"{{{NFE_NAMESPACE}}}ICMSSN102")
        etree.SubElement(sn, f"{{{NFE_NAMESPACE}}}orig").text = "0"
        etree.SubElement(sn, f"{{{NFE_NAMESPACE}}}CSOSN").text = "102"
        
        pis = etree.SubElement(imp, f"{{{NFE_NAMESPACE}}}PIS")
        pis_nt = etree.SubElement(pis, f"{{{NFE_NAMESPACE}}}PISNT")
        etree.SubElement(pis_nt, f"{{{NFE_NAMESPACE}}}CST").text = "07"
        
        cofins = etree.SubElement(imp, f"{{{NFE_NAMESPACE}}}COFINS")
        cofins_nt = etree.SubElement(cofins, f"{{{NFE_NAMESPACE}}}COFINSNT")
        etree.SubElement(cofins_nt, f"{{{NFE_NAMESPACE}}}CST").text = "07"
        
        tot = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}total")
        ict = etree.SubElement(tot, f"{{{NFE_NAMESPACE}}}ICMSTot")
        campos_tot = ["vBC", "vICMS", "vICMSDeson", "vFCP", "vBCST", "vST", "vFCPST", "vFCPSTRet", "vProd", "vFrete", "vSeg", "vDesc", "vII", "vIPI", "vIPIDevol", "vPIS", "vCOFINS", "vOutro", "vNF", "vTotTrib", "vFCPUFDest", "vICMSUFDest", "vICMSUFRemet"]
        for f in campos_tot:
            val = f"{dados['valor_total']:.2f}" if f in ["vProd", "vNF"] else "0.00"
            etree.SubElement(ict, f"{{{NFE_NAMESPACE}}}{f}").text = val
        
        transp = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}transp")
        etree.SubElement(transp, f"{{{NFE_NAMESPACE}}}modFrete").text = "9"
        
        pag = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}pag")
        dpag = etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}detPag")
        etree.SubElement(dpag, f"{{{NFE_NAMESPACE}}}tPag").text = "01"
        etree.SubElement(dpag, f"{{{NFE_NAMESPACE}}}vPag").text = f"{dados['valor_total']:.2f}"
        etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}vTroco").text = "0.00"
        
        self.root = root
        return infNFe.get("Id")

    def assinar_e_transmitir(self, cert_pem, key_pem, nfe_id):
        signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha256", digest_algorithm="sha256")
        signed = signer.sign(self.root, key=key_pem, cert=cert_pem, reference_uri=f"#{nfe_id}")
        
        valido, erro_msg = self.validar_com_xsd(signed)
        if not valido:
            raise Exception(f"Erro de Schema detectado localmente: {erro_msg}")

        envio = etree.Element(f"{{{NFE_NAMESPACE}}}enviNFe", nsmap=NS_MAP, versao="4.00")
        etree.SubElement(envio, f"{{{NFE_NAMESPACE}}}idLote").text = "1"
        etree.SubElement(envio, f"{{{NFE_NAMESPACE}}}indSinc").text = "1"
        envio.append(signed)
        
        xml_final = etree.tostring(envio, encoding="unicode")
        wsdl_ns = "http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4"
        soap = f'<soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><nfeDadosMsg xmlns="{wsdl_ns}">{xml_final}</nfeDadosMsg></soap12:Body></soap12:Envelope>'
        
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as c, tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as k:
            c.write(cert_pem); k.write(key_pem); cp, kp = c.name, k.name
        
        res = requests.post(URL_SEFAZ, data=soap, headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, cert=(cp, kp), timeout=30)
        os.unlink(cp); os.unlink(kp)
        return res.text

def gerar_xml_centi(rps_numero, dados_cliente, discriminacao, valor_total, data_emissao, codigo_ibge_resolvido, caminho_pfx, senha_pfx):
    cert, key = carregar_certificado(caminho_pfx, senha_pfx)
    if not cert: return {"sucesso": False, "erros": ["Falha no certificado"]}
    doc = dados_cliente.get("documento", "").replace(".", "").replace("-", "").replace("/", "")
    builder = NFeBuilder()
    nfe_id = builder.montar_nfe({"rps_numero": rps_numero, "valor_total": valor_total, "data_emissao": data_emissao, "codigo_ibge": codigo_ibge_resolvido, "documento_tomador": doc, "nome": dados_cliente.get("nome"), "endereco": dados_cliente.get("endereco"), "numero": dados_cliente.get("numero") or "SN", "bairro": dados_cliente.get("bairro"), "uf": dados_cliente.get("uf"), "cep": dados_cliente.get("cep", "").replace("-", "")})
    try:
        resultado = builder.assinar_e_transmitir(cert, key, nfe_id)
        return {"sucesso": True, "xml": resultado}
    except Exception as e: return {"sucesso": False, "erros": [str(e)]}

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