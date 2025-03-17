import requests # работа с запросами
import os   #  работа с файлами
from typing import List, Dict, Any, Optional
from tqdm import tqdm  # Для отображения прогресса
import json  # Для логирования в json
from datetime import datetime

# Получаем настройки
import settings as s
# Константы для HTTP-статусов
import httpconst as h
from base import BaseClass


class Yd(BaseClass, s.Settings):

    def __init__(self,
                 access_token: str,
                 base_url: str = '',
                 log_file: str = '', language='', save_folder =''
                 ):
        """
        Инициализация класса для работы с Яндекс.Диском.
        :param access_token: OAuth-токен для доступа к API Яндекс.Диска.
        :param base_url: Базовый URL API Яндекс.Диска.
        """
        super().__init__(language) # 1
        super(BaseClass, self).__init__(filename='settings.ini')  # 2

        self.token = access_token
        self.base_url = base_url or self.get_yd_base_url()
        self.headers = {"Authorization": f"OAuth {access_token}"}
        self.log_file = log_file or self.get_yd_log_filepath() # Файл для логирования
        self.language = language or self.get_language()
        self.save_folder = save_folder or self.get_yd_save_folder()

    # Информация о диске
    def get_disk_info(self):
        """
        Выдает инф о YD
        :return: dic, иначе None.
        """
        url = self.base_url
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == h.HTTP_STATUS_OK:
                print(self.get_message("response_ok"))
                return response.json()
            else:
                print(f'{self.get_message("network_error")} : {response.status_code} - {response.text}')
                return None
        except requests.exceptions.RequestException as e:
            print(f'{self.get_message("network_error")} : {e}')
            return None


    def check_folder_exists(self, folder_name: str) -> bool:
        """
        Проверяет, существует ли папка на Яндекс.Диске.
        :param folder_name: Имя папки.
        :return: True, если папка существует, иначе False.
        """
        params = {"path": f"/{folder_name}"}
        url=self.base_url+'resources'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == h.HTTP_STATUS_OK:
                return True
            elif response.status_code == h.HTTP_STATUS_NOT_FOUND:
                return False
            else:
                print(f"Ошибка при проверке папки: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return False

    def create_folder(self, folder_name: str) -> bool:
        """
        Создает папку на Яндекс.Диске.
        :param folder_name: Имя папки, которую нужно создать.
        :return: True, если папка создана успешно, иначе False.
        """
        if self.check_folder_exists(folder_name):
            print(f"Папка '{folder_name}' уже существует.")
            return True

        params = {"path": f"/{folder_name}"}
        url = self.base_url + 'resources'
        try:
            response = requests.put(url, headers=self.headers, params=params)
            if response.status_code == h.HTTP_STATUS_CREATED:
                print(f"Папка '{folder_name}' успешно создана.")
                return True
            elif response.status_code == h.HTTP_STATUS_CONFLICT:
                print(f"Папка '{folder_name}' уже существует.")
                return False
            else:
                print(f"Ошибка при создании папки: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return False

    def upload_file(self, file_path: str, folder_name: str, overwrite: bool = False) -> int:
        """
        Загружает файл в указанную папку на Яндекс.Диске.
        :param file_path: Локальный путь к файлу.
        :param folder_name: Имя папки на Яндекс.Диске.
        :param overwrite: Перезаписывать файл, если он уже существует.
        :return:
            0 - Общая ошибка (не загружен).
            1 - Загружен успешно.
            2 - Не загружен, потому что уже существует.
        """
        if not os.path.exists(file_path):
            print(f"Файл '{file_path}' не найден.")
            return 0

        # Получаем имя файла из пути
        file_name = os.path.basename(file_path)

        # Проверяем, существует ли файл на Яндекс.Диске
        if not overwrite and self._check_file_exists(folder_name, file_name):
            print(f"Файл '{file_name}' уже существует в папке '{folder_name}'. Пропускаем.")
            return 2

        # Получаем ссылку для загрузки
        upload_url = self._get_upload_url(folder_name, file_name)
        if not upload_url:
            return 0

        # Загружаем файл
        try:
            with open(file_path, "rb") as file:
                response = requests.put(upload_url, files={"file": file})
                if response.status_code == 201:
                    print(f"Файл '{file_name}' успешно загружен в папку '{folder_name}'.")
                    return 1
                else:
                    print(f"Ошибка при загрузке файла: {response.status_code} - {response.text}")
                    return 0
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return 0


    def _check_file_exists(self, folder_name: str, file_name: str) -> bool:
        """
        Проверяет, существует ли файл в указанной папке на Яндекс.Диске.
        :param folder_name: Имя папки на Яндекс.Диске.
        :param file_name: Имя файла.
        :return: True, если файл существует, иначе False.
        """
        params = {"path": f"/{folder_name}/{file_name}"}
        url = self.base_url + 'resources'
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == h.HTTP_STATUS_OK:
                return True
            elif response.status_code == h.HTTP_STATUS_NOT_FOUND:
                return False
            else:
                print(f"Ошибка при проверке файла: {response.status_code} - {response.text}")
                return False
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return False


    def _get_upload_url(self, folder_name: str, file_name: str) -> Optional[str]:
        """
        Получает ссылку для загрузки файла на Яндекс.Диск.
        :param folder_name: Имя папки на Яндекс.Диске.
        :param file_name: Имя файла.
        :return: Ссылка для загрузки или None в случае ошибки.
        """
        params = {
            "path": f"/{folder_name}/{file_name}",
            "overwrite": "true"  # Перезаписывать файл, если он уже существует
        }
        url = self.base_url + 'resources'
        try:
            response = requests.get(f"{url}/upload", headers=self.headers, params=params)
            if response.status_code == h.HTTP_STATUS_OK:
                return response.json().get("href")
            else:
                print(f"Ошибка при получении ссылки для загрузки: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return None

    def _log_to_file(self, log_data: Dict[str, Any]):
        """
        Записывает данные в лог-файл в формате JSON.
        :param log_data: Данные для логирования.
        """
        try:
            # Если файл существует, читаем его содержимое
            if os.path.exists(self.log_file):
                with open(self.log_file, "r", encoding="utf-8") as file:
                    logs = json.load(file)
            else:
                logs = []

            # Добавляем новые данные
            logs.append(log_data)

            # Записываем обновленные данные обратно в файл
            with open(self.log_file, "w", encoding="utf-8") as file:
                json.dump(logs, file, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка при записи в лог-файл: {e}")


    def upload_images_from_folder(self, local_folder: str, remote_folder: str, overwrite: bool = False) -> bool:
        """
        Загружает все изображения из указанной локальной папки в папку на Яндекс.Диске.
        :param local_folder: Локальная папка с изображениями.
        :param remote_folder: Папка на Яндекс.Диске.
        :param overwrite: Перезаписывать файлы, если они уже существуют.
        :return: True, если все файлы загружены успешно, иначе False.
        """
        if not os.path.isdir(local_folder):
            print(f"Локальная папка '{local_folder}' не существует.")
            return False

        # Получаем список всех файлов в папке
        image_files = self._get_image_files(local_folder)
        if not image_files:
            print(f"В папке '{local_folder}' нет изображений.")
            return False

        # Создаем папку на Яндекс.Диске, если она не существует
        if not self.create_folder(remote_folder):
            print(f"Не удалось создать папку '{remote_folder}' на Яндекс.Диске.")
            return False

        # Загружаем файлы с отображением прогресса
        success_count = 0
        skipped_count = 0
        failed_files = []  # Список для хранения информации о неудачных загрузках

        for file_path in tqdm(image_files, desc="Загрузка файлов", unit="file"):
            try:
                result = self.upload_file(file_path, remote_folder, overwrite)
                if result == 1:
                    success_count += 1
                    # Логируем успешную загрузку
                    self._log_to_file({
                        "timestamp": datetime.now().isoformat(),
                        "file_path": file_path,
                        "status": "success",
                        "message": "Файл успешно загружен."
                    })
                elif result == 2:
                    skipped_count += 1
                    # Логируем пропуск файла
                    self._log_to_file({
                        "timestamp": datetime.now().isoformat(),
                        "file_path": file_path,
                        "status": "skipped",
                        "message": "Файл уже существует на Яндекс.Диске."
                    })
                else:
                    failed_files.append((file_path, "Ошибка при загрузке файла"))
                    # Логируем ошибку
                    self._log_to_file({
                        "timestamp": datetime.now().isoformat(),
                        "file_path": file_path,
                        "status": "error",
                        "message": "Ошибка при загрузке файла."
                    })
            except Exception as e:
                failed_files.append((file_path, str(e)))
                # Логируем исключение
                self._log_to_file({
                    "timestamp": datetime.now().isoformat(),
                    "file_path": file_path,
                    "status": "error",
                    "message": str(e)
                })

        # Выводим итоговый отчет
        print(f"Загружено {success_count} из {len(image_files)} файлов.")
        print(f"Пропущено {skipped_count} файлов (уже существуют).")
        if failed_files:
            print("\nОшибки при загрузке файлов:")
            for file_path, error in failed_files:
                print(f"- Файл: {file_path}, Ошибка: {error}")

        return success_count == len(image_files)


    def _get_image_files(self, folder: str) -> List[str]:
        """
        Возвращает список путей к изображениям в указанной папке.
        :param folder: Локальная папка.
        :return: Список путей к изображениям.
        """
        supported_extensions = [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff"]
        image_files = []
        for root, _, files in os.walk(folder):
            for file in files:
                if any(file.lower().endswith(ext) for ext in supported_extensions):
                    image_files.append(os.path.join(root, file))
        return image_files


    def upload_file_from_memory(self, file_name: str, remote_folder: str, file_content: bytes) -> int:
        """
        Загружает файл из памяти на Яндекс.Диск.
        :param file_name: Имя файла.
        :param remote_folder: Папка на Яндекс.Диске.
        :param file_content: Содержимое файла в виде байтов.
        :return:
            0 - Общая ошибка (не загружен).
            1 - Загружен успешно.
            2 - Не загружен, потому что уже существует.
        """
        # Проверяем, существует ли файл на Яндекс.Диске
        if self._check_file_exists(remote_folder, file_name):
            print(f"Файл '{file_name}' уже существует в папке '{remote_folder}'. Пропускаем.")
            return 2

        # Получаем ссылку для загрузки
        upload_url = self._get_upload_url(remote_folder, file_name)
        if not upload_url:
            return 0

        # Загружаем файл
        try:
            response = requests.put(upload_url, data=file_content)
            if response.status_code == 201:
                #print(f"Файл '{file_name}' успешно загружен в папку '{remote_folder}'.")  // мешает прогресс бару
                return 1
            else:
                print(f"Ошибка при загрузке файла: {response.status_code} - {response.text}")
                return 0
        except requests.exceptions.RequestException as e:
            print(f"Ошибка сети: {e}")
            return 0


if __name__ == '__main__':
    print(">Test YD")

    st = s.Settings()
    try:
        yd_token = st.get_yd_token()
        yd_save_dir = st.get_yd_save_folder()

        if not yd_token:
            raise ValueError("Токен Яндекс.Диска не найден.")
        if not yd_save_dir:
            raise ValueError("Папка для сохранения не указана.")

        print(f"YD Token: {yd_token}")
        print(f"Save dir: {yd_save_dir}")

        yd = Yd(yd_token)

        test_num = 1
        print("Num_test", test_num)
        # Информация о диске
        if test_num == 1:
            print(yd.get_disk_info())

        # Проверяем наличие папки на YD
        if test_num==2:
            if yd.check_folder_exists(yd_save_dir):
                print("Папка существует.")
            else:
                print("Папка не существует.")

        # Создаем папку, если она не существует
        if test_num==3:
            if not yd.create_folder(yd_save_dir):
                print("Не удалось создать папку. Проверьте, возможно, она уже существует.")

        # Загружаем файл
        if test_num==4:
            file_path = "c:/test1/photo.jpg"  # путь к файлу
            if yd.upload_file(file_path, yd_save_dir):
                print("Файл успешно загружен.")
            else:
                print("Не удалось загрузить файл.")

        # Указываем локальную папку с изображениями
        local_folder = "c:/test1/images"  # путь к локальной папке

        # Загружаем все изображения из папки
        if test_num==5:
            if yd.upload_images_from_folder(local_folder, yd_save_dir, overwrite=False):
                print("Все файлы успешно загружены.")
            else:
                print("Не удалось загрузить все файлы.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")