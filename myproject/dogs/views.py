from django.shortcuts import render
import google.generativeai as genai
import requests
from django.conf import settings
import json

# Configura la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Configura la API de Unsplash
UNSPLASH_ACCESS_KEY = settings.UNSPLASH_ACCESS_KEY  # Reemplaza con tu Access Key de Unsplash

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
        # Mejora del prompt con instrucciones más específicas
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
            "Por favor, asegúrate de incluir detalles sobre el tamaño, el tipo de pelo, el temperamento, el mantenimiento, el nivel de actividad y los cuidados necesarios para cada raza."
        )
        print(f"Prompt enviado a Gemini: {prompt}")  # Imprime el prompt para depuración
        response = model.generate_content(prompt)
        print(response)  # Imprime la estructura completa de la respuesta para depuración

        if not response.candidates:
            raise ValueError("No candidates returned from the model.")

        # Accede correctamente al contenido dentro de 'parts'
        texto_respuesta = response.candidates[0].content.parts[0].text.strip()

        # Extraer el JSON del bloque de código Markdown, si es necesario
        if texto_respuesta.startswith('```') and texto_respuesta.endswith('```'):
            texto_respuesta = texto_respuesta.strip('``` JSON\n').strip('```')

        # Verifica si la respuesta contiene información válida en formato JSON
        try:
            razas_recomendadas = json.loads(texto_respuesta)
        except json.JSONDecodeError:
            raise ValueError("La respuesta de Gemini no contiene un JSON válido.")

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
                'imagen': obtener_imagen_perro(nombre_raza)
            }

            razas.append(raza_actual)

        return razas

    except Exception as e:
        print(f"Error al obtener datos de Gemini: {e}")
        return []

def obtener_imagen_perro(raza):
    try:
        query = f"{raza} dog"
        url = f"https://www.googleapis.com/customsearch/v1?q={query}&searchType=image&key={settings.GOOGLE_API_KEY}&cx={settings.GOOGLE_CX}"
        response = requests.get(url)
        data = response.json()
        print(data)  # Depuración: Imprime los datos obtenidos de Google Custom Search
        if 'items' in data:
            return data['items'][0]['link']  # Devuelve el enlace de la primera imagen
        return ''
    except Exception as e:
        print(f"Error obteniendo la imagen de la raza: {raza}. Error: {e}")
        return ''