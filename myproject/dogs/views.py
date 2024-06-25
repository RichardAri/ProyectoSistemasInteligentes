from django.shortcuts import render
import requests

def index(request):
    return render(request, 'index.html')

def resultados(request):
    descripcion = request.POST.get('descripcion')
    razas = obtener_razas(descripcion)
    return render(request, 'resultados.html', {'razas': razas})

def obtener_razas(descripcion):
    # Aquí puedes implementar la llamada a Gemini y lógica para obtener las razas
    # Por ahora, usaremos datos de prueba
    url = "https://dog.ceo/api/breeds/image/random"
    response = requests.get(url)
    data = response.json()
    return [{'nombre': 'Golden Retriever', 'imagen': data['message']}]
