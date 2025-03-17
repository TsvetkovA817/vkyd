import tkinter as tk
from tkinter import messagebox
import configparser
import os

class SettingsEditor(tk.Toplevel):

    def __init__(self, parent, on_close_callback, settings_file: str):
        super().__init__(parent)
        self.title("Редактор настроек")
        self.geometry("650x730")
        # Позиция второго окна относительно главного окна
        parent_x = parent.winfo_x()  # Получаем X- гл окна
        parent_y = parent.winfo_y()  # Y
        self.geometry(f"+{parent_x + 150}+{parent_y + 80}")  # Смещение  вправо и вниз
        self.on_close_callback = on_close_callback
        self.focus_force()  #  фокус на второе окно

        # обработчик закрытия
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.settings_file = settings_file
        self.config = configparser.ConfigParser()
        self.config.read(settings_file)

        # Поля для редактирования настроек
        self.entries = {}
        self.create_form()

        # Кнопки "Сохранить" и "Отмена"
        save_button = tk.Button(self, text="Сохранить", command=self.save_settings)
        cancel_button = tk.Button(self, text="Отмена", command=self.on_close)

        # Размещаем кнопки внизу окна
        save_button.grid(row=100, column=0, padx=10, pady=10, sticky=tk.W)
        cancel_button.grid(row=100, column=1, padx=10, pady=10, sticky=tk.E)

    def on_close(self):
        # callback когда окно закр.
        self.on_close_callback()
        self.destroy()  # закрыть окно

    def create_form(self):
        """
        Создает форму для редактирования настроек.
        """
        row = 0
        for section in self.config.sections():
            # Добавляем заголовок секции
            tk.Label(self, text=f"[{section}]", font=("Arial", 12, "bold")).grid(row=row, column=0, columnspan=2, pady=5)
            row += 1

            for key, value in self.config[section].items():
                # Добавляем поле для редактирования
                tk.Label(self, text=key).grid(row=row, column=0, padx=10, pady=5, sticky=tk.W)

                entry_width = 80
                entry = tk.Entry(self, width=entry_width)
                entry.insert(0, value)
                entry.grid(row=row, column=1, padx=10, pady=5, sticky=tk.EW)
                self.entries[(section, key)] = entry
                row += 1

    def save_settings(self):
        """
        Сохраняет изменения в файл настроек.
        """
        try:
            for (section, key), entry in self.entries.items():
                self.config[section][key] = entry.get()

            with open(self.settings_file, "w") as configfile:
                self.config.write(configfile)

            messagebox.showinfo("Успех", "Настройки успешно сохранены!")
            self.on_close()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")

    def run(self):
        """
        Запускает цикл окна.
        """
        self.mainloop()


if __name__ == '__main__':
    # Путь к файлу настроек
    settings_file = "settings.ini"
    # Проверяем, существует ли файл настроек
    if not os.path.exists(settings_file):
        # Создаем файл настроек, если его нет
        import settings as s
        st = s.Settings()
        st.create_file_ini(settings_file)

    # Запускаем редактор настроек
    editor = SettingsEditor(settings_file)
    editor.run()