from django.shortcuts import render

from . import views 

def inicio(request):
    return render(request, 'inicio.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def servicios(request):
    return render(request, 'servicios.html')
    
def pagina_original(request):
    return render(request, 'pagina_original.html')