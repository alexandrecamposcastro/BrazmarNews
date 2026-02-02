import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import sys
import time
import os
import google.generativeai as genai
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

# Configuração da IA
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
ai_model = genai.GenerativeModel('gemini-2.5-flash')

print(f"Iniciando bot : (Python {sys.version.split()[0]})")
print("=" * 60)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {'User-Agent': USER_AGENT}

TERMOS_BUSCA = [
    "P&I insurance maritime", "protection indemnity club", "marine insurance claim",
    "shipping liability insurance", "navio afundado Brasil", "acidente marítimo petroleiro",
    "colisão navios porto", "navio encalhado litoral", "vazamento óleo navio",
    "incêndio navio mercante", "abalroação navio", "Porto do Itaqui MA",
    "Terminal Marítimo Itaqui", "Complexo Portuário Itaqui", "Porto de Suape notícias",
    "Terminal de Suape", "Porto de Santos operação", "Porto de Paranaguá",
    "Porto de Rio Grande", "Marinha Mercante Brasil", "Capitania dos Portos",
    "DPC Marinha Brasil", "Normam 2024", "regulamentação marítima ANTAQ",
    "IBAMA fiscalização navio", "receita federal alfândega porto", "graneleiro acidente",
    "petroleiro operação", "navio contêineres atracação", "rebocador portuário",
    "balsa transporte", "offshore plataforma", "praticagem porto", "rebocador manobra",
    "atracação navio", "desatracação terminal", "estadia portuária", "demurrage porto",
    "armador fretamento", "carga avariada porto", "contêiner perdido",
    "mercadoria apreendida alfândega", "granel sólido porto", "carga líquida terminal",
    "vazamento óleo mar", "poluição marítima", "navio poluidor multa",
    "resíduos navio porto", "arresto navio Brasil", "embargo judicial navio",
    "desembargo maritime", "penhora embarcação", "processo judicial portuário",
    "estaleiro reparo navio", "docagem embarcação", "casco navio reparo",
    "lastro água navio", "segurança marítima Brasil", "salvamento marítimo",
    "SAR Brasil", "busca salvamento marítimo"
] 

PALAVRAS_PROIBIDAS = [
    "moto", "motocicleta", "carro", "automóvel", "caminhão", "rodovia", "br-",
    "trânsito", "atropelou", "atropelamento", "colisão frontal", "motorista", "pedestre",
    "ônibus", "passageiro", "motoboy", "uber", "taxi", "olimpíada", "gincana", "jogos",
    "maio amarelo", "outubro rosa", "novembro azul", "concurso", "festa", "show",
    "cultura", "lazer", "passeio", "turismo", "inaugura praça", "visita escolar",
    "formatura", "simulado", "treinamento", "festival", "carnaval", "réveillon",
    "natal", "polícia prende", "tráfico de drogas", "homicídio", "tiroteio", "facção",
    "assalto", "roubo", "furto", "latrocínio", "sequestro", "eleição", "candidato",
    "prefeito", "vereador", "deputado", "senador", "partido político", "votação",
    "plebiscito", "referendo", "futebol", "campeonato", "estádio", "jogador", "time",
    "esporte", "natação", "corrida", "maratona", "competição", "cinema", "filme",
    "série", "novela", "ator", "atriz", "celebridade", "música", "cantor", "banda",
    "show musical", "hospital", "posto saúde", "vacina", "epidemia", "doença",
    "médico", "enfermeiro", "UTI", "pronto socorro", "escola", "universidade",
    "aluno", "professor", "aula", "ensino", "porto alegre", "porto seguro",
    "porto velho", "rio de janeiro cidade", "são paulo capital"
] # 

PALAVRAS_CHAVE = [
    "p&i", "proteção", "indenização", "seguro", "sinistro", "apólice", "cobertura",
    "franquia", "risco", "seguradora", "clube p&i", "navio", "embarcação", "vessel",
    "ship", "graneleiro", "bulk carrier", "petroleiro", "tanker", "contêiner",
    "container ship", "rebocador", "tug", "balsa", "ferry", "offshore", "plataforma",
    "yacht", "veleiro", "porto", "terminal", "atracadouro", "ancoradouro", "cais",
    "píer", "dolfim", "caisense", "berço", "backlog", "roadstead", "praticagem",
    "pilotagem", "rebocador", "manobra", "atracação", "desatracação", "estadia",
    "demurrage", "despacho", "armador", "fretamento", "charter", "afretamento",
    "time charter", "carga", "descarga", "estiva", "granel", "bulk", "contêiner",
    "container", "liquid bulk", "granel sólido", "granel líquido", "project cargo",
    "carga projeto", "carga perigosa", "arresto", "embargo", "desembargo", "penhora",
    "sequestro", "ação judicial", "processo", "litígio", "arbitragem", "laj",
    "liminar", "sentença", "execução", "colisão", "abalroação", "encalhe",
    "naufrágio", "afundamento", "incêndio", "explosão", "vazamento", "derramamento",
    "acidente", "sinistro", "avaria", "danos", "óleo", "poluição", "meio ambiente",
    "ibama", "multa ambiental", "resíduo", "lastro", "água lastro", "óleo lubrificante",
    "marinha", "capitania", "dpc", "normam", "antaq", "regulamento", "fiscalização",
    "inspeção", "certificado", "documentação", "frete", "freight", "hire", "aluguel",
    "pagamento", "cobrança", "credor", "devedor", "hipoteca", "mortgage", "casco",
    "hull", "lastro", "ballast", "leme", "rudder", "hélice", "propeller", "motor",
    "engine", "gerador", "estaleiro", "shipyard", "docagem", "dry dock", "reparo"
]

def validar_relevancia(texto):
    if not texto: return False
    texto_lower = texto.lower()
    for proibida in PALAVRAS_PROIBIDAS:
        if proibida in texto_lower: return False
    if "itaqui" in texto_lower:
        if not any(x in texto_lower for x in ["porto", "maranhão", "ma ", "são luís", "terminal", "marítimo"]):
            return False
    palavras_encontradas = [chave for chave in PALAVRAS_CHAVE if chave.lower() in texto_lower]
    tem_pi = any(termo in texto_lower for termo in ["p&i", "proteção", "indenização", "seguro", "sinistro"])
    return tem_pi or len(palavras_encontradas) >= 2 # 

def parsear_data_rss(data_str):
    if not data_str: return datetime.now()
    formatos = [
        '%a, %d %b %Y %H:%M:%S %z', '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z', '%Y-%m-%d %H:%M:%S', '%d/%m/%Y %H:%M'
    ]
    for formato in formatos:
        try: return datetime.strptime(data_str, formato)
        except: continue
    return datetime.now() 

def analisar_com_ia(titulo, descricao):
    prompt = f"""
    Analise a notícia abaixo para um Clube de Seguros P&I.
    Retorne APENAS um objeto JSON com:
    {{
        "risco_pontuacao": (int de 0 a 10),
        "analise_ia": "resumo técnico do impacto marítimo/jurídico",
        "entidades": ["lista de navios, portos ou empresas"],
        "recomendacao": "ação sugerida para o segurador"
    }}
    Notícia: {titulo} | Contexto: {descricao[:300]}
    """
    try:
        response = ai_model.generate_content(prompt)
        content = response.text.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        return json.loads(content)
    except Exception as e:
        return {
            "risco_pontuacao": 0, 
            "analise_ia": f"Falha no processamento: {str(e)[:50]}", 
            "entidades": [], 
            "recomendacao": "Revisão manual necessária"
        }

def buscar_noticias_google_rss(termo_busca):
    noticias = []
    try:
        termo_codificado = quote_plus(termo_busca)
        url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419" 
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200: return noticias
        
        root = ET.fromstring(response.content)
        items = root.findall('.//item')
        
        for item in items[:15]:
            titulo = item.find('title').text
            descricao = item.find('description').text or ""
            pub_date = item.find('pubDate').text
            data = parsear_data_rss(pub_date)
            
            if data < datetime.now() - timedelta(days=60): continue 
            
            if validar_relevancia(f"{titulo} {descricao}"):
                ia_data = analisar_com_ia(titulo, descricao)
                
                noticias.append({
                    'titulo': titulo.split(' - ')[0],
                    'link': item.find('link').text,
                    'data': data.strftime('%d/%m/%Y'),
                    'fonte': item.find('source').text if item.find('source') is not None else 'Google News',
                    **ia_data
                })
    except Exception as e: print(f"Erro: {e}")
    return noticias

def main():
    print(f"Buscando em todos os {len(TERMOS_BUSCA)} termos (Processamento Paralelo)...")
    todas_noticias = []
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        resultados = list(executor.map(buscar_noticias_google_rss, TERMOS_BUSCA))
    
    for r in resultados: todas_noticias.extend(r)
    
    unicas = []
    vistos = set()
    for n in todas_noticias:
        slug = "".join([c for c in n['titulo'].lower() if c.isalnum()])[:80]
        if slug not in vistos:
            unicas.append(n)
            vistos.add(slug)
            
    os.makedirs('public', exist_ok=True)
    with open('public/noticias.json', 'w', encoding='utf-8') as f:
        json.dump(unicas, f, ensure_ascii=False, indent=2)
        
    print(f"Total de {len(unicas)} notícias P&I processadas com IA.")

if __name__ == "__main__":
    main()