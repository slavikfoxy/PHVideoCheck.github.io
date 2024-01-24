import phub
import codecs
import json
from datetime import datetime
from phub.locals import *
import os
import re
import requests
from bs4 import BeautifulSoup
inputF = "listvideo.json"
outputLog = 'outputJSON.json'
pattern = r'"video\.url":\s+"(https://[^"]+)"'
pattern2 = r'viewkey=(\w+)'
client = phub.Client('allashevtcova@yandex.ru', '1qa2ws3ed', delay = 0.2)
videoUrl = set()

def extract_objects_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Використовуємо регулярний вираз для вилучення об'єктів з рядка
    objects = re.findall(r'\{[^}]*\}', content)
    # Додаємо кому після кожного "}" крім останнього елементу
    modified_content = ','.join(objects)
    # Перетворюємо модифікований вміст у список об'єктів JSON
    modified_objects = json.loads(f'[{modified_content}]')
    return modified_objects
def download_image(url, filename):
    if not os.path.exists(filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
    return
        

def imput():
    with open(inputF, 'r+', encoding='utf-8') as FR,open('tmp.json', 'w', encoding='utf-8') as OUT:
        delend(inputF, 0)
        files_sete = get_file_list('./img')
        modified_objects = extract_objects_from_file(outputLog)
        OUT.write('[')
        for i, obj in enumerate(modified_objects):
            is_last_element = (i == len(modified_objects) - 1)
            #print(obj)
            obj_str = json.dumps(obj, ensure_ascii=False,indent=2)
            if is_last_element:
                OUT.write(obj_str)
            else:
                OUT.write(obj_str + ',')
           
        OUT.write(']')
        OUT.close()
        data = json.load(FR)
        FR.close()
        keywords1 = set(item["video.url"] for item in data if "video.url" in item)
        delend(inputF, 1)
        with open(inputF, 'a', encoding='utf-8') as FW:
            for i, video in enumerate(client.account.watched):
                try:
                    image_filename = f'img/{video.key}.jp'
                    if not f'{video.key}.jp' in files_sete:
                         print(f'Download img {image_filename}')
                         download_image(video.image.url, image_filename)
                    videoUrl.add(video.url)
                    if video.url in keywords1:
                       print(f'{i}')
                    else:
                        print(f'{i}. "{video.title}"')
                        vidAuthor = str(video.author)
                        data = {
                            'video.date':str(video.date),
                            'video.author': vidAuthor[15:-1],
                            'video.url': video.url,
                            'video.image.url': video.image.url,
                            'video.title': video.title
                            }
                        FW.write(",")
                        json.dump(data, FW, ensure_ascii=False,indent=2)
                except:
                    print(f'ERROR - {video.key}')
                    data = {
                        'video.url': video.url,
                        'video.title': video.title
                        }
                    FW.write(",")
                    json.dump(data, FW, ensure_ascii=False,indent=2)     
        delend(inputF, 0)
                
def delend(file_path, dela):
    with open(file_path, 'r+', encoding='utf-8') as file:
    # Перейти в кінець файлу
        file.seek(0, 2)
        file.seek(file.tell() - 1, 0)
        last_char = file.read(1)
        print(f'last_char - {last_char}')
        file.seek(file.tell() - 2, 0)
        second_last_char = file.read(2)
        file.seek(file.tell() - 3, 0)
        three_last_char = file.read(3)
        if dela == 1:
            if last_char == ']' and second_last_char == ',' and three_last_char == '}':
                file.seek(file.tell() - 1, 0)
                file.truncate()
                file.seek(file.tell() - 2, 0)
                file.truncate()
                print(f'deleted ] and , ')
            if last_char == ']' and second_last_char == '}' :
                file.seek(file.tell() - 1, 0)
                file.truncate()
                print(f'deleted ] and')
            if last_char == ',' and second_last_char == '}' :
                file.seek(file.tell() - 1, 0)
                file.truncate()
                print(f'deleted , and')
            if last_char == ']':
                file.seek(file.tell() - 1, 0)
                file.truncate()
                print(f'deleted ]')
        if dela == 0:
            if last_char != ']':
                file.write("]")
                print(f'Write ]')
            
def compare_json_files_by_keywords(file1, output_file):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    with open(file1, 'r', encoding='utf-8') as f1, open(output_file, 'r', encoding='utf-8') as outputr:
        delend(file1, 0)
        data1 = json.load(f1)
        keywords1 = set(item.get('video.url') for item in data1)
        lines1 = [line.strip() for line in outputr]
        outputr.close()
        OutputList = [extract_keyword(line) for line in lines1 if extract_keyword(line)]
        with open(output_file, 'a', encoding='utf-8') as output:
            missing_items = [item for item in data1 if item.get('video.url') in keywords1 - videoUrl]
            output.write(f'---{formatted_datetime}---\n')
            for item in missing_items:
                if item.get('video.url') not in OutputList:
                    #print(f'item.get video.url - {item.get('video.url')}')
                    #print(f'OutputList - {OutputList}')
                    print(f'Видалений елемент - {item} /n')
                    output.write(f'Deleted video: {json.dumps(item, ensure_ascii=False,indent=2)}\n')
    with open('tmp.json', 'r', encoding='utf-8') as dd:
        data2 = json.load(dd)
        with open('index.html', 'w', encoding='utf-8') as html_file:
            # Додаємо початок HTML-файлу
            html_file.write('<html>\n<head>\n<title>My HTML Page</title>\n</head>\n<body>\n')
            #if not os.path.exists('img'):
                #os.makedirs('img')
            # Обробляємо кожен елемент у JSON файлі
            for element in data2:
                # Отримуємо URL зображення
                image_url = element.get('video.image.url', {})
                # Якщо URL існує, скачуємо зображення та додаємо тег зображення в HTML файл
                if image_url:
                    html_file.write(f'<p>-----------------{data2.index(element)}------------------------</p>\n')
                    image_filenamee = f'img/{extract_keyword_key(element.get("video.url", {}))}.jp'
                    #download_image(image_url, image_filename)
                    html_file.write(f'<p>Video url: {element.get('video.url', {})}</p>\n')
                    html_file.write(f'<p>Video img url: {element.get('video.image.url', {})}</p>\n')
                    html_file.write(f'<img src="{image_filenamee}" title="{element.get('video.title', {})}">\n')
                    html_file.write(f'<p>Date: {element.get('video.date', {})}</p>\n')
                    html_file.write(f'<p>Author: {element.get('video.author', {})}</p>\n')

            # Додаємо кінець HTML-файлу
            html_file.write('</body>\n</html>')        
def extract_keyword(line):
    match = re.search(pattern, line)
    if match:
        url = match.group(1)
        return(url)
def extract_keyword_key(line):
    match = re.search(pattern2, line)
    if match:
        desired_characters = match.group(1)
        return(desired_characters)
def get_file_list(directory):
  file_list = set()
  for file in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file)):
      file_list.add(file)
  return file_list
# Приклад використання:
if __name__ == "__main__":
    imput()
    compare_json_files_by_keywords(inputF, outputLog) 
