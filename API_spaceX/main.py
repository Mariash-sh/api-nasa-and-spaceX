import requests
import pathlib
import random, os
from time import sleep 
from dotenv import dotenv_values
import urllib3


config = dotenv_values('.env')

# очистка папки 
def clear_folder(folder_path):
    for file in os.listdir(folder_path):
        os.remove(f'{folder_path}/{file}')

# 10 фоток наса
def download_photos_nasa(API_NASA, count=10):
    url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': API_NASA,
        'count': count,
        'hd': True,
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return 'Ошибка! Нет подключения к серверу'
    except urllib3.exceptions.SSLError:
        return 'Ошибка! Несоответсвие версии SSL'
    except urllib3.exceptions.SSLError:
        return 'Ошибка! Несоответсвие версии SSL'
    except requests.exceptions.ConnectionError:
        return 'Нет интернета!'
            
    response = response.json()
    for index, i in enumerate(response):
        if i['media_type'] == 'image':
            image = requests.get(i['url'])
            image.raise_for_status()
            with open(pathlib.Path('nasa', f'image_day{index}.jpg'), 'wb') as file:
                file.write(image.content)
    return 'Успешно загружены 10 фоток Nasa!'

# последний запуск spaceX
def download_last_launch_spaceX():
    url = 'https://api.spacexdata.com/v3/launches/'
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.JSONDecodeError:
        return 'Ошибка! '
    # except:
    #     return 'Ошибка! '
    # except:
    #     return 'Ошибка! '
    except requests.exceptions.ConnectionError:
        return 'Нет интернета!'
    text_image = f'Крайний запуск ракеты SpaceX. Cовершен: {response.json()[::-1][0]['launch_date_local']}!'
    image_links = response.json()[::-1][0]['links']['flickr_images']

    if image_links:
        for index, url in enumerate(image_links):
            image = requests.get(url)
            with open(pathlib.Path('spaceX', f'image_lautch{index}.jpg'), 'wb') as file:
                file.write(image.content)
        return text_image     

    else:
        return 'Картинки Нет!' 


# выбор рандомной фотки из папки
def choice_random_photo_folder(**folder_paths_texts):
    files = []
    for folder, text in folder_paths_texts.items():
        for i, file in enumerate(os.listdir(folder)):
            files.append(f'{folder}/{i}.jpg')  
    photo = random.choice(files)

    for key, value in folder_paths_texts.items():
        if key in photo:
            text = value
    return  photo, text   
    

# отпрака фото в тгк
def send_photo_tgk(TOKEN, ID_chat, photo ,caption):
    url_photo = f'https://api.telegram.org/bot{TOKEN}/sendPhoto' 
    params = {
        'chat_id': ID_chat,
        'caption': caption
    }
    with open(photo, 'rb') as file:
        response = requests.post(url_photo, files={'photo': file}, params=params)
    return response.raise_for_status    




if __name__ == "__main__":   
    API_NASA = config['API_NASA']
    TOKEN = config['TOKEN']
    ID_chat = config['ID_chat']
    
    while True:
        clear_folder('nasa')
        clear_folder('spaceX')
        print(download_photos_nasa(API_NASA, count=10))
        text_image_nasa = 'Картинка дня от Nasa'
        text_image_SpaceX = download_last_launch_spaceX()
        path_text_photo = {
            'nasa': text_image_nasa, 
            'spaceX':text_image_SpaceX
        }
        try:
            photo_path, caption_post = choice_random_photo_folder(**path_text_photo)
            res = send_photo_tgk(config["TOKEN"], ID_chat, photo_path, caption_post)
            print(res)
        except:
            print('Картинок в папке не найдено!')      
        sleep(60*60)