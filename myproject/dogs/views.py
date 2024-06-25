from django.shortcuts import render
import google.generativeai as genai
import requests
from django.conf import settings
import json
import os

# Configura la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Cargar el mapeo de razas desde el archivo JSON
with open(os.path.join(settings.BASE_DIR, 'dogs/static/raza_map.json')) as f:
    raza_map = json.load(f)

def index(request):
    return render(request, 'index.html')

def resultados(request):
    if request.method == 'POST':
        descripcion = request.POST.get('user_prompt')
        razas = obtener_razas(descripcion)
        return render(request, 'resultados.html', {'results': razas})
    return render(request, 'resultados.html', {'results': []})

def obtener_razas(descripcion):
    try:
        # Llama a Gemini para obtener las razas de perros recomendadas
        prompt = (
            f"Con base en la siguiente descripción del perro ideal: {descripcion}, "
            "proporciona una lista de al menos 4 razas de perros en el siguiente formato JSON:\n"
            "[\n"
            "  {\n"
            "    \"nombre\": \"Nombre de la raza\",\n"
            "    \"tamaño\": \"Descripción del tamaño\",\n"
            "    \"tipo_de_pelo\": \"Descripción del tipo de pelo\",\n"
            "    \"temperamento\": \"Descripción del temperamento\",\n"
            "    \"mantenimiento\": \"Tipo de mantenimiento\",\n"
            "    \"nivel_de_actividad\": \"Nivel de actividad\",\n"
            "    \"cuidados\": \"Cuidados necesarios\"\n"
            "  }\n"
            "]\n"
        )
        response = model.generate_content(prompt)
        print(response)  # Imprime la estructura completa de la respuesta para depuración

        if not response.candidates:
            raise ValueError("No candidates returned from the model.")

        # Accede correctamente al contenido dentro de 'parts'
        texto_respuesta = response.candidates[0].content.parts[0].text.strip()

        # Extraer el JSON del bloque de código Markdown
        if texto_respuesta.startswith('```json') and texto_respuesta.endswith('```'):
            texto_respuesta = texto_respuesta[7:-3].strip()

        # Parsear el JSON de la respuesta
        razas_recomendadas = json.loads(texto_respuesta)

        razas = []
        for raza in razas_recomendadas:
            nombre_raza = raza.get('nombre', '').lower()
            tamaño = raza.get('tamaño', '')
            tipo_de_pelo = raza.get('tipo_de_pelo', '')
            temperamento = raza.get('temperamento', '')
            mantenimiento = raza.get('mantenimiento', '')
            nivel_de_actividad = raza.get('nivel_de_actividad', '')
            cuidados = raza.get('cuidados', '')

            raza_actual = {
                'nombre': nombre_raza,
                'tamaño': tamaño,
                'tipo_de_pelo': tipo_de_pelo,
                'temperamento': temperamento,
                'mantenimiento': mantenimiento,
                'nivel_de_actividad': nivel_de_actividad,
                'cuidados': cuidados,
                'imagen': ''
            }

            try:
                raza_url = raza_map.get(nombre_raza, nombre_raza.replace(" ", "/"))
                imagen_url = f"https://dog.ceo/api/breed/{raza_url}/images/random"
                imagen_response = requests.get(imagen_url)
                imagen_data = imagen_response.json()
                raza_actual['imagen'] = imagen_data.get('message', '')
            except Exception as e:
                print(f"Error obteniendo la imagen de la raza: {raza_actual['nombre']}. Error: {e}")

            razas.append(raza_actual)

        return razas

    except Exception as e:
        print(f"Error al obtener datos de Gemini: {e}")
        return []

