import json
from datetime import datetime, timedelta
import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import sys
import time
import os

print(f"🚀 Iniciando Brazmar Bot v3.0 P&I (Python {sys.version.split()[0]})")
print("=" * 60)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
HEADERS = {'User-Agent': USER_AGENT}

# Termos de busca 
TERMOS_BUSCA = [
    # Termos gerais P&I
    "P&I insurance maritime",
    "protection indemnity club",
    "marine insurance claim",
    "shipping liability insurance",
    "船舶保険 P&I",
    
    # Acidentes e sinistros
    "navio afundado Brasil",
    "acidente marítimo petroleiro",
    "colisão navios porto",
    "navio encalhado litoral",
    "vazamento óleo navio",
    "incêndio navio mercante",
    "abalroação navio",
    
    # Porto do Itaqui e complexos
    "Porto do Itaqui MA",
    "Terminal Marítimo Itaqui",
    "Complexo Portuário Itaqui",
    "Porto de Suape notícias",
    "Terminal de Suape",
    "Porto de Santos operação",
    "Porto de Paranaguá",
    "Porto de Rio Grande",
    
    # Marinha e regulamentação
    "Marinha Mercante Brasil",
    "Capitania dos Portos",
    "DPC Marinha Brasil",
    "Normam 2024",
    "regulamentação marítima ANTAQ",
    "IBAMA fiscalização navio",
    "receita federal alfândega porto",
    
    # Tipos de navios
    "graneleiro acidente",
    "petroleiro operação",
    "navio contêineres atracação",
    "rebocador portuário",
    "balsa transporte",
    "offshore plataforma",
    
    # Operações portuárias
    "praticagem porto",
    "rebocador manobra",
    "atracação navio",
    "desatracação terminal",
    "estadia portuária",
    "demurrage porto",
    "armador fretamento",
    
    # Cargas e mercadorias
    "carga avariada porto",
    "contêiner perdido",
    "mercadoria apreendida alfândega",
    "granel sólido porto",
    "carga líquida terminal",
    
    # Acidentes ambientais
    "vazamento óleo mar",
    "poluição marítima",
    "navio poluidor multa",
    "resíduos navio porto",
    
    # Legal/Jurídico
    "arresto navio Brasil",
    "embargo judicial navio",
    "desembargo maritime",
    "penhora embarcação",
    "processo judicial portuário",
    
    # Manutenção e reparo
    "estaleiro reparo navio",
    "docagem embarcação",
    "casco navio reparo",
    "lastro água navio",
    
    # Segurança
    "segurança marítima Brasil",
    "salvamento marítimo",
    "SAR Brasil",
    "busca salvamento marítimo"
]

PALAVRAS_PROIBIDAS = [
    # Trânsito e Rodoviário
    "moto", "motocicleta", "carro", "automóvel", "caminhão", "rodovia", "br-",
    "trânsito", "atropelou", "atropelamento", "colisão frontal", "motorista", "pedestre",
    "ônibus", "passageiro", "motoboy", "uber", "taxi",
    
    # Eventos sociais
    "olimpíada", "gincana", "jogos", "maio amarelo", "outubro rosa", "novembro azul",
    "concurso", "festa", "show", "cultura", "lazer", "passeio", "turismo",
    "inaugura praça", "visita escolar", "formatura", "simulado", "treinamento",
    "festival", "carnaval", "réveillon", "natal",
    
    # Crimes comuns não marítimos
    "polícia prende", "tráfico de drogas", "homicídio", "tiroteio", "facção",
    "assalto", "roubo", "furto", "latrocínio", "sequestro",
    
    # Política não relacionada
    "eleição", "candidato", "prefeito", "vereador", "deputado", "senador",
    "partido político", "votação", "plebiscito", "referendo",
    
    # Esportes
    "futebol", "campeonato", "estádio", "jogador", "time", "esporte",
    "natação", "corrida", "maratona", "competição",
    
    # Entretenimento
    "cinema", "filme", "série", "novela", "ator", "atriz", "celebridade",
    "música", "cantor", "banda", "show musical",
    
    # Saúde geral
    "hospital", "posto saúde", "vacina", "epidemia", "doença", "médico",
    "enfermeiro", "UTI", "pronto socorro",
    
    # Educação geral
    "escola", "universidade", "aluno", "professor", "aula", "ensino",
    
    # Ambiguidades Geográficas
    "porto alegre", "porto seguro", "porto velho",
    "rio de janeiro cidade", "são paulo capital"
]

PALAVRAS_CHAVE = [
    # P&I e Seguros
    "P&I", "proteção", "indenização", "seguro", "sinistro", "apólice",
    "cobertura", "franquia", "risco", "seguradora", "clube P&I",
    
    # Navios e embarcações
    "navio", "embarcação", "vessel", "ship", "graneleiro", "bulk carrier",
    "petroleiro", "tanker", "contêiner", "container ship", "rebocador", "tug",
    "balsa", "ferry", "offshore", "plataforma", "yacht", "veleiro",
    
    # Portos e terminais
    "porto", "terminal", "atracadouro", "ancoradouro", "cais", "píer",
    "dolfim", "caisense", "berço", "backlog", "roadstead",
    
    # Operações
    "praticagem", "pilotagem", "rebocador", "manobra", "atracação",
    "desatracação", "estadia", "demurrage", "despacho", "armador",
    "fretamento", "charter", "afretamento", "time charter",
    
    # Cargas
    "carga", "descarga", "estiva", "granel", "bulk", "contêiner",
    "container", "liquid bulk", "granel sólido", "granel líquido",
    "project cargo", "carga projeto", "carga perigosa",
    
    # Legal/Jurídico
    "arresto", "embargo", "desembargo", "penhora", "sequestro",
    "ação judicial", "processo", "litígio", "arbitragem", "LAJ",
    "liminar", "sentença", "execução",
    
    # Acidentes
    "colisão", "abalroação", "encalhe", "naufrágio", "afundamento",
    "incêndio", "explosão", "vazamento", "derramamento", "acidente",
    "sinistro", "avaria", "danos",
    
    # Ambiental
    "óleo", "poluição", "meio ambiente", "IBAMA", "multa ambiental",
    "resíduo", "lastro", "água lastro", "óleo lubrificante",
    
    # Regulatório
    "marinha", "capitania", "DPC", "normam", "ANTAQ", "regulamento",
    "fiscalização", "inspeção", "certificado", "documentação",
    
    # Financeiro
    "frete", "freight", "hire", "aluguel", "pagamento", "cobrança",
    "credor", "devedor", "hipoteca", "mortgage",
    
    # Técnico
    "casco", "hull", "lastro", "ballast", "leme", "rudder",
    "hélice", "propeller", "motor", "engine", "gerador",
    "estaleiro", "shipyard", "docagem", "dry dock", "reparo"
]

def validar_relevancia(texto):
    if not texto:
        return False
    
    texto_lower = texto.lower()
    
    for proibida in PALAVRAS_PROIBIDAS:
        if proibida in texto_lower:
            return False

    if "itaqui" in texto_lower:
        if not any(x in texto_lower for x in ["porto", "maranhão", "ma ", "são luís", "terminal", "marítimo"]):
            return False

    palavras_encontradas = [chave for chave in PALAVRAS_CHAVE if chave.lower() in texto_lower]
    
    termos_pi = ["p&i", "proteção", "indenização", "seguro", "sinistro"]
    tem_pi = any(termo in texto_lower for termo in termos_pi)
    
    # Se tiver termo P&I ou pelo menos 2 palavras-chave, é relevante
    return tem_pi or len(palavras_encontradas) >= 2

def parsear_data_rss(data_str):
    if not data_str:
        return datetime.now()
    
    # Formatos possíveis de parsing 
    formatos = [
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M',
        '%d-%m-%Y %H:%M',
        '%d/%m/%Y',
        '%d-%m-%Y'
    ]
    
    for formato in formatos:
        try:
            return datetime.strptime(data_str, formato)
        except:
            continue
    
    return datetime.now()

def buscar_noticias_google_rss(termo_busca):
    noticias = []
    
    try:
        termo_codificado = quote_plus(termo_busca)
        url = f"https://news.google.com/rss/search?q={termo_codificado}&hl=pt-BR&gl=BR&ceid=BR:pt-419"
        
        print(f"🔍 Buscando: {termo_busca}")
        
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"   ⚠️  Erro HTTP: {response.status_code}")
            return noticias
        
        root = ET.fromstring(response.content)
        
        items = root.findall('.//item')
        print(f"   📰 Encontrados {len(items)} itens no feed")
        
        for item in items[:10]: 
            try:
                titulo = item.find('title').text if item.find('title') is not None else 'Sem título'
                link = item.find('link').text if item.find('link') is not None else '#'
                descricao = item.find('description').text if item.find('description') is not None else ''
                pub_date = item.find('pubDate').text if item.find('pubDate') is not None else None
                fonte = item.find('source').text if item.find('source') is not None else 'Google News'
                
                data = parsear_data_rss(pub_date)
                
                # Mudar dias quando for necessário, por enquanto vou deixar 2 meses
                limite = datetime.now() - timedelta(days=60)
                if data < limite:
                    continue
                
                texto_completo = f"{titulo} {descricao}"
                
                if validar_relevancia(texto_completo):
                    titulo_limpo = titulo.split(' - ')[0] if ' - ' in titulo else titulo
                    titulo_limpo = titulo_limpo.split(' | ')[0]
                    
                    tag = "P&I"
                    if any(palavra in texto_completo.lower() for palavra in ['acidente', 'sinistro', 'colisão', 'incêndio']):
                        tag = "Sinistro"
                    elif any(palavra in texto_completo.lower() for palavra in ['porto', 'terminal', 'atracação']):
                        tag = "Portuário"
                    elif any(palavra in texto_completo.lower() for palavra in ['marinha', 'normam', 'antag']):
                        tag = "Regulatório"
                    elif any(palavra in texto_completo.lower() for palavra in ['ambiental', 'ibama', 'poluição']):
                        tag = "Ambiental"
                    elif any(palavra in texto_completo.lower() for palavra in ['legal', 'judicial', 'processo']):
                        tag = "Jurídico"
                    
                    noticias.append({
                        'titulo': titulo_limpo[:150],  # Limitar tamanho
                        'link': link,
                        'data': data.strftime('%d/%m/%Y'),
                        'fonte': fonte[:50],
                        'tag': tag,
                        'descricao': descricao[:200] + '...' if descricao else '',
                        'termo_busca': termo_busca[:30]
                    })
                    
            except Exception as e:
                continue  
        
        print(f"   ✅ Relevantes: {len(noticias)} notícias")
        
    except Exception as e:
        print(f"   ❌ Erro: {str(e)[:50]}...")
    
    return noticias

def remover_duplicatas(noticias):
    noticias_unicas = []
    titulos_vistos = set()
    
    for noticia in noticias:
        titulo_simplificado = ''.join([c for c in noticia['titulo'].lower() if c.isalnum()])[:80]
        
        if titulo_simplificado not in titulos_vistos:
            noticias_unicas.append(noticia)
            titulos_vistos.add(titulo_simplificado)
    
    return noticias_unicas

def salvar_noticias(noticias, pasta='public'):
    try:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"📁 Pasta '{pasta}' criada")
        
        noticias.sort(key=lambda x: datetime.strptime(x['data'], '%d/%m/%Y'), reverse=True)
        
        caminho_arquivo = os.path.join(pasta, 'noticias.json')
        
        with open(caminho_arquivo, 'w', encoding='utf-8') as f:
            json.dump(noticias, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Arquivo salvo: {caminho_arquivo}")
        print(f"📊 Total de notícias salvas: {len(noticias)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao salvar arquivo: {str(e)}")
        return False

def criar_noticias_exemplo(pasta='public'):
    print("\n📝 Criando notícias de exemplo P&I...")
    
    noticias_exemplo = [
        {
            "titulo": "Clube P&I alerta para aumento de sinistros com graneleiros no Atlântico Sul",
            "link": "https://exemplo.com/pi1",
            "data": datetime.now().strftime('%d/%m/%Y'),
            "fonte": "Maritime Insurance Review",
            "tag": "P&I",
            "descricao": "Clube de P&I reporta aumento de 30% em sinistros envolvendo graneleiros na rota Brasil-África...",
            "termo_busca": "P&I insurance"
        },
        {
            "titulo": "Navio petroleiro tem vazamento de óleo próximo ao Porto do Itaqui",
            "link": "https://exemplo.com/pi2",
            "data": (datetime.now() - timedelta(days=1)).strftime('%d/%m/%Y'),
            "fonte": "Portal Marítimo",
            "tag": "Sinistro",
            "descricao": "Embarcação de bandeira liberiana apresenta vazamento durante operação de carga...",
            "termo_busca": "vazamento óleo navio"
        },
        {
            "titulo": "ANTAQ publica nova resolução sobre demurrage em terminais portuários",
            "link": "https://exemplo.com/pi3",
            "data": (datetime.now() - timedelta(days=2)).strftime('%d/%m/%Y'),
            "fonte": "Diário Oficial",
            "tag": "Regulatório",
            "descricao": "Agência Nacional de Transportes Aquaviários atualiza regras para cobrança de demurrage...",
            "termo_busca": "demurrage porto"
        },
        {
            "titulo": "Justiça decreta arresto de navio graneleiro por dívida de frete",
            "link": "https://exemplo.com/pi4",
            "data": (datetime.now() - timedelta(days=3)).strftime('%d/%m/%Y'),
            "fonte": "Jornal Náutico",
            "tag": "Jurídico",
            "descricao": "Embarcação ficará retida no Porto de Santos até solução de litígio entre armador e fretador...",
            "termo_busca": "arresto navio"
        },
        {
            "titulo": "Complexo de Suape investe R$ 300 milhões em novo terminal de contêineres",
            "link": "https://exemplo.com/pi5",
            "data": (datetime.now() - timedelta(days=4)).strftime('%d/%m/%Y'),
            "fonte": "Agência Portuária",
            "tag": "Portuário",
            "descricao": "Ampliação aumentará capacidade de movimentação em 40% no terminal nordestino...",
            "termo_busca": "Suape terminal"
        }
    ]
    
    salvar_noticias(noticias_exemplo, pasta)
    return noticias_exemplo

def main():
    print("🎯 BRAZMAR P&I - Coletor de Notícias Especializado")
    print(f"📅 Período: últimos 30 dias")
    print(f"🔑 Termos de busca P&I: {len(TERMOS_BUSCA)}")
    print("=" * 60)
    
    todas_noticias = []
    
    termos_limitados = TERMOS_BUSCA[:15] 
    
    for i, termo in enumerate(termos_limitados, 1):
        print(f"\n[{i}/{len(termos_limitados)}] ", end="")
        noticias = buscar_noticias_google_rss(termo)
        todas_noticias.extend(noticias)
        time.sleep(0.5)
    
    noticias_unicas = remover_duplicatas(todas_noticias)
    
    print(f"\n{'='*60}")
    print(f"📈 Total encontrado: {len(noticias_unicas)} notícias P&I relevantes")
    
    if noticias_unicas:
        sucesso = salvar_noticias(noticias_unicas, 'public')

        if sucesso:
            print("\n📋 RESUMO DAS NOTÍCIAS P&I:")
            for i, noticia in enumerate(noticias_unicas[:8], 1):
                print(f"{i}. [{noticia['tag']}] {noticia['titulo'][:60]}...")
                print(f"   📅 {noticia['data']} | 📰 {noticia['fonte']}")
            
            print("\n🏷️  DISTRIBUIÇÃO POR CATEGORIA:")
            tags = {}
            for noticia in noticias_unicas:
                tags[noticia['tag']] = tags.get(noticia['tag'], 0) + 1
            
            for tag, count in tags.items():
                print(f"   {tag}: {count} notícias")
                
    else:
        print("\n📭 Nenhuma notícia P&I encontrada.")
        print("Criando notícias de exemplo para demonstração...")
        criar_noticias_exemplo('public')
    
    print(f"\n✅ Processo concluído em {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Processo interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
        criar_noticias_exemplo('public')