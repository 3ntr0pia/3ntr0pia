import os
import json
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

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

def generate_doughnut_chart():
    try:
        data = accumulate_data()
        if not data:
            print("No se pudo generar la gráfica debido a la falta de datos.")
            return
        
        # Filtrar los lenguajes especificados y obtener los 5 más usados
        languages = [lang for lang in data["languages"] if lang["name"] not in ["Brainfuck", "Other", "Text"]]
        languages.sort(key=lambda x: x["total_seconds"], reverse=True)
        top_5_languages = languages[:5]
        other_seconds = sum([lang["total_seconds"] for lang in languages[5:]])
        if other_seconds > 0:
            top_5_languages.append({"name": "Other Languages", "total_seconds": other_seconds})
        
        names = [lang["name"] for lang in top_5_languages]
        total_seconds = [lang["total_seconds"] for lang in top_5_languages]

        fig, ax = plt.subplots(figsize=(10, 7))
        wedges, texts, autotexts = ax.pie(total_seconds, labels=names, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3), colors=plt.cm.Paired.colors, textprops={'fontsize': 12, 'color': 'lightcyan', 'fontweight': 'bold'})
        
        # Aplicar sombra al texto
        for autotext in autotexts:
            autotext.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])

        plt.tight_layout()
        plt.savefig('./chart.png', transparent=True)
    except Exception as e:
        print(f"Error en generate_doughnut_chart: {e}")

generate_doughnut_chart()


def accumulate_ide_data():
    ide_accu_file = './json_data/accumulateIDE.json'
    try:
        # Read the existing accumulateIDE.json file if it exists
        with open(ide_accu_file, 'r') as f:
            ide_data = json.load(f)
    except FileNotFoundError:
        ide_data = {"ides": []}
    
    # Read the latest JSON file for the day's data
    latest_json_file = get_latest_json_file('./json_data')
    with open(latest_json_file, 'r') as f:
        latest_data = json.load(f)
    
    # Assuming that 'ides' key exists in the latest data (to be confirmed)
    # Omit 'Firefox' from the IDE data
    for ide in [i for i in latest_data.get('ides', []) if i['name'] != 'Firefox']:
        # Convert total_seconds to total_hours
        ide['total_hours'] = ide['total_seconds'] / 3600
        
        # Check if this IDE is already in the accumulated data
        for accu_ide in ide_data['ides']:
            if accu_ide['name'] == ide['name']:
                accu_ide['total_hours'] += ide['total_hours']
                break
        else:
            ide_data['ides'].append(ide)
    
    # Save the updated accumulateIDE.json file
    with open(ide_accu_file, 'w') as f:
        json.dump(ide_data, f, indent=4)


def generate_ide_radar_chart():
    # Read the accumulateIDE.json file
    with open('./json_data/accumulateIDE.json', 'r') as f:
        ide_data = json.load(f)
    
    # Extract IDE names and total_hours for the radar chart
    ide_names = [ide['name'] for ide in ide_data['ides']]
    total_hours = [ide['total_hours'] for ide in ide_data['ides']]
    
    # Create the radar chart
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    ax.fill(ide_names, total_hours, color='b', alpha=0.6)
    ax.set_title('IDE Usage', color='skyblue', path_effects=[PathEffects.withStroke(linewidth=3, foreground='black')])

    # Save the radar chart as a PNG with a transparent background
    plt.savefig('./json_data/ide_radar_chart.png', transparent=True)


# Existing doughnut chart generation logic (truncated for simplicity)
# ...

# Add a title to the doughnut chart
total_seconds = sum([lang['total_seconds'] for lang in accumulated_data['languages']])
total_hours = total_seconds / 3600
plt.title(f'Total Hours: {total_hours:.2f}', color='skyblue', path_effects=[PathEffects.withStroke(linewidth=3, foreground='black')])

# Save the doughnut chart as a temporary PNG
plt.savefig('./json_data/temp_doughnut_chart.png', transparent=True)

# Combine the doughnut and radar charts into a single PNG image
from PIL import Image

doughnut_img = Image.open('./json_data/temp_doughnut_chart.png')
radar_img = Image.open('./json_data/ide_radar_chart.png')

combined_img = Image.new('RGBA', (doughnut_img.width, doughnut_img.height + radar_img.height))
combined_img.paste(doughnut_img, (0, 0))
combined_img.paste(radar_img, (0, doughnut_img.height))

# Save the combined image
combined_img.save('./json_data/combined_chart.png', 'PNG')
