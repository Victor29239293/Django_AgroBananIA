from django.shortcuts import render
from django.views import View
import json
# Create your views here.

class HomeView(View):
    def get(self, request):
        return render(request, 'core/home.html')


class DashboardView(View):
    def get(self, request):
        # DATOS QUEMADOS - Coordenadas de zonas bananeras reales de Ecuador
        coordenadas = [
            {
                'id': 1,
                'nombre': 'Finca El Paraíso',
                'latitud': '-2.170',  # Guayas, Ecuador
                'longitud': '-79.920',
                'ubicacion': 'Guayas, Ecuador',
                'extension_hectareas': '45.5',
                'fecha_registro': '15/01/2020',
                'propietario': 'Juan Pérez González'
            },
            {
                'id': 2,
                'nombre': 'Plantación San José',
                'latitud': '-1.850',  # Los Ríos, Ecuador
                'longitud': '-79.450',
                'ubicacion': 'Los Ríos, Ecuador',
                'extension_hectareas': '32.8',
                'fecha_registro': '22/03/2019',
                'propietario': 'María Carmen Rodríguez'
            },
            {
                'id': 3,
                'nombre': 'Hacienda Verde',
                'latitud': '-3.260',  # El Oro, Ecuador
                'longitud': '-79.850',
                'ubicacion': 'El Oro, Ecuador',
                'extension_hectareas': '58.2',
                'fecha_registro': '10/07/2018',
                'propietario': 'Carlos Mendoza Silva'
            },
            {
                'id': 4,
                'nombre': 'Finca La Esperanza',
                'latitud': '-0.980',  # Esmeraldas, Ecuador
                'longitud': '-79.650',
                'ubicacion': 'Esmeraldas, Ecuador',
                'extension_hectareas': '28.5',
                'fecha_registro': '05/11/2021',
                'propietario': 'Ana Sofía Torres'
            },
            {
                'id': 5,
                'nombre': 'Agrícola Santa Rosa',
                'latitud': '-2.420',  # Guayas (sur), Ecuador
                'longitud': '-79.680',
                'ubicacion': 'Guayas Sur, Ecuador',
                'extension_hectareas': '72.3',
                'fecha_registro': '18/06/2017',
                'propietario': 'Roberto Castro Vargas'
            },
            {
                'id': 6,
                'nombre': 'Plantación Los Andes',
                'latitud': '-1.650',  # Los Ríos (norte), Ecuador
                'longitud': '-79.280',
                'ubicacion': 'Los Ríos Norte, Ecuador',
                'extension_hectareas': '41.7',
                'fecha_registro': '30/09/2020',
                'propietario': 'Luisa Fernanda Gómez'
            },
            {
                'id': 7,
                'nombre': 'Finca Bananera El Sol',
                'latitud': '-2.050',  # Guayas (centro), Ecuador
                'longitud': '-79.750',
                'ubicacion': 'Guayas Centro, Ecuador',
                'extension_hectareas': '35.9',
                'fecha_registro': '12/02/2019',
                'propietario': 'Diego Alejandro Morales'
            },
            {
                'id': 8,
                'nombre': 'Agroindustrial Costa Verde',
                'latitud': '-3.150',  # El Oro (norte), Ecuador
                'longitud': '-79.720',
                'ubicacion': 'El Oro Norte, Ecuador',
                'extension_hectareas': '64.1',
                'fecha_registro': '25/04/2018',
                'propietario': 'Patricia Isabel Vásquez'
            }
        ]
        
        # Plantación principal (la primera de la lista)
        plantacion_principal = {
            'id': 1,
            'nombre': 'Finca El Paraíso',
            'ubicacion': 'Zona 1, Guayas',
            'extension_hectareas': 45.5,
            'fecha_registro': '01/01/2020',
            'propietario': 'Juan Pérez González',
            'latitud': -2.170,
            'longitud': -79.920
        }
        
        context = {
            'coordenadas_plantaciones': json.dumps(coordenadas),
            'plantacion': plantacion_principal
        }

        return render(request, 'core/Dashboard/inicio.html', context)
