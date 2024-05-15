import phub
import codecs
import json
from datetime import datetime
#from phub.locals import *
import os
import re
import requests
from bs4 import BeautifulSoup
from phub.utils import suppress
inputF = "listvideo.json"
outputLog = 'outputJSON.json'
pattern = r'"video\.url":\s+"(https://[^"]+)"'
pattern2 = r'viewkey=(\w+)'
client = phub.Client('allashevtcova@yandex.ru', 'Alla@2024', delay = 0.2)
videoUrlMy = set()
videoUrlTail = set()
videoUrlSocks = set()
videoUrlCostume = set()
videoUrlAll = set()

def buildTmp(filename):# Будує TMP з OutputJSON видалених відео
    with open(filename, 'w', encoding='utf-8') as OUT:
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

def SortInpList():# Будує TMP з OutputJSON видалених відео
    with open("listvideo.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
# Створюємо словник для збереження унікальних даних за video.url
        unique_data = {}
# Проходимося по кожному об'єкту у списку даних
        for item in data:
    # Використовуємо video.url як ключ для унікальних записів
             url = item['video.url']
    # Якщо url вже зустрічався, ігноруємо цей запис
             if url not in unique_data:
                 unique_data[url] = item

# Перетворюємо словник у список
    unique_data_list = list(unique_data.values())

# Записуємо унікальні дані у новий JSON файл
    with open('List2sort.json', 'w') as file:
        json.dump(unique_data_list, file, indent=4)
    file.close()

def input(name1, phlist,video_Url):
    try:
        with open(name1, 'r+', encoding='utf-8') as FR: 
            delend(name1, 0)
            data = json.load(FR)
            FR.close()
            keywords1 = set(item["video.url"] for item in data if "video.url" in item)
            #for i, keywords1 in enumerate(keywords1):
                #print(f'{i} {keywords1}')
            delend(name1, 1)
            with open(name1, 'a', encoding='utf-8') as FW:
                files_sete = get_file_list('./img')
               
                if (phlist == "client.account.watched"):
                    videos_iterator = iter(client.account.watched)
                else:
                    playlist = client.get_playlist(phlist)
                    videos_iterator = iter(playlist)
                #videos_iterator = iter(client.account.watched)
                i = 0
                while True:
                    try:
                            video =  next(videos_iterator)
                            image_filename = f'img/{video.key}.jp'
                            
                            if not f'{video.key}.jp' in files_sete:
                                 print(f'Download img {image_filename}')
                                 download_image(video.image.url, image_filename)
                            video_Url.add(video.url)
                            if video.url in keywords1:
                               print(f'{i} {video}')
                            else:
                                    print(f'{i} {video.url}')
                                    image = video.image.url
                                    print(f'{i}. "{video.title}"')
                                    vidAuthor = str(video.author)
                                    data = {
                                        'video.numer':i,
                                        'video.date':str(video.date),
                                        'video.author': vidAuthor[15:-1],
                                        'video.url': video.url,
                                        'video.image.url': image,
                                        'video.title': video.title
                                        }
                                    FW.write(",")
                                    json.dump(data, FW, ensure_ascii=False,indent=2)  
                    except Exception as e:
                            print(f'ERROR - video = next(videos_iterator)')
                            try:
                                next(videos_iterator)
                            except StopIteration:
                                 break  # Якщо досягнута остання ітерація, вийти з циклу
                            continue  # Продовжуємо цикл без обробки поточної помилки       
                    i+=1        
            delend(name1, 0)
    
    except FileNotFoundError:
        print(f"The file '{name1}' does not exist. Creating the file.")
        # Create the file
        
        
    except Exception as e:
        raise e


def compare_json_files_by_keywords(file1, output_file, video_Url): #Input file and OutputJson
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    if len(video_Url) < 5000:
        print(f'len(video_Url) < 5000 /n')
    else:
        with open(file1, 'r', encoding='utf-8') as f1, open(output_file, 'r', encoding='utf-8') as outputr:
            delend(file1, 0)
            data1 = json.load(f1)
            keywords1 = set(item.get('video.url') for item in data1)
            lines1 = [line.strip() for line in outputr]
            outputr.close()
            OutputList = [extract_keyword(line) for line in lines1 if extract_keyword(line)]
            with open(output_file, 'a', encoding='utf-8') as output:
                missing_items = [item for item in data1 if item.get('video.url') in keywords1 - video_Url]
                output.write(f'---{formatted_datetime}---\n')
                i = 0
                for item in missing_items:
                    if item.get('video.url') not in OutputList:
                        i+=1
                        #print(f'item.get video.url - {item.get('video.url')}')
                        #print(f'OutputList - {OutputList}')
                        print(f'Видалений елемент - {item} /n')
                        output.write(f'Deleted video: {json.dumps(item, ensure_ascii=False,indent=2)}\n')
                print(f'К-сть видалених елементів - {i} /n')

def compare_json_files_by_keywords2(): #Input file and OutputJson
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        with open('listvideo.json', 'r', encoding='utf-8') as f1, open(outputLog, 'r', encoding='utf-8') as outputr:
            delend('listvideo.json', 0)
            data1 = json.load(f1)
            keywords1 = set(item.get('video.url') for item in data1)
            lines1 = [line.strip() for line in outputr]
            outputr.close()
            OutputList = [extract_keyword(line) for line in lines1 if extract_keyword(line)]
            with open(outputLog, 'a', encoding='utf-8') as output:
                #missing_items = [item for item in data1 if item.get('video.url') in keywords1 - video_Url]
                output.write(f'---{formatted_datetime}---\n')
                i = 0
                for i, item in enumerate (data1):
                    try:
                        video = client.get(item.get('video.url'))
                        print(f'{i} = Відео - {video}')
                        print(f'{i} - {video.title}')
                    except Exception as e:
                        if item.get('video.url') not in OutputList:
                            i+=1
                            print(f'Видалений елемент - {item} /n')
                            output.write(f'Deleted video: {json.dumps(item, ensure_ascii=False,indent=2)}\n')
                print(f' Додано {i} нових відео до Output')
           
            
           
                    
                    #if  client.get(url):
                        #print(f'item.get video.url - {item.get('video.url')}')
                        #print(f'OutputList - {OutputList}')
                        #print(f'Видалений елемент - {item} /n')
                        #utput.write(f'Deleted video: {json.dumps(item, ensure_ascii=False,indent=2)}\n')
                #print(f'К-сть видалених елементів - {i} /n')

def build_HTML(file1):
        buildTmp('tmp.json')
        with open(file1, 'r', encoding='utf-8') as dd:
            delend(file1, 0)
            data2 = json.load(dd)
            with open('index.html', 'w', encoding='utf-8') as html_file:
                # Додаємо початок HTML-файлу
                html_file.write('<html>\n<head>\n<title>My HTML Page</title>\n</head>\n<body>\n')
                #if not os.path.exists('img'):
                    #os.makedirs('img')
                # Обробляємо кожен елемент у JSON файлі
                for i, element in enumerate(data2):
                    #if element.get('video.author',{}) != 'BabyDollDiana':
                    # Отримуємо URL зображення
                    image_url = element.get('video.image.url', {})
                    # Якщо URL існує, скачуємо зображення та додаємо тег зображення в HTML файл
                    if image_url:
                        html_file.write(f'<p>-----------------{i}------------------------</p>\n')
                        image_filenamee = f'img/{extract_keyword_key(element.get("video.url", {}))}.jp'
                        #download_image(image_url, image_filename)
                        html_file.write(f'<p>Video url: {element.get('video.url', {})}</p>\n')
                        html_file.write(f'<p><a href="{element.get('video.url', {})}">{element.get('video.url', {})}</a> </p>\n')
                        html_file.write(f'<p>Video img url: {element.get('video.image.url', {})}</p>\n')
                        html_file.write(f'<img src="{image_filenamee}" title="{element.get('video.title', {})}">\n')
                        html_file.write(f'<p>Video title: {element.get('video.title', {})}</p>\n')
                        html_file.write(f'<p>Date: {element.get('video.date', {})}</p>\n')
                        html_file.write(f'<p>Author: {element.get('video.author', {})}</p>\n')
                        html_file.write(f'<p><a href="https://3gpporn.org/video/{extract_keyword_key(element.get("video.url", {}))}">link to 3GPP</a> </p>\n')
                        html_file.write(f'<p><a href="https://duckduckgo.com/?q={element.get("video.title", {})}">link to DUCKDUCKGO</a> </p>\n')
                        html_file.write(f'<p><a href="https://yandex.com/search/?text={element.get("video.title", {})}">link to YANDEX</a> </p>\n')
                        html_file.write(f'<p><a href="https://www.bing.com/search?q={element.get("video.title", {})}">link to BING</a> </p>\n')
                # Додаємо кінець HTML-файлу
                html_file.write('</body>\n</html>')
        print(f'HTML Created /n')

              
def delend(file_path, dela):   # Видалення(1) або добавлення(0) " ] " 
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

def extract_objects_from_file(file_path): # Для tmp4html
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    # Використовуємо регулярний вираз для вилучення об'єктів з рядка
    objects = re.findall(r'\{[^}]*\}', content)
    # Додаємо кому після кожного "}" крім останнього елементу
    modified_content = ','.join(objects)
    # Перетворюємо модифікований вміст у список об'єктів JSON
    modified_objects = json.loads(f'[{modified_content}]')
    return modified_objects

def download_image(url, filename): # Завантаження зобрадення
    if not os.path.exists(filename):
        response = requests.get(url)
        with open(filename, 'wb') as f:
            f.write(response.content)
    return

def tmp4html(name1): #output.json to tmp.json for HTML
    with open(name1, 'r+', encoding='utf-8') as FR,open("tmp.json", 'w', encoding='utf-8') as OUT: 
            delend(name1, 0)
            
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

                  
def extract_keyword(line): #отиримання url відео з рядку json
    match = re.search(pattern, line)
    if match:
        url = match.group(1)
        return(url)

def extract_keyword_key(line): #отиримання key відео
    match = re.search(pattern2, line)
    if match:
        desired_characters = match.group(1)
        return(desired_characters)

def get_file_list(directory): #отиримання Списку файлів
  file_list = set()
  for file in os.listdir(directory):
    if os.path.isfile(os.path.join(directory, file)):
      file_list.add(file)
  return file_list

if __name__ == "__main__":
    input("listvideo.json",  "client.account.watched", videoUrlAll)
    input("MY.json",  "https://rt.pornhub.com/playlist/310163161", videoUrlMy)
    input("Tail.json",  "https://rt.pornhub.com/playlist/185091142", videoUrlTail)
    input("Socks.json",  "https://rt.pornhub.com/playlist/200793251", videoUrlSocks)
    input("Costume.json",  "https://rt.pornhub.com/playlist/228798371", videoUrlCostume)
    #compare_json_files_by_keywords("MY.json", outputLog, videoUrlMy)
    compare_json_files_by_keywords2()
    build_HTML("tmp.json")


    #SortInpList()
    
    