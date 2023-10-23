import os
import json
import matplotlib.pyplot as plt

ACCU_FILE = './json_data/accumulated.json'

def get_latest_json_file(path):
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json') and 'accumulated' not in f]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None

def accumulate_data():
    latest_json_file = get_latest_json_file('./json_data')
    
    if not latest_json_file:
        print("No JSON files found.")
        return

    with open(latest_json_file, 'r') as f:
        new_data = json.load(f)

    # Aquí estamos asegurándonos de que cada archivo JSON tenga la clave "languages"
    # y que el arreglo no esté vacío antes de continuar.
    if "languages" not in new_data or not new_data["languages"]:
        print(f"El archivo {latest_json_file} no contiene datos válidos.")
        return

    if os.path.exists(ACCU_FILE):
        with open(ACCU_FILE, 'r') as f:
            accu_data = json.load(f)
    else:
        accu_data = {"languages": []}

    # Suma las estadísticas de los nuevos datos al archivo acumulado
    for new_lang in new_data["languages"]:
        found = False
        for accu_lang in accu_data["languages"]:
            if accu_lang["name"] == new_lang["name"]:
                accu_lang["total_seconds"] += new_lang["total_seconds"]
                # Actualizar otros campos relevantes si es necesario
                found = True
                break
        if not found:
            accu_data["languages"].append(new_lang)

    # Guarda los datos acumulados actualizados
    with open(ACCU_FILE, 'w') as f:
        json.dump(accu_data, f, indent=4)

    return accu_data

def generate_chart():
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
    plt.savefig('chart.png')

generate_chart()
