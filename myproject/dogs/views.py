from django.shortcuts import render
import google.generativeai as genai
import requests
from django.conf import settings

# Configura la API de Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

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
        response = model.generate_content(descripcion)
        print(response)  # Imprime la estructura completa de la respuesta para depuración

        if not response.candidates:
            raise ValueError("No candidates returned from the model.")

        # Accede correctamente al contenido dentro de 'parts'
        texto_respuesta = response.candidates[0].content.parts[0].text.strip()

        # Procesar la respuesta
        lineas = texto_respuesta.split('\n')
        razas = []
        raza_actual = None

        for linea in lineas:
            if linea.startswith('**'):
                if raza_actual:
                    razas.append(raza_actual)
                nombre_raza = linea.strip('** ')
                raza_actual = {'nombre': nombre_raza, 'cuidados': '', 'actividad': '', 'imagen': ''}
            elif linea.startswith('* '):
                if 'Tamaño' in linea:
                    raza_actual['tamaño'] = linea.replace('* Tamaño: ', '').strip()
                elif 'Tipo de pelo' in linea:
                    raza_actual['cuidados'] = linea.replace('* Tipo de pelo: ', '').strip()
                elif 'Temperamento' in linea:
                    raza_actual['actividad'] = linea.replace('* Temperamento: ', '').strip()
        if raza_actual:
            razas.append(raza_actual)

        for raza in razas:
            try:
                raza_url = raza['nombre'].lower().replace(" ", "/")
                imagen_url = f"https://dog.ceo/api/breed/{raza_url}/images/random"
                imagen_response = requests.get(imagen_url)
                imagen_data = imagen_response.json()
                raza['imagen'] = imagen_data.get('message', '')
            except Exception as e:
                print(f"Error obteniendo la imagen de la raza: {raza['nombre']}. Error: {e}")

        return razas

    except Exception as e:
        print(f"Error al obtener datos de Gemini: {e}")
        return []

