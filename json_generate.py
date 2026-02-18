import os
import sys
import json
from bs4 import BeautifulSoup

def gerar_json_atividades(pasta_alvo):
    # Verifica se a pasta informada realmente existe
    if not os.path.isdir(pasta_alvo):
        print(f"❌ ERRO: A pasta '{pasta_alvo}' não existe ou não foi encontrada.")
        return

    # 1. Encontrar os arquivos HTML na pasta alvo
    arquivos = os.listdir(pasta_alvo)
    
    arquivos_mdl = [f for f in arquivos if f.endswith('.mdl.html')]
    arquivos_yt = [f for f in arquivos if f.endswith('.yt.html')]

    # Validação Rígida: Deve haver exatamente 1 de cada
    if len(arquivos_mdl) != 1:
        print(f"❌ ERRO: Encontrado(s) {len(arquivos_mdl)} arquivo(s) '.mdl.html' na pasta '{pasta_alvo}'.")
        print("   -> É necessário ter exatamente UM arquivo '.mdl.html'.")
        return
        
    if len(arquivos_yt) != 1:
        print(f"❌ ERRO: Encontrado(s) {len(arquivos_yt)} arquivo(s) '.yt.html' na pasta '{pasta_alvo}'.")
        print("   -> É necessário ter exatamente UM arquivo '.yt.html'.")
        return

    # Pega o nome do único arquivo encontrado de cada tipo
    arquivo_mdl = arquivos_mdl[0]
    arquivo_yt = arquivos_yt[0]

    # Monta o caminho completo (Pasta + Nome do Arquivo)
    caminho_mdl = os.path.join(pasta_alvo, arquivo_mdl)
    caminho_yt = os.path.join(pasta_alvo, arquivo_yt)

    print(f"📂 Pasta alvo: {pasta_alvo}")
    print(f"📄 Lendo Moodle: {arquivo_mdl}")
    print(f"📄 Lendo YouTube: {arquivo_yt}")

    # Verifica se precisa inverter a lista do YouTube
    deve_inverter_yt = ".flip." in arquivo_yt

    # 2. Extraindo dados do Moodle
    moodle_items = []
    with open(caminho_mdl, 'r', encoding='utf-8') as f:
        soup_mdl = BeautifulSoup(f, 'html.parser')
        
        atividades_h5p = soup_mdl.find_all('li', class_='modtype_hvp')
        
        for atividade in atividades_h5p:
            course_id = atividade.get('data-id')
            span_nome = atividade.find('span', class_='inplaceeditable')
            
            if span_nome and span_nome.get('data-value'):
                title = span_nome.get('data-value')
            else:
                link = atividade.find('a', class_='aalink')
                if link:
                    nome_span = link.find('span', class_='instancename')
                    if nome_span:
                        escondido = nome_span.find('span', class_='accesshide')
                        if escondido:
                            escondido.decompose()
                        title = nome_span.get_text(strip=True)
            
            if course_id and title:
                moodle_items.append({
                    "course-title": title,
                    "course-id": course_id
                })

    # 3. Extraindo dados do YouTube
    yt_items = []
    with open(caminho_yt, 'r', encoding='utf-8') as f:
        soup_yt = BeautifulSoup(f, 'html.parser')
        
        videos = soup_yt.find_all('ytd-playlist-video-renderer')
        
        for video in videos:
            a_tag = video.find('a', id='video-title')
            if not a_tag:
                continue
                
            yt_name = a_tag.get('title')
            yt_link = "https://www.youtube.com" + a_tag.get('href')
            
            tempo_div = video.find('div', class_='yt-badge-shape__text')
            yt_time = tempo_div.get_text(strip=True) if tempo_div else ""
            
            yt_items.append({
                "yt-name": yt_name,
                "yt-link": yt_link,
                "yt-time": yt_time
            })

    # 4. Inverter a lista do YouTube caso seja .flip.yt.html
    if deve_inverter_yt:
        print("🔄 Arquivo '.flip.' detectado. Invertendo a ordem dos vídeos do YouTube...")
        yt_items.reverse()

    # 5. Validação RÍGIDA de Quantidade
    print(f"\n📊 Total atividades Moodle encontradas: {len(moodle_items)}")
    print(f"📊 Total vídeos YouTube encontrados: {len(yt_items)}")
    
    if len(moodle_items) != len(yt_items):
        print("\n❌ ERRO CRÍTICO: As quantidades não batem!")
        print("   -> A quantidade de vídeos do YouTube é diferente da quantidade de atividades H5P do Moodle.")
        print("   -> Verifique os HTMLs, corrija o que faltar e rode novamente.")
        return 

    # 6. Juntando as duas listas
    json_final = []
    for mdl, yt in zip(moodle_items, yt_items):
        item_combinado = {
            "yt-name": yt["yt-name"],
            "yt-link": yt["yt-link"],
            "yt-time": yt["yt-time"],
            "course-title": mdl["course-title"],
            "course-id": mdl["course-id"]
        }
        json_final.append(item_combinado)

    # 7. Salvando o arquivo NA PASTA ALVO
    caminho_json = os.path.join(pasta_alvo, 'mapping.json')
    
    with open(caminho_json, 'w', encoding='utf-8') as f:
        json.dump(json_final, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Sucesso! Arquivo gerado em: {caminho_json}")

if __name__ == "__main__":
    # Verifica se o usuário passou a pasta como argumento no terminal
    if len(sys.argv) < 2:
        print("❌ ERRO: Faltou informar a pasta!")
        print("💡 Uso correto: python json_generate.py <caminho_da_pasta>")
        print("💡 Exemplo: python json_generate.py content/Entendendo-HTML-e-CSS/")
    else:
        # Pega o primeiro argumento após o nome do script
        pasta_informada = sys.argv[1]
        gerar_json_atividades(pasta_informada)