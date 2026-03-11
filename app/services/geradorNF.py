from lxml import etree
import unicodedata
import requests
from signxml import XMLSigner, methods
import base64
import os
import subprocess
import tempfile
import random
import re

PRESTADOR_CNPJ = "55952245000100"
PRESTADOR_IE = "201690195"
NFE_NAMESPACE = "http://www.portalfiscal.inf.br/nfe"
URL_SEFAZ = "https://homolog.sefaz.go.gov.br/nfe/services/NFeAutorizacao4"
NS_MAP = {None: NFE_NAMESPACE}

def normalizar_texto(texto):
    if not texto: return ""
    texto = str(texto).replace("'", "").replace('"', "")
    return ''.join(c for c in unicodedata.normalize('NFD', texto)
                   if unicodedata.category(c) != 'Mn').strip().upper()

def carregar_certificado(senha):
    b64_data = os.getenv("CERTIFICADO_BASE64")
    if not b64_data: return None, None
    try:
        pfx_data = base64.b64decode(b64_data)
        with tempfile.NamedTemporaryFile(suffix=".pfx", delete=False) as temp_pfx:
            temp_pfx.write(pfx_data)
            temp_pfx_path = temp_pfx.name
        
        cert_raw = subprocess.run(["openssl", "pkcs12", "-in", temp_pfx_path, "-nokeys", "-passin", f"pass:{senha}"], capture_output=True, check=True).stdout
        cert_match = re.search(r"-----BEGIN CERTIFICATE----- (.*?) -----END CERTIFICATE-----", cert_raw.decode().replace('\n', ' '), re.DOTALL)
        cert_b64 = cert_match.group(1).replace(" ", "") if cert_match else ""

        key_pem = subprocess.run(["openssl", "pkcs12", "-in", temp_pfx_path, "-nocerts", "-nodes", "-passin", f"pass:{senha}"], capture_output=True, check=True).stdout
        
        os.unlink(temp_pfx_path)
        return cert_b64.encode(), key_pem
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
    def montar_nfe(self, dados):
        dh_emi = dados["data_emissao"].replace(" ", "T")
        if "T" not in dh_emi: dh_emi += "T10:00:00-03:00"
        elif "-" not in dh_emi[10:] and "+" not in dh_emi[10:]: dh_emi = dh_emi[:19] + "-03:00"
            
        chave, cnf, dv = gerar_chave_acesso("52", dh_emi, PRESTADOR_CNPJ, "1", dados["rps_numero"])
        
        self.root = etree.Element(f"{{{NFE_NAMESPACE}}}NFe", nsmap=NS_MAP)
        infNFe = etree.SubElement(self.root, f"{{{NFE_NAMESPACE}}}infNFe", versao="4.00", Id=f"NFe{chave}")
        
        ide = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}ide")
        tags_ide = [("cUF", "52"), ("cNF", cnf), ("natOp", "VENDAS"), ("mod", "55"), ("serie", "1"), ("nNF", str(dados["rps_numero"])[:9]), ("dhEmi", dh_emi), ("tpNF", "1"), ("idDest", "1"), ("cMunFG", "5209903"), ("tpImp", "1"), ("tpEmis", "1"), ("cDV", str(dv)), ("tpAmb", "2"), ("finNFe", "1"), ("indFinal", "1"), ("indPres", "1"), ("indIntermed", "0"), ("procEmi", "0"), ("verProc", "1.0")]
        for tag, val in tags_ide: etree.SubElement(ide, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        
        emit = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}emit")
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CNPJ").text = PRESTADOR_CNPJ
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}xNome").text = "LUCAS ABRAAO NERI DE MELO"
        enderEmit = etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}enderEmit")
        for tag, val in [("xLgr", "AV 21 DE ABRIL"), ("nro", "SN"), ("xBairro", "SOLON AMARAL"), ("cMun", "5209903"), ("xMun", "IACIARA"), ("UF", "GO"), ("CEP", "73920000"), ("cPais", "1058"), ("xPais", "BRASIL")]:
            etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}IE").text = PRESTADOR_IE
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CRT").text = "1"
        
        dest = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}dest")
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}{'CPF' if len(dados['documento_tomador'])==11 else 'CNPJ'}").text = dados["documento_tomador"]
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}xNome").text = normalizar_texto(dados["nome"])[:60]
        enderDest = etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}enderDest")
        for tag, val in [("xLgr", normalizar_texto(dados["endereco"])[:60]), ("nro", dados["numero"]), ("xBairro", normalizar_texto(dados["bairro"])[:60]), ("cMun", dados["codigo_ibge"]), ("xMun", dados["nome_cidade"]), ("UF", dados["uf"]), ("CEP", dados["cep"]), ("cPais", "1058"), ("xPais", "BRASIL")]:
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
        
        for tag in ["PIS", "COFINS"]:
            sub = etree.SubElement(imp, f"{{{NFE_NAMESPACE}}}{tag}")
            nt = etree.SubElement(sub, f"{{{NFE_NAMESPACE}}}{tag}NT")
            etree.SubElement(nt, f"{{{NFE_NAMESPACE}}}CST").text = "07"
        
        tot = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}total")
        ict = etree.SubElement(tot, f"{{{NFE_NAMESPACE}}}ICMSTot")
        for f in ["vBC", "vICMS", "vICMSDeson", "vFCP", "vBCST", "vST", "vFCPST", "vFCPSTRet", "vProd", "vFrete", "vSeg", "vDesc", "vII", "vIPI", "vIPIDevol", "vPIS", "vCOFINS", "vOutro", "vNF", "vTotTrib"]:
            val = f"{dados['valor_total']:.2f}" if f in ["vProd", "vNF"] else "0.00"
            etree.SubElement(ict, f"{{{NFE_NAMESPACE}}}{f}").text = val
        
        etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}transp").append(etree.Element(f"{{{NFE_NAMESPACE}}}modFrete"))
        infNFe.xpath(".//*[local-name()='modFrete']")[0].text = "9"
        
        pag = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}pag")
        dpag = etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}detPag")
        etree.SubElement(dpag, f"{{{NFE_NAMESPACE}}}tPag").text = "01"
        etree.SubElement(dpag, f"{{{NFE_NAMESPACE}}}vPag").text = f"{dados['valor_total']:.2f}"
        etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}vTroco").text = "0.00"
        
        return infNFe.get("Id")

    def assinar_e_transmitir(self, cert_b64, key_pem, nfe_id):
        signer = XMLSigner(method=methods.enveloped, signature_algorithm="rsa-sha256", digest_algorithm="sha256")
        signed_nfe = signer.sign(self.root, key=key_pem, cert=cert_b64, reference_uri=f"#{nfe_id}")
        
        for el in signed_nfe.xpath(".//*"):
            if el.tag.startswith("{http://www.portalfiscal.inf.br/nfe}"):
                el.tag = el.tag.replace("{http://www.portalfiscal.inf.br/nfe}", "")
        
        envio = etree.Element("enviNFe", versao="4.00", xmlns=NFE_NAMESPACE)
        etree.SubElement(envio, "idLote").text = str(random.randint(1000, 99999999))
        etree.SubElement(envio, "indSinc").text = "1"
        envio.append(signed_nfe)
        
        xml_string = etree.tostring(envio, encoding="utf-8").decode()
        xml_string = xml_string.replace('algorithm-more#rsa-sha256', 'xmldsig#rsa-sha256')
        xml_string = xml_string.replace('xmlenc#sha256', 'xmldsig#sha256')
        
        soap = f'<soap12:Envelope xmlns:soap12="http://www.w3.org/2003/05/soap-envelope"><soap12:Body><nfeDadosMsg xmlns="http://www.portalfiscal.inf.br/nfe/wsdl/NFeAutorizacao4">{xml_string}</nfeDadosMsg></soap12:Body></soap12:Envelope>'
        
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as c, tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as k:
            c.write(base64.b64decode(cert_b64))
            k.write(key_pem)
            cp, kp = c.name, k.name
        
        try:
            res = requests.post(URL_SEFAZ, data=soap.encode('utf-8'), headers={'Content-Type': 'application/soap+xml; charset=utf-8'}, cert=(cp, kp), timeout=30)
            return res.text
        finally:
            if os.path.exists(cp): os.unlink(cp)
            if os.path.exists(kp): os.unlink(kp)

def gerar_xml_centi(rps_numero, dados_cliente, discriminacao, valor_total, data_emissao, codigo_ibge, caminho_pfx, senha_pfx):
    cert, key = carregar_certificado(senha_pfx)
    if not cert: return {"sucesso": False, "erros": ["Certificado invalido"]}
    
    builder = NFeBuilder()
    nfe_id = builder.montar_nfe({
        "rps_numero": rps_numero, "valor_total": valor_total, "data_emissao": data_emissao,
        "codigo_ibge": codigo_ibge, "documento_tomador": dados_cliente.get("documento", "").replace(".", "").replace("-", "").replace("/", "").strip(),
        "nome": dados_cliente.get("nome", ""), "endereco": dados_cliente.get("endereco", ""),
        "numero": str(dados_cliente.get("numero") or "SN"), "bairro": dados_cliente.get("bairro", ""),
        "uf": dados_cliente.get("uf", ""), "cep": dados_cliente.get("cep", "").replace("-", "").strip(),
        "nome_cidade": normalizar_texto(dados_cliente.get("cidade", "IACIARA"))
    })
    
    try:
        resultado = builder.assinar_e_transmitir(cert, key, nfe_id)
        return {"sucesso": True, "xml": resultado}
    except Exception as e: return {"sucesso": False, "erros": [str(e)]}