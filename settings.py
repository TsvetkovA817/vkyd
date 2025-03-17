import configparser as ini
import os


class Settings:
    def __init__(self, filename='settings.ini', vk_token=None,
                 vk_user_id=None, yd_token=None, vk_album_id='', yd_save_folder=None,
                 vk_rev=0, vk_extended=0, vk_count=0, local_folder='', vk_version='',
                 vk_base_url='', vk_log_file='', yd_base_url='', yd_upload_file='',
                 yd_log_file='', vk_sort_method=0, vk_name_with_likes=0,
                 language=''):
        self.file = filename
        self.__settings = self.__read_settings()  # Прочитали настройки в конструкторе
        self.__vk_token = ""
        self.__yd_token = ""
        self.set_vk_token(vk_token)
        self.set_yd_token(yd_token)
        self.__vk_user_id = vk_user_id or self.__settings.get('vk', 'user_id', fallback=None)
        self.__vk_album_id = vk_album_id or self.__settings.get('vk', 'album_id', fallback=None)
        self.__yd_save_folder = yd_save_folder or self.__settings.get('yd', 'save_folder', fallback=None)
        self.__vk_rev = vk_rev or self.__settings.get('vk', 'rev', fallback=None)
        self.__vk_extended = vk_extended or self.__settings.get('vk', 'extended', fallback=None)
        self.__vk_count = vk_count or self.__settings.get('vk', 'count', fallback=None)
        self.__vk_base_url = vk_base_url or self.__settings.get('vk', 'base_url', fallback=None)
        self.__yd_base_url = yd_base_url or self.__settings.get('yd', 'base_url', fallback=None)
        self.__local_folder = local_folder or self.__settings.get('other', 'local_folder', fallback=None)
        self.__vk_version = vk_version or self.__settings.get('vk', 'version', fallback=None)
        self.__vk_log_file = vk_log_file or self.__settings.get('vk', 'log_file', fallback=None)
        self.__yd_log_file = yd_log_file or self.__settings.get('yd', 'log_file', fallback=None)
        self.__vk_sort_method = vk_sort_method or self.__settings.get('vk', 'sort_method', fallback=None)
        self.__vk_name_with_likes = vk_name_with_likes or self.__settings.get('vk', 'name_with_likes', fallback=None)
        self.__language = language or self.__settings.get('other', 'language', fallback=None)
        self.__yd_upload_file = yd_upload_file or self.__settings.get('yd', 'upload_file', fallback=None)

    def __read_settings(self):
        cfg = ini.ConfigParser()
        if self.file and os.path.exists(self.file):
            try:
                cfg.read(self.file)
                return cfg
            except Exception as e:
                print(f"Ошибка при чтении файла с настройками '{self.file}': {e}")
                return ini.ConfigParser()  # Возвращаем пустой объект
        else:
            print(f"Файл настроек '{self.file}' не найден.")
            return ini.ConfigParser()  # Пустой объект

    def create_file_ini(self, settings_file):
        print("Создаем файл настроек")
        config = ini.ConfigParser()
        config["vk"] = {
            "token": "your_vk_token",
            "user_id": "your_vk_user_id",
            "album_id": "wall",
            "rev": "0",
            "extended": "1",
            "count": "3"
        }
        config["yd"] = {
            "token": "your_yd_token",
            "upload_file": "c:/test2/test1.txt"
        }
        config["other"] = {
            "language": "ru",
            "local_folder": "c:/test2"
        }
        with open(settings_file, "w") as configfile:
            config.write(configfile)

    def _check_len(self, s: str = '', lmin: int = 0, lmax: int = 0) -> bool:
        if s and lmin < len(s.strip()) <= lmax:
            return True
        else:
            return False

    def _check_str_attr(self, attr: str = '', lmin: int = 0, lmax: int = 0,
                        part: str = '', name_attr: str = '') -> str:
        if self._check_len(attr, lmin, lmax):
            return attr.strip()
        else:
            res = self.__settings.get(part, name_attr, fallback=None)
            if self._check_len(res, lmin, lmax):
                return res.strip()
            else:
                print(f"wrong {part} {name_attr}")
                return ''

    def get_vk_token(self):
        return self.__vk_token

    def set_vk_token(self, token):
        self.__vk_token = self._check_str_attr(token, 40, 200, 'vk', 'token')

    def get_yd_token(self):
        return self.__yd_token

    def set_yd_token(self, token):
        self.__yd_token = self._check_str_attr(token, 40, 80, 'yd', 'token')

    def get_vk_user_id(self):
        return self.__vk_user_id

    def set_vk_user_id(self, id):
        self.__vk_user_id = id

    def get_vk_album_id(self):
        return self.__vk_album_id

    def set_vk_album_id(self, id):
        self.__vk_album_id = id

    def get_yd_save_folder(self):
        return self.__yd_save_folder

    def set_yd_save_folder(self, yd_save_folder):
        self.__yd_save_folder = yd_save_folder

    def get_vk_rev(self):
        return self.__vk_rev

    def set_vk_rev(self, rev):
        self.__vk_rev = rev

    def get_vk_extended(self):
        return self.__vk_extended

    def set_vk_extended(self, extended):
        self.__vk_extended = extended

    def get_vk_count(self):
        return self.__vk_count

    def set_vk_count(self, count):
        self.__vk_count = count

    def get_vk_version(self):
        return self.__vk_version

    def set_vk_version(self, version):
        self.__vk_version = version

    def get_local_folder(self):
        return self.__local_folder

    def set_local_folder(self, local_folder):
        self.__local_folder = local_folder

    def get_vk_log_filepath(self):
        return self.__vk_log_file

    def set_vk_log_filepath(self, log_file):
        self.__vk_log_file = log_file

    def get_yd_log_filepath(self):
        return self.__yd_log_file

    def set_yd_log_filepath(self, log_file):
        self.__yd_log_file = log_file

    def get_vk_base_url(self):
        return self.__vk_base_url

    def set_vk_base_url(self, base_url):
        self.__vk_base_url = base_url

    def get_yd_base_url(self):
        return self.__yd_base_url

    def set_yd_base_url(self, base_url):
        self.__yd_base_url = base_url

    def get_vk_sort_method(self):
        return self.__vk_sort_method

    def set_vk_sort_method(self, sort_method):
        self.__vk_sort_method = sort_method

    def get_vk_name_with_likes(self):
        return self.__vk_name_with_likes

    def set_vk_name_with_likes(self, name_with_likes):
        self.__vk_name_with_likes = name_with_likes

    def get_language(self):
        return self.__language

    def set_language(self, language):
        self.__language = language

    def get_yd_upload_file(self):
        return self.__yd_upload_file

    def set_yd_upload_file(self, upload_file):
        self.__yd_upload_file = upload_file


if __name__ == '__main__':
    print(">Test. Getting settings")
    st = Settings()
    try:
        v_token = st.get_vk_token()
        y_token = st.get_yd_token()
        v_baseurl = st.get_vk_base_url()
        v_user_id = st.get_vk_user_id()
        v_album_id = st.get_vk_album_id()
        y_save_dir = st.get_yd_save_folder()
        v_rev = st.get_vk_rev()
        v_extended = st.get_vk_extended()
        v_count = st.get_vk_count()
        l_folder = st.get_local_folder()
        vk_log = st.get_vk_log_filepath()
        yd_log = st.get_yd_log_filepath()
        vk_baseurl = st.get_vk_base_url()
        vk_name_with_likes = st.get_vk_name_with_likes()
        vk_sort_method = st.get_vk_sort_method()

        print(f"VK Token: {v_token}")
        print(f"YD Token: {y_token}")
        print(f"VK User ID: {v_user_id}")
        print(f"Album ID: {v_album_id}")
        print(f"Save dir: {y_save_dir}")
        print(f"VK rev: {v_rev}")
        print(f"VK ext: {v_extended}")
        print(f"VK cou: {v_count}")
        print(f"l_folder: {l_folder}")
        print(f"v_log_file: {vk_log}")
        print(f"y_log_file: {yd_log}")
        print(f"v_base_url: {vk_baseurl}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
