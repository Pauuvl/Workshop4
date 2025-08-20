import pandas as pd

# Nombre del archivo CSV de entrada
csv_file = "movies_initial.csv"

# Nombre del archivo JSON de salida
json_file = "movies.json"

try:
    # Leer el archivo CSV
    df = pd.read_csv(csv_file)

    # Convertir a JSON
    df.to_json(json_file, orient="records", indent=4, force_ascii=False)

    print(f"✅ Conversión completa. Archivo generado: {json_file}")

except FileNotFoundError:
    print(f"❌ No se encontró el archivo {csv_file}. Verifica que exista en la raíz del proyecto.")
except Exception as e:
    print(f"⚠️ Error durante la conversión: {e}")
