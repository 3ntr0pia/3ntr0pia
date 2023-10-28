
import json
import os
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as PathEffects

def accumulate_data_with_editors_adjusted():
    try:
        accu_file_path = 'accumulated.json'
        if os.path.exists(accu_file_path):
            with open(accu_file_path, 'r') as f:
                accu_data = json.load(f)
        else:
            accu_data = {"languages": [], "editors": []}

        latest_json_file = get_latest_json_file('./json_data/')
        if not latest_json_file:
            print("No JSON files found.")
            return accu_data

        with open(latest_json_file, 'r') as f:
            new_data = json.load(f)

        # Extract and sum the languages and editors data from each date
        all_languages = defaultdict(float)
        all_editors = defaultdict(float)
        for date, data in new_data.items():
            for lang in data["languages"]:
                all_languages[lang["name"]] += lang["total_seconds"]
            
            for editor in data.get("editors", []):
                all_editors[editor["name"]] += editor["total_seconds"]

        # Convert the accumulated data into the expected format
        accumulated_languages = [{"name": name, "total_seconds": total_seconds} for name, total_seconds in all_languages.items()]
        accumulated_editors = [{"name": name, "total_seconds": total_seconds} for name, total_seconds in all_editors.items()]

        for new_lang in accumulated_languages:
            found = False
            for accu_lang in accu_data["languages"]:
                if accu_lang["name"] == new_lang["name"]:
                    accu_lang["total_seconds"] += new_lang["total_seconds"]
                    found = True
                    break
            if not found:
                accu_data["languages"].append(new_lang)

        for new_editor in accumulated_editors:
            found = False
            for accu_editor in accu_data.get("editors", []):
                if accu_editor["name"] == new_editor["name"]:
                    accu_editor["total_seconds"] += new_editor["total_seconds"]
                    found = True
                    break
            if not found:
                if "editors" not in accu_data:
                    accu_data["editors"] = []
                accu_data["editors"].append(new_editor)

        with open(accu_file_path, 'w') as f:
            json.dump(accu_data, f, indent=4)

        return accu_data
    except Exception as e:
        print(f"Error en accumulate_data_with_editors_adjusted: {e}")
        return None

def get_latest_json_file(path):
    files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.json') and 'accumulated' not in f]
    files.sort(key=os.path.getmtime, reverse=True)
    return files[0] if files else None



def combined_generate_chart():
    try:
        data = accumulate_data_with_editors_adjusted()
        if not data:
            print("No se pudo generar la gráfica combinada debido a la falta de datos.")
            return
        
        # Total time for languages and editors
        total_language_seconds = sum([lang["total_seconds"] for lang in data["languages"]])
        total_editor_seconds = sum([editor["total_seconds"] for editor in data["editors"]])
        
        # Convert to hours
        total_language_hours = total_language_seconds / 3600
        total_editor_hours = total_editor_seconds / 3600
        
        # Create a combined chart with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 14))
        
        # DOUGHNUT CHART
        languages = [lang for lang in data["languages"] if lang["name"] not in ["Brainfuck", "Other", "Text"]]
        languages.sort(key=lambda x: x["total_seconds"], reverse=True)
        top_5_languages = languages[:5]
        other_seconds = sum([lang["total_seconds"] for lang in languages[5:]])
        if other_seconds > 0:
            top_5_languages.append({"name": "Other Languages", "total_seconds": other_seconds})

        names = [lang["name"] for lang in top_5_languages]
        total_seconds = [lang["total_seconds"] for lang in top_5_languages]
        
        wedges, texts, autotexts = ax1.pie(total_seconds, labels=names, autopct='%1.1f%%', startangle=90, wedgeprops=dict(width=0.3), colors=plt.cm.Paired.colors, textprops={'fontsize': 12, 'color': 'lightcyan', 'fontweight': 'bold'})

        for autotext in autotexts:
            autotext.set_path_effects([PathEffects.withStroke(linewidth=3, foreground='black')])
        
        ax1.set_title(f"Languages (Total: {total_language_hours:.2f} hrs)", color="skyblue", fontweight="bold", path_effects=[PathEffects.withStroke(linewidth=2, foreground='black')])
        
        # RADAR CHART
        # Exclude Firefox from the data
        editors = [editor for editor in data["editors"] if editor["name"] != "Firefox"]
        editors.sort(key=lambda x: x["total_seconds"], reverse=True)
        top_editors = editors[:5]
    
        labels = [editor["name"] for editor in top_editors]
        values = [editor["total_seconds"] for editor in top_editors]
    
        # Number of variables (editors)
        num_vars = len(labels)
    
        # Compute angle for each axis in the plot
        angles = [n / float(num_vars) * 2 * np.pi for n in range(num_vars)]
        angles += angles[:1]
    
        # Draw one axis per variable + add labels with adjusted colors and effects
        ax2.set_xticks(angles[:-1])
        ax2.set_xticklabels(labels, color='skyblue', size=10, fontweight='bold', path_effects=[PathEffects.withStroke(linewidth=2, foreground='black')])
    
        # Draw ylabels
        ax2.set_rlabel_position(30)
        ax2.set_yticks([5000, 10000, 15000])
        ax2.set_yticklabels(["5k", "10k", "15k"], color="skyblue", size=7, path_effects=[PathEffects.withStroke(linewidth=1, foreground='black')])
        ax2.set_ylim(0, max(values) + 1000)
    
        values += values[:1]
        ax2.plot(angles, values, linewidth=2, linestyle='solid')
        ax2.fill(angles, values, 'b', alpha=0.1)
        
        ax2.set_title(f"IDEs (Total: {total_editor_hours:.2f} hrs)", color="skyblue", fontweight="bold", path_effects=[PathEffects.withStroke(linewidth=2, foreground='black')])
        
        plt.tight_layout()
        plt.savefig('./combined_chart.png', transparent=True)
        plt.show()
        
    except Exception as e:
        print(f"Error en combined_generate_chart: {e}")

# Generate the combined chart
combined_generate_chart()


# Call the function to generate the combined chart
combined_generate_chart_final_adjustments()
