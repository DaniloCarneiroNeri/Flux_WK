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
            temp_pfx.write(pfx_data)
            temp_pfx_path = temp_pfx.name
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
    def validar_com_xsd(self, xml_element):
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            xsd_file = os.path.join(base_dir, "nfe_v4.00.xsd")
            
            schema_doc = etree.parse(xsd_file)
            schema = etree.XMLSchema(schema_doc)
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
        for tag, val in [("xLgr", "AV 21 DE ABRIL"), ("nro", "SN"), ("xBairro", "SOLON AMARAL"), ("cMun", "5209903"), ("xMun", "Iaciara"), ("UF", "GO"), ("CEP", "73920000"), ("cPais", "1058"), ("xPais", "BRASIL")]:
            etree.SubElement(enderEmit, f"{{{NFE_NAMESPACE}}}{tag}").text = val
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}IE").text = PRESTADOR_IE
        etree.SubElement(emit, f"{{{NFE_NAMESPACE}}}CRT").text = "1"
        
        dest = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}dest")
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}{'CPF' if len(dados['documento_tomador'])==11 else 'CNPJ'}").text = dados["documento_tomador"]
        etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}xNome").text = normalizar_texto(dados["nome"][:60])
        enderDest = etree.SubElement(dest, f"{{{NFE_NAMESPACE}}}enderDest")
        for tag, val in [("xLgr", normalizar_texto(dados["endereco"])), ("nro", dados["numero"]), ("xBairro", normalizar_texto(dados["bairro"])), ("cMun", dados["codigo_ibge"]), ("xMun", "IACIARA"), ("UF", dados["uf"]), ("CEP", dados["cep"]), ("cPais", "1058"), ("xPais", "BRASIL")]:
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
        campos_tot = [
            "vBC", "vICMS", "vICMSDeson", "vFCPUFDest", "vICMSUFDest", "vICMSUFRemet",
            "vFCP", "vBCST", "vST", "vFCPST", "vFCPSTRet", "vProd", "vFrete", "vSeg",
            "vDesc", "vII", "vIPI", "vIPIDevol", "vPIS", "vCOFINS", "vOutro", "vNF", "vTotTrib"
        ]
        for f in campos_tot:
            val = f"{dados['valor_total']:.2f}" if f in ["vProd", "vNF"] else "0.00"
            etree.SubElement(ict, f"{{{NFE_NAMESPACE}}}{f}").text = val
        
        transp = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}transp")
        etree.SubElement(transp, f"{{{NFE_NAMESPACE}}}modFrete").text = "9"
        
        pag = etree.SubElement(infNFe, f"{{{NFE_NAMESPACE}}}pag")
        dpag = etree.SubElement(pag, f"{{{NFE_NAMESPACE}}}detPag")
        etree.SubElement(dpag, f"{{{NFE_NAMESPACE}}}tPag").text = "01"
        etree.Sub