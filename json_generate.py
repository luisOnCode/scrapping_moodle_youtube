import os
import json
from bs4 import BeautifulSoup

def gerar_json_atividades():
    # 1. Encontrar os arquivos HTML na pasta atual
    arquivos = os.listdir('.')
    
    arquivo_mdl = next((f for f in arquivos if f.endswith('.mdl.html')), None)
    arquivo_yt = next((f for f in arquivos if f.endswith('.yt.html')), None)

    if not arquivo_mdl or not arquivo_yt:
        print("Erro: Arquivos .mdl.html ou .yt.html não encontrados na pasta atual.")
        return

    print(f"Lendo Moodle: {arquivo_mdl}")
    print(f"Lendo YouTube: {arquivo_yt}")

    # Verifica se precisa inverter a lista do YouTube
    deve_inverter_yt = ".flip." in arquivo_yt

    # 2. Extraindo dados do Moodle
    moodle_items = []
    with open(arquivo_mdl, 'r', encoding='utf-8') as f:
        soup_mdl = BeautifulSoup(f, 'html.parser')
        
        # Pega APENAS as listas <li> que são atividades do tipo H5P
        atividades_h5p = soup_mdl.find_all('li', class_='modtype_hvp')
        
        for atividade in atividades_h5p:
            # O ID da atividade já vem limpo na tag <li>
            course_id = atividade.get('data-id')
            
            # O nome limpo da atividade fica no atributo 'data-value' de um span específico
            span_nome = atividade.find('span', class_='inplaceeditable')
            
            if span_nome and span_nome.get('data-value'):
                title = span_nome.get('data-value')
            else:
                # Fallback caso o html mude: pega do link e limpa a tag <span class="accesshide">
                link = atividade.find('a', class_='aalink')
                if link:
                    nome_span = link.find('span', class_='instancename')
                    if nome_span:
                        escondido = nome_span.find('span', class_='accesshide')
                        if escondido:
                            escondido.decompose() # Remove a palavra "Conteúdo interativo"
                        title = nome_span.get_text(strip=True)
            
            if course_id and title:
                moodle_items.append({
                    "course-title": title,
                    "course-id": course_id
                })

    # 3. Extraindo dados do YouTube
    yt_items = []
    with open(arquivo_yt, 'r', encoding='utf-8') as f:
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
        print("Arquivo '.flip.' detectado. Invertendo a ordem dos vídeos do YouTube...")
        yt_items.reverse()

    # 5. Validação RÍGIDA de Quantidade
    print(f"\nTotal atividades Moodle encontradas: {len(moodle_items)}")
    print(f"Total vídeos YouTube encontrados: {len(yt_items)}")
    
    if len(moodle_items) != len(yt_items):
        # HARD STOP: Se der ruim, o script morre aqui mesmo avisando o erro.
        print("\n❌ ERRO CRÍTICO: As quantidades não batem!")
        print("   -> A quantidade de vídeos do YouTube é diferente da quantidade de atividades H5P do Moodle.")
        print("   -> Verifique os HTMLs, corrija o que faltar e rode novamente.")
        return 

    # 6. Juntando as duas listas (agora com certeza têm o mesmo tamanho)
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

    # 7. Salvando o arquivo
    with open('atividades_mapeadas.json', 'w', encoding='utf-8') as f:
        json.dump(json_final, f, ensure_ascii=False, indent=4)
        
    print("\n✅ Sucesso! Arquivo 'atividades_mapeadas.json' gerado e pronto para o Playwright!")

if __name__ == "__main__":
    gerar_json_atividades()