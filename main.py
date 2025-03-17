"""
vkyd Tsvetkov 2025 v1
"""

import tkinter as tk   # GUI
from tkinter import messagebox
from settings_edit import SettingsEditor  # класс редактора настроек
from vk import Vk  # класс Vk
from yd import Yd  # класс Yd
import configparser  # работа с файлом настроек
from time import sleep
import os
from translations import translations  # Импортируем словарь с переводами
import settings as s

class MainApp(tk.Tk):
    def __init__(self, language: str = ""):
        """
        Инициализация главного приложения.
        :param language: Язык интерфейса (ru, en, zh).
        """
        super().__init__()
        # Загружаем настройки
        self.settings_file = "settings.ini"
        self.config = configparser.ConfigParser()
        self.config.read(self.settings_file)
        st = s.Settings()
        if language:
            self.language = language
        else:
            self.language = self.config["other"]["language"]
        # Создаем экземпляры классов Vk и Yd
        self.nm = 'vkyd. '
        self.vk = Vk(
            access_token=self.config["vk"]["token"],
            user_id=self.config["vk"]["user_id"] ,
            language=self.language,
            album_id=st.get_vk_album_id(),
            vk_log_file=st.get_vk_log_filepath(),
            local_folder=st.get_local_folder()
        )

        self.yd = Yd(
            access_token=self.config["yd"]["token"],
            log_file=st.get_yd_log_filepath(),
            save_folder = st.get_yd_save_folder()
        )

        self.upload_file = self.config["yd"]["upload_file"]

        # Создаем главное окно
        self.title(f"{self.nm}Главное меню" if self.language == "ru" else f"{self.nm}Main Menu" if self.language == "en" else f"{self.nm}主菜单")
        self.geometry("360x420+110+70")

        # Кнопки
        self.btn1 = tk.Button(self, text='1', width = 30, command=self.open_settings_editor)
        self.btn1.pack(pady=10)
        self.btn2 = tk.Button(self, text='2', width = 30, command=self.upload_photos_to_yandex)
        self.btn2.pack(pady=10)
        self.btn3 = tk.Button(self, text='3', width = 30, command=self.download_photos_from_vk)
        self.btn3.pack(pady=10)
        self.btn4 = tk.Button(self, text='4',  width = 30,command=self.upload_images_from_folder)
        self.btn4.pack(pady=10)
        self.btn5 = tk.Button(self, text='5',  width = 30,command=self.yd_info)
        self.btn5.pack(pady=10)
        self.btn6 = tk.Button(self, text='6',  width = 30,command=self.yd_folder_check)
        self.btn6.pack(pady=10)
        self.btn7 = tk.Button(self, text='7',  width = 30,command=self.yd_create_folder)
        self.btn7.pack(pady=10)
        self.btn8 = tk.Button(self, text='8',  width = 30,command=self.yd_upload_one_file)
        self.btn8.pack(pady=10)
        self.btn9 = tk.Button(self, text='9',  width = 30,command=self.current_data_set)
        self.btn9.pack(pady=10)
        self.lbl1 = tk.Label(self, text='vkyd Tsvetkov 2025 v1', fg='grey')
        self.lbl1.pack(pady=10)
        self.set_text_btn()
        self.upload_file = self.config["yd"]["upload_file"]

    def set_options(self):
        """
        Установка измененных настроек
        :return:
        """
        st = s.Settings()
        self.language = st.get_language()
        self.vk.access_token=st.get_vk_token()
        self.vk.user_id=st.get_vk_user_id()
        self.vk.language = st.get_language()
        self.vk.album_id=st.get_vk_album_id()
        self.vk.vk_log_file=st.get_vk_log_filepath()
        self.vk.local_folder=st.get_local_folder()

        self.yd.access_token=st.get_yd_token()
        self.yd.language = st.get_language()
        self.yd.log_file=st.get_yd_log_filepath()
        self.yd.save_folder = st.get_yd_save_folder()
        self.upload_file =  st.get_yd_upload_file()
        #print("2",self.yd.save_folder)
        #print("2", self.upload_file)

    def current_data_set(self):
        self.set_options()
        print("Язык сообщений: ", self.vk.language)
        print("Загружаемый файл в yd: ", self.upload_file)
        print("Папка загрузки в yd: ", self.yd.save_folder)
        print("Из локальной папки: ", self.vk.local_folder)

    def open_settings_editor(self):
        """
        Открывает форму редактора настроек.
        """
        self.btn1.config(bg="yellow")
        self.btn1.update()
        # Путь к файлу настроек
        settings_file = "settings.ini"
        # Проверяем, существует ли файл настроек
        if not os.path.exists(settings_file):
            # Создаем файл настроек, если его нет
            st = s.Settings()
            st.create_file_ini(settings_file)

        self.second_form = SettingsEditor(self, self.restore_button_color, self.settings_file)
        self.second_form.transient(self)  # Связываем второе окно с главным

    def restore_button_color(self):
        self.btn1.config(bg="SystemButtonFace")
        self.set_options()
        print('1111')
        print("1",self.yd.get_yd_save_folder())
        self.set_text_btn()

    def set_text_btn(self):
        """
        Меняет текст кнопок главной формы, если изменились настройки
        """
        text1 = translations[self.language]["edit_settings"]
        text2 = translations[self.language]["upload_photos_vk_to_yd"]
        text3 = translations[self.language]["download_photos_from_vk"]
        text4 = translations[self.language]["upload_photos_from_folder_to_yd"]
        text5 = translations[self.language]["yd_info"]
        text6 = translations[self.language]["yd_folder_check"]
        text7 = translations[self.language]["yd_create_folder"]
        text8 = translations[self.language]["yd_upload_one_file"]
        text9 = translations[self.language]["current_data_set"]

        self.btn1.config(text=text1)
        self.btn1.update()
        self.btn2.config(text=text2)
        self.btn2.update()
        self.btn3.config(text=text3)
        self.btn3.update()
        self.btn4.config(text=text4)
        self.btn4.update()
        self.btn5.config(text=text5)
        self.btn5.update()
        self.btn6.config(text=text6)
        self.btn6.update()
        self.btn7.config(text=text7)
        self.btn7.update()
        self.btn8.config(text=text8)
        self.btn8.update()
        self.btn9.config(text=text9)
        self.btn9.update()

    def yd_info(self):
        """
        Вызывает метод класса yd. Информация о диске
        """
        self.btn5.config(bg="yellow")
        self.btn5.update()
        self.set_options()
        print(self.vk.language)
        try:
            print(self.yd.get_disk_info())
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запроса: {e}")
        sleep(1)
        self.btn5.config(bg="SystemButtonFace")

    def yd_folder_check(self):
        """
        Вызывает метод класса yd. проверка папки
        """
        self.btn6.config(bg="yellow")
        self.btn6.update()
        self.set_options()
        print(self.vk.language)
        print("3",self.yd.save_folder)
        try:
            if self.yd.check_folder_exists(self.yd.save_folder):
                print("Папка существует.")
            else:
                print("Папка не существует.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запроса: {e}")
        sleep(1)
        self.btn6.config(bg="SystemButtonFace")

    def yd_create_folder(self):
        """
        Вызывает метод класса yd.
        """
        self.btn7.config(bg="yellow")
        self.btn7.update()
        self.set_options()
        print(self.vk.language)

        try:
            if not self.yd.create_folder(self.yd.get_yd_save_folder()):
                print("Не удалось создать папку. Проверьте, возможно, она уже существует.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запроса: {e}")
        sleep(1)
        self.btn7.config(bg="SystemButtonFace")

    def yd_upload_one_file(self):
        """
        Вызывает метод класса yd.
        """
        self.btn8.config(bg="yellow")
        self.btn8.update()
        self.set_options()
        print(self.vk.language)

        try:
            file_path = self.upload_file  # путь к файлу
            yd_save_dir = self.yd.save_folder
            print(file_path)
            print(yd_save_dir)
            if self.yd.upload_file(file_path, yd_save_dir):
                print("Файл успешно загружен.")
            else:
                print("Не удалось загрузить файл.")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка запроса: {e}")
        sleep(1)
        self.btn8.config(bg="SystemButtonFace")


    def upload_photos_to_yandex(self):
        """
        Вызывает метод upload_photos_to_yandex_disk класса Vk.
        """
        self.btn2.config(bg="yellow")
        self.btn2.update()
        self.set_options()
        try:
            # Получаем список фотографий
            photos_json = self.vk.get_list_photo1()
            # Загружаем фотографии
            if self.vk.upload_photos_to_yandex_disk(photos_json, self.yd, self.config["yd"]["save_folder"]):
                messagebox.showinfo("Успех", "Фотографии успешно загружены на yd")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось загрузить все фотографии.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке фотографий: {e}")
        sleep(1)
        self.btn2.config(bg="SystemButtonFace")

    def download_photos_from_vk(self):
        """
        Вызывает метод download_photos класса Vk.
        """
        self.btn3.config(bg="yellow")
        self.btn3.update()

        self.set_options()
        print(self.vk.language)
        try:
            # Получаем список фотографий
            photos_json = self.vk.get_list_photo1()
            # Скачиваем фотографии
            print('sort_method = ', self.vk.get_vk_sort_method())
            if self.vk.download_photos(photos_json, local_folder=self.vk.local_folder,
                                       sort_method=self.vk.get_vk_sort_method()):
                messagebox.showinfo("Успех", "Фотографии успешно скачаны!")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось скачать все фотографии.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при скачивании фотографий: {e}")
        sleep(1)
        self.btn3.config(bg="SystemButtonFace")


    def upload_images_from_folder(self):
        """
        Вызывает метод upload_images_from_folder класса Yd.
        """
        self.set_options()
        try:
            # Загружаем фотографии из папки
            if self.yd.upload_images_from_folder(local_folder=self.vk.local_folder,
                                                 remote_folder= self.config["yd"]["save_folder"]):
                messagebox.showinfo("Успех", "Фотографии успешно загружены на yd")
            else:
                messagebox.showwarning("Предупреждение", "Не удалось загрузить все фотографии")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при загрузке фотографий: {e}")

    def run(self):
        """
        Запускает главный цикл окна.
        """
        #self.root.mainloop()
        self.mainloop()


if __name__ == '__main__':
    print(">Hello world! Start vkyd")
    # Путь к файлу настроек
    settings_file = "settings.ini"
    st = s.Settings()
    # Проверяем, существует ли файл настроек
    if not os.path.exists(settings_file):
        # Создаем файл настроек, если его нет
        st.create_file_ini(settings_file)
    # Выбор языка варианты (ru, en, zh)
    # language = "ru"
    language = ""
    # Запускаем главное приложение
    app = MainApp(language=language)
    app.run()