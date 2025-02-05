import pandas as pd
import os
import json

def get_data_path():
    home = os.path.expanduser("~")
    data_dir = os.path.join(home, '.my_app_data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    return os.path.join(data_dir, 'data.xlsx')

def get_settings_path():
    home = os.path.expanduser("~")
    settings_dir = os.path.join(home, '.my_app_data')
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)
    return os.path.join(settings_dir, 'settings.json')

class DataManager:
    def load_data(self):
        file_path = get_data_path()
        try:
            if os.path.exists(file_path):
                df = pd.read_excel(file_path)
                return list(df.itertuples(index=False, name=None))
        except Exception as e:
            print(f"Error loading data: {e}")
        return []

    def save_data(self, entries):
        try:
            df = pd.DataFrame(entries, columns=['编号', '姓名'])
            df.to_excel(get_data_path(), index=False)
        except Exception as e:
            print(f"Error saving data: {e}")

    def load_settings(self):
        settings_path = get_settings_path()
        if os.path.exists(settings_path):
            with open(settings_path, 'r') as f:
                return json.load(f)
        return {}

    def save_settings(self, settings):
        settings_path = get_settings_path()
        with open(settings_path, 'w') as f:
            json.dump(settings, f)

    def load_prizes(self):
        prize_file_path = os.path.join(os.path.expanduser("~"), '.my_app_data', 'prizes.json')
        if os.path.exists(prize_file_path):
            with open(prize_file_path, 'r') as f:
                return json.load(f)
        return []

    def save_prizes(self, prizes):
        prize_file_path = os.path.join(os.path.expanduser("~"), '.my_app_data', 'prizes.json')
        with open(prize_file_path, 'w') as f:
            json.dump(prizes, f)