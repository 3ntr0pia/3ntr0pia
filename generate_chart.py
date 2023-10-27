import os
import json
import matplotlib.pyplot as plt

ACCU_FILE = './json_data/accumulated.json'

def get_latest_json_file(path):
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json') and 'accumulated' not in f]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def accumulate_data():
    try:
        latest_json_file = get_latest_json_file('./json_data')
        
        if not latest_json_file:
            print("No JSON files found.")
            return

        with open(latest_json_file, 'r') as f:
            new_data = json.load(f)

        # Check if the data is structured by date
        if not any(isinstance(val, dict) and "languages" in val for val in new_data.values()):
            print(f"El archivo {latest_json_file} no contiene datos válidos.")
            return

        # Extract and sum the languages data from each date
        all_languages = {}
        for date, data in new_data.items():
            for lang in data["languages"]:
                name = lang["name"]
                total_seconds = lang["total_seconds"]
                if name in all_languages:
                    all_languages[name] += total_seconds
                else:
                    all_languages[name] = total_seconds

        # Convert the accumulated data into the expected format
        accumulated_languages = [{"name": name, "total_seconds": total_seconds} for name, total_seconds in all_languages.items()]

        if os.path.exists(ACCU_FILE):
            with open(ACCU_FILE, 'r') as f:
                accu_data = json.load(f)
        else:
            accu_data = {"languages": []}

        for new_lang in accumulated_languages:
            found = False
            for accu_lang in accu_data["languages"]:
                if accu_lang["name"] == new_lang["name"]:
                    accu_lang["total_seconds"] += new_lang["total_seconds"]
                    found = True
                    break
            if not found:
                accu_data["languages"].append(new_lang)

        with open(ACCU_FILE, 'w') as f:
            json.dump(accu_data, f, indent=4)

        return accu_data
    except Exception as e:
        print(f"Error en accumulate_data: {e}")
        return None

def generate_chart():
    try:
        data = accumulate_data()
        if not data:
            print("No se pudo generar la gráfica debido a la falta de datos.")
            return
        languages = data["languages"]
        names = [lang["name"] for lang in languages]
        total_seconds = [lang["total_seconds"] for lang in languages]

        plt.figure(figsize=(10,7))
        plt.barh(names, total_seconds, color='skyblue')
        plt.xlabel('Total Seconds')
        plt.ylabel('Languages')
        plt.title('Languages Used Over Time')
        plt.gca().invert_yaxis()
        plt.tight_layout()
        plt.savefig('./chart.png')
    except Exception as e:
        print(f"Error en generate_chart: {e}")

generate_chart()
