import os
import requests
from urllib.parse import urlparse
import pprint as p
import json
from tqdm import tqdm
from datetime import datetime
import base as b

import settings as s
import httpconst as h


class Vk(b.BaseClass, s.Settings):
    def __init__(self, access_token, user_id, version='', base_url='',
                 album_id='', rev='', extended='', count=0, vk_log_file='',
                 local_folder='', language=""):
        super().__init__(language)  # 1
        super(b.BaseClass, self).__init__(filename='settings.ini')  # 2

        self.token = access_token
        self.id = user_id
        self.version = version or self.get_vk_version()
        self.base_url = base_url or self.get_vk_base_url()
        self.album_id = album_id or self.get_vk_album_id()
        self.rev = rev or self.get_vk_rev()
        self.extended = extended or self.get_vk_extended()
        self.count = count or self.get_vk_count()
        self.params = {'access_token': self.token, 'v': self.version}
        self.vk_log_file = vk_log_file or self.get_vk_log_filepath()
        self.local_folder = local_folder or self.get_local_folder()
        self.language = language or self.get_language()

    def user_info(self):
        """
        Информация о пользователе
        :return: dic
        """
        url = f'{self.base_url}/users.get'
        params = {'user_ids': self.id}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_friends(self, user_id, count=3):
        """
        Получить друзей
        :return: dic
        """
        url = f'{self.base_url}/friends.get'
        params = {
            'user_id': user_id,
            'fields': ['city'],
            'count': count
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

    def user_test(self):
        """
        Проверка параметров
        :return: param
        """
        params = {'user_ids': self.id}
        return params

    def get_list_photo1(self):
        """
        Получить фото. Параметры из полей
        :return: dic
        """
        url = f'{self.base_url}/photos.get'
        params = {'owner_id': self.id, 'album_id': self.album_id, 'rev': self.rev,
                  'extended': self.extended, 'count': self.count}
        response = requests.get(url, params={**self.params, **params})
        return response.json()

    def get_list_photo2(self, user_id, count=3, album_id='profile'):
        """
        Получить фото. Параметры из аргументов
        :param user_id: юзер
        :return: dic
        """
        url = f'{self.base_url}/photos.get'
        params = {
            'owner_id': user_id,
            'count': count,
            'album_id': album_id,
            'extended': 1
        }
        params.update(self.params)
        response = requests.get(url, params=params)
        return response.json()

    def _sort_photos_by_likes(self, photos_json):
        """
        Сортирует фотографии по количеству лайков (по убыванию).
        :param photos_json: JSON-ответ с фотографиями.
        :return: Отсортированный список фотографий.
        """
        items = photos_json.get("response", {}).get("items", [])
        if not items:
            print("Нет фотографий для сортировки.")
            return []

        # Сортируем фотографии по количеству лайков (по убыванию)
        sorted_items = sorted(items, key=lambda x: x.get("likes", {}).get("count", 0), reverse=True)
        return sorted_items

    def _sort_photos_by_date(self, photos_json, reverse: bool = 0):
        """
        Сортирует фотографии по дате (по убыванию).
        :param photos_json: JSON-ответ с фотографиями.
        :return: Отсортированный список фотографий.
        """
        items = photos_json.get("response", {}).get("items", [])
        if not items:
            print("Нет фотографий для сортировки.")
            return []

        # Сортируем фотографии по дате
        sorted_items = sorted(items, key=lambda x: x['date'], reverse=reverse)
        return sorted_items

    def _generate_file_name(self, photo_url: str, owner_id: int, photo_id: int, likes_count: int,
                            name_with_likes: bool) -> str:
        """
        Генерирует имя файла на основе URL фотографии и параметров.
        :param photo_url: URL фотографии.
        :param owner_id: ID владельца фотографии.
        :param photo_id: ID фотографии.
        :param likes_count: Количество лайков.
        :param name_with_likes: Если True, добавляет количество лайков в имя файла.
        :return: Сгенерированное имя файла.
        """
        # Извлекаем расширение файла из URL
        parsed_url = urlparse(photo_url)
        file_extension = os.path.splitext(parsed_url.path)[1]  # Например, ".jpg"

        # Формируем имя файла
        if name_with_likes:
            file_name = f"{owner_id}_{photo_id}_{likes_count}{file_extension}"
        else:
            file_name = f"{owner_id}_{photo_id}{file_extension}"

        return file_name

    def download_photos(self, photos_json, local_folder: str, sort_method: int = 1,
                        name_with_likes: bool = False) -> bool:
        """
        Скачивает фотографии из JSON-ответа ВКонтакте в указанную локальную папку.
        :param photos_json: JSON-ответ с фотографиями.
        :param local_folder: Локальная папка для сохранения фотографий.
        :param sort_method: Если 1 = сортирует фотографии по количеству лайков,
        2= сортируем по дате сначала ранние, 3=сортируем по дате сначала поздние
        :param name_with_likes: Если True, добавляет количество лайков в имя файла.
        :return: True, если все фотографии успешно скачаны, иначе False.
        """
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)  # Создаем папку, если она не существует
            print(self.get_message("folder_created"))

        items = photos_json.get("response", {}).get("items", [])
        if not items:
            print(self.get_message("no_photos"))
            return False

        # Сортируем фотографии по лайкам, если нужно
        if int(sort_method) == 1:
            items = self._sort_photos_by_likes(photos_json)
        elif int(sort_method) == 2:
            items = self._sort_photos_by_date(photos_json, reverse=False)
        elif int(sort_method) == 3:
            items = self._sort_photos_by_date(photos_json, reverse=True)

        success_count = 0
        logs = []  # Список для хранения логов

        # Используем tqdm для отображения прогресса
        for item in tqdm(items, desc=self.get_message("download_photos"), unit="фото"):
            photo_id = item.get("id")
            owner_id = item.get("owner_id")
            likes_count = item.get("likes", {}).get("count", 0)  # Количество лайков
            sizes = item.get("sizes", [])

            # Выбираем изображение с максимальным разрешением
            max_size = max(sizes, key=lambda x: x.get("width", 0) * x.get("height", 0))
            photo_url = max_size.get("url")

            if not photo_url:
                print(self.get_message("file_not_found"))
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "file_name": f"{owner_id}_{photo_id}",
                    "status": "error",
                    "message": self.get_message("no_photo_url")
                })
                continue

            # Генерируем имя файла
            file_name = self._generate_file_name(photo_url, owner_id, photo_id, likes_count, name_with_likes)
            file_path = os.path.join(local_folder, file_name)

            # Скачиваем фотографию
            try:
                response = requests.get(photo_url)
                if response.status_code == h.HTTP_STATUS_OK:
                    # Сохраняем файл
                    with open(file_path, "wb") as file:
                        file.write(response.content)
                    # print(self.get_message("download_success")) //мешает прогресс бару
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "file_name": file_name,
                        "status": "success",
                        "message": self.get_message("download_success")
                    })
                    success_count += 1
                else:
                    print(self.get_message("download_error"))
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "file_name": file_name,
                        "status": "error",
                        "message": f"{self.get_message('download_error')}: {response.status_code}"
                    })
            except Exception as e:
                print(self.get_message("network_error"))
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "file_name": file_name,
                    "status": "error",
                    "message": f"print(self.get_message('network_error')): {str(e)}"
                })

        # Сохраняем логи в файл
        log_file = os.path.join(local_folder, "download_log.json")
        try:
            with open(log_file, "w", encoding="utf-8") as file:
                json.dump(logs, file, indent=4, ensure_ascii=False)
            print(f"Логи сохранены в файл: {log_file}")
        except Exception as e:
            print(f"Ошибка при сохранении логов: {e}")

        print(f"{self.get_message('download_success')}: {success_count}/{len(items)}")
        return success_count == len(items)

    def upload_photos_to_yandex_disk(self, photos_json, yd_instance, remote_folder: str, sort_method: int = 1,
                                     name_with_likes: bool = False) -> bool:
        """
        Загружает фотографии из ВКонтакте напрямую на Яндекс.Диск.
        :param photos_json: JSON-ответ с фотографиями.
        :param yd_instance: Экземпляр класса Yd для работы с Яндекс.Диском.
        :param remote_folder: Папка на Яндекс.Диске для сохранения фотографий.
        :param sort_method: Если 1, сортирует фотографии по количеству лайков.
        :param name_with_likes: Если True, добавляет количество лайков в имя файла.
        :return: True, если все фотографии успешно загружены, иначе False.
        """
        items = photos_json.get("response", {}).get("items", [])
        if not items:
            print("Нет фотографий для загрузки.")
            return False

        # Сортируем фотографии по лайкам, если нужно
        if int(sort_method) == 1:
            items = self._sort_photos_by_likes(photos_json)
        elif int(sort_method) == 2:
            items = self._sort_photos_by_date(photos_json, reverse=False)
        elif int(sort_method) == 3:
            items = self._sort_photos_by_date(photos_json, reverse=True)

        success_count = 0
        skipped_count = 0
        logs = []  # Список для хранения логов

        # Используем tqdm для отображения прогресса
        for item in tqdm(items, desc="Загрузка фотографий на Яндекс.Диск", unit="фото"):
            photo_id = item.get("id")
            owner_id = item.get("owner_id")
            likes_count = item.get("likes", {}).get("count", 0)  # Количество лайков
            sizes = item.get("sizes", [])

            # Выбираем изображение с максимальным разрешением
            max_size = max(sizes, key=lambda x: x.get("width", 0) * x.get("height", 0))
            photo_url = max_size.get("url")

            if not photo_url:
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "file_name": f"{owner_id}_{photo_id}",
                    "status": "error",
                    "message": "Не удалось получить URL для фотографии."
                })
                continue

            # Генерируем имя файла
            file_name = self._generate_file_name(photo_url, owner_id, photo_id, likes_count, name_with_likes)

            # Скачиваем фотографию
            try:
                response = requests.get(photo_url)
                if response.status_code == h.HTTP_STATUS_OK:
                    # Загружаем фотографию на Яндекс.Диск
                    result = yd_instance.upload_file_from_memory(file_name, remote_folder, response.content)
                    if result == 1:
                        logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "file_name": file_name,
                            "status": "success",
                            "message": "Фотография успешно загружена на yd"
                        })
                        success_count += 1
                    elif result == 2:
                        logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "file_name": file_name,
                            "status": "skipped",
                            "message": "Файл уже существует на yd."
                        })
                        skipped_count += 1
                    else:
                        logs.append({
                            "timestamp": datetime.now().isoformat(),
                            "file_name": file_name,
                            "status": "error",
                            "message": "Ошибка при загрузке на yd"
                        })
                else:
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "file_name": file_name,
                        "status": "error",
                        "message": f"Ошибка при скачивании: {response.status_code}"
                    })
            except Exception as e:
                logs.append({
                    "timestamp": datetime.now().isoformat(),
                    "file_name": file_name,
                    "status": "error",
                    "message": f"Ошибка при скачивании: {str(e)}"
                })

        # Сохраняем логи в файл
        log_file = "upload_to_yandex_log.json"
        try:
            with open(log_file, "w", encoding="utf-8") as file:
                json.dump(logs, file, indent=4, ensure_ascii=False)
            print(f"Логи сохранены в файл: {log_file}")
        except Exception as e:
            print(f"Ошибка при сохранении логов: {e}")

        print(f"Успешно загружено {success_count} из {len(items)} фотографий на YD.")
        print(f"Пропущено {skipped_count} файлов (уже существуют).")
        return success_count == len(items)


if __name__ == '__main__':
    print(">Test VK")
    import yd as y

    st = s.Settings()
    try:
        vk_token = st.get_vk_token()
        vk_user_id = st.get_vk_user_id()
        vk_album_id = st.get_vk_album_id()
        vk_rev = st.get_vk_rev()
        vk_extended = st.get_vk_extended()
        vk_count = st.get_vk_count()
        local_folder = st.get_local_folder()
        vk_name_with_likes = st.get_vk_name_with_likes()
        vk_sort_method = st.get_vk_method()
        yd_token = st.get_yd_token()
        remote_folder = st.get_yd_save_folder()
        vk_log = st.get_vk_log_filepath()
        language = st.get_language()  # Получаем язык из настроек

        print(f"VK Token: {vk_token}")
        print(f"VK User ID: {vk_user_id}")
        print(f"Album ID: {vk_album_id}")
        print(f"VK rev: {vk_rev}")
        print(f"VK ext: {vk_extended}")
        print(f"VK cou: {vk_count}")
        print(f"l_folder: {local_folder}")
        print(f"Remote Folder: {remote_folder}")
        print(f"vk_log_file: {vk_log}")

        vk = Vk(vk_token, vk_user_id, language=language)
        yd = y.Yd(yd_token)

        num_test = 3
        print("Num_test", num_test)
        if num_test == 1:
            print(vk.user_test())
            print(vk.user_info())

        # Получаем список фотографий
        photos_json = vk.get_list_photo1()
        if num_test == 2:
            p.pprint(photos_json)

        # Скачиваем фотографии, отсортированные по количеству лайков
        if num_test == 3:
            if vk.download_photos(photos_json, local_folder,
                                  sort_method=vk_sort_method,
                                  name_with_likes=vk_name_with_likes):
                print(vk.get_message("download_success"))
            else:
                print(vk.get_message("download_error"))

        # Загружаем фотографии напрямую на Яндекс.Диск
        if num_test == 4:
            if vk.upload_photos_to_yandex_disk(photos_json, yd, remote_folder, sort_method=1,
                                               name_with_likes=True):
                print("Все фотографии успешно загружены на YD")
            else:
                print("Не удалось загрузить все фотографии на YD.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
