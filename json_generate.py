import os
import sys
import json
import re
from bs4 import BeautifulSoup

def format_course_title(raw_name):
    # 1. Remove o padrão inicial de números (Ex: "02.01_", "04.10_", "10.05_")
    clean_name = re.sub(r'^\d+\.\d+_', '', raw_name).strip()
    
    # 2. Formatação avançada (baseado no seu padrão de organização):
    # Transforma " Parte 1" em " | 01"
    clean_name = re.sub(r'(?i)\s+parte\s+(\d+)$', r' | 0\1', clean_name)
    
    # Transforma " Extra" no final da string em " (Extra)"
    clean_name = re.sub(r'(?i)\s+extra$', r' (Extra)', clean_name)
    
    return clean_name

def generate_activities_json(target_folder):
    if not os.path.isdir(target_folder):
        print(f"❌ ERROR: The folder '{target_folder}' does not exist or was not found.")
        return

    files = os.listdir(target_folder)
    
    mdl_files = [f for f in files if f.endswith('.mdl.html')]
    yt_files = [f for f in files if f.endswith('.yt.html')]

    if len(mdl_files) != 1:
        print(f"❌ ERROR: Found {len(mdl_files)} '.mdl.html' file(s) in folder '{target_folder}'.")
        print("   -> Exactly ONE '.mdl.html' file is required.")
        return
        
    if len(yt_files) != 1:
        print(f"❌ ERROR: Found {len(yt_files)} '.yt.html' file(s) in folder '{target_folder}'.")
        print("   -> Exactly ONE '.yt.html' file is required.")
        return

    mdl_file = mdl_files[0]
    yt_file = yt_files[0]

    mdl_path = os.path.join(target_folder, mdl_file)
    yt_path = os.path.join(target_folder, yt_file)

    print(f"📂 Target folder: {target_folder}")
    print(f"📄 Reading Moodle: {mdl_file}")
    print(f"📄 Reading YouTube: {yt_file}")

    should_flip_yt = ".flip." in yt_file

    moodle_items = []
    with open(mdl_path, 'r', encoding='utf-8') as f:
        soup_mdl = BeautifulSoup(f, 'html.parser')
        
        h5p_activities = soup_mdl.find_all('li', class_='modtype_hvp')
        
        for activity in h5p_activities:
            course_id = activity.get('data-id')
            # Não precisamos mais extrair o nome do Moodle, pois ele é "Molde (copiado)"
            if course_id:
                moodle_items.append({
                    "course-id": course_id
                })

    yt_items = []
    with open(yt_path, 'r', encoding='utf-8') as f:
        soup_yt = BeautifulSoup(f, 'html.parser')
        
        videos = soup_yt.find_all('ytd-playlist-video-renderer')
        
        for video in videos:
            a_tag = video.find('a', id='video-title')
            if not a_tag:
                continue
                
            yt_name = a_tag.get('title')
            yt_link = "https://www.youtube.com" + a_tag.get('href')
            
            time_div = video.find('div', class_='yt-badge-shape__text')
            yt_time = time_div.get_text(strip=True) if time_div else ""
            
            yt_items.append({
                "yt-name": yt_name,
                "yt-link": yt_link,
                "yt-time": yt_time
            })

    if should_flip_yt:
        print("🔄 '.flip.' file detected. Reversing YouTube videos order...")
        yt_items.reverse()

    print(f"\n📊 Total Moodle activities found: {len(moodle_items)}")
    print(f"📊 Total YouTube videos found: {len(yt_items)}")
    
    if len(moodle_items) != len(yt_items):
        print("\n❌ CRITICAL ERROR: The quantities do not match!")
        print("   -> The number of YouTube videos is different from the number of Moodle H5P activities.")
        print("   -> Please check the HTML files, fix any missing items, and run again.")
        return 

    json_final = []
    for mdl, yt in zip(moodle_items, yt_items):
        
        # Aqui a mágica acontece: o título do curso é gerado limpando o nome do YouTube
        beautiful_title = format_course_title(yt["yt-name"])
        
        combined_item = {
            "yt-name": yt["yt-name"],
            "yt-link": yt["yt-link"],
            "yt-time": yt["yt-time"],
            "course-title": beautiful_title,
            "course-id": mdl["course-id"]
        }
        json_final.append(combined_item)

    json_path = os.path.join(target_folder, 'mapping.json')
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_final, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ Success! File generated at: {json_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ ERROR: Missing folder argument!")
        print("💡 Correct usage: python json_generate.py <folder_path>")
        print("💡 Example: python json_generate.py content/data/")
    else:
        provided_folder = sys.argv[1]
        generate_activities_json(provided_folder)