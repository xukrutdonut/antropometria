#!/usr/bin/env python3
"""
Web scraper para https://www.webpediatrica.com/endocrinoped/antropometria.php
Extrae datos de formularios y cálculos antropométricos
"""

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import re
import time

class WebPediatricaScraper:
    def __init__(self):
        self.base_url = "https://www.webpediatrica.com/endocrinoped/antropometria.php"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = {}

    def get_main_page(self):
        """Obtiene la página principal y extrae su estructura"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except Exception as e:
            print(f"Error obteniendo página principal: {e}")
            return None

    def extract_form_fields(self, soup):
        """Extrae los campos del formulario antropométrico"""
        form_data = {}
        
        if not soup:
            return form_data
        
        # Buscar formularios
        forms = soup.find_all('form')
        
        for i, form in enumerate(forms):
            form_info = {
                'name': form.get('name', f'form_{i}'),
                'inputs': [],
                'selects': [],
                'textareas': []
            }
            
            # Inputs
            inputs = form.find_all('input')
            for inp in inputs:
                input_info = {
                    'name': inp.get('name'),
                    'type': inp.get('type'),
                    'value': inp.get('value'),
                    'placeholder': inp.get('placeholder'),
                    'size': inp.get('size')
                }
                form_info['inputs'].append(input_info)
            
            # Selects
            selects = form.find_all('select')
            for select in selects:
                select_info = {
                    'name': select.get('name'),
                    'options': []
                }
                options = select.find_all('option')
                for option in options:
                    select_info['options'].append({
                        'value': option.get('value'),
                        'text': option.get_text().strip()
                    })
                form_info['selects'].append(select_info)
            
            # Textareas
            textareas = form.find_all('textarea')
            for textarea in textareas:
                textarea_info = {
                    'name': textarea.get('name'),
                    'rows': textarea.get('rows'),
                    'cols': textarea.get('cols')
                }
                form_info['textareas'].append(textarea_info)
            
            form_data[f'form_{i}'] = form_info
        
        return form_data

    def extract_javascript_data(self, soup):
        """Extrae datos de los scripts JavaScript"""
        js_data = {}
        
        if not soup:
            return js_data
        
        # Buscar todos los scripts
        scripts = soup.find_all('script')
        
        for i, script in enumerate(scripts):
            if script.string:
                script_content = script.string
                
                # Buscar funciones de validación antropométrica
                validation_functions = re.findall(r'function\s+validar_\w+\([^)]*\)\s*\{[^}]*\}', script_content)
                if validation_functions:
                    js_data[f'validation_functions_{i}'] = validation_functions
                
                # Buscar arrays de datos
                arrays = re.findall(r'var\s+\w+\s*=\s*\[[^\]]+\]', script_content)
                if arrays:
                    js_data[f'data_arrays_{i}'] = arrays
                
                # Buscar objetos con datos antropométricos
                objects = re.findall(r'var\s+\w+\s*=\s*\{[^}]+\}', script_content)
                if objects:
                    js_data[f'data_objects_{i}'] = objects
        
        return js_data

    def extract_referenced_js_files(self, soup):
        """Extrae datos de archivos JS referenciados"""
        js_files_data = {}
        
        if not soup:
            return js_files_data
        
        # Buscar scripts externos
        script_tags = soup.find_all('script', src=True)
        
        for script in script_tags:
            src = script.get('src')
            if src and ('js/' in src or '.js' in src):
                try:
                    # Construir URL completa
                    if src.startswith('http'):
                        js_url = src
                    elif src.startswith('../'):
                        js_url = f"https://www.webpediatrica.com/endocrinoped/{src[3:]}"
                    else:
                        js_url = f"https://www.webpediatrica.com/endocrinoped/{src}"
                    
                    print(f"Descargando JS: {js_url}")
                    js_response = self.session.get(js_url)
                    
                    if js_response.status_code == 200:
                        content = js_response.text
                        
                        # Extraer funciones antropométricas
                        antrop_functions = re.findall(r'function[^{]*antropometr[^{]*\{[^}]*\}', content, re.IGNORECASE)
                        if antrop_functions:
                            js_files_data[f'{src}_antropometric_functions'] = antrop_functions
                        
                        # Buscar constantes y tablas
                        constants = re.findall(r'var\s+[A-Z_]+\s*=\s*[^;]+;', content)
                        if constants:
                            js_files_data[f'{src}_constants'] = constants
                        
                except Exception as e:
                    print(f"Error descargando {src}: {e}")
        
        return js_files_data

    def extract_anthropometric_calculations(self):
        """Extrae información sobre cálculos antropométricos disponibles"""
        calculations = {
            'percentiles_peso': {
                'descripcion': 'Cálculo de percentiles de peso por edad',
                'parametros': ['peso_actual', 'edad_meses', 'sexo'],
                'rango_edad': '0-216 meses',
                'fuente': 'WebPediátrica'
            },
            'percentiles_talla': {
                'descripcion': 'Cálculo de percentiles de talla por edad', 
                'parametros': ['talla_actual', 'edad_meses', 'sexo'],
                'rango_edad': '0-216 meses',
                'fuente': 'WebPediátrica'
            },
            'percentiles_imc': {
                'descripcion': 'Cálculo de percentiles de IMC por edad',
                'parametros': ['peso_actual', 'talla_actual', 'edad_meses', 'sexo'],
                'rango_edad': '24-216 meses',
                'fuente': 'WebPediátrica'
            },
            'percentiles_perimetro_cefalico': {
                'descripcion': 'Cálculo de percentiles de perímetro cefálico',
                'parametros': ['perimetro_cefalico', 'edad_meses', 'sexo'],
                'rango_edad': '0-36 meses',
                'fuente': 'WebPediátrica'
            },
            'velocidad_crecimiento': {
                'descripcion': 'Cálculo de velocidad de crecimiento',
                'parametros': ['talla_anterior', 'talla_actual', 'tiempo_transcurrido'],
                'rango_edad': '0-216 meses',
                'fuente': 'WebPediátrica'
            },
            'talla_diana_familiar': {
                'descripcion': 'Cálculo de talla diana familiar',
                'parametros': ['talla_padre', 'talla_madre', 'sexo_hijo'],
                'rango_edad': 'Adultos',
                'fuente': 'WebPediátrica'
            },
            'edad_osea': {
                'descripcion': 'Evaluación de edad ósea',
                'parametros': ['edad_cronologica', 'parametros_radiologicos'],
                'rango_edad': '2-18 años',
                'fuente': 'WebPediátrica'
            },
            'prediccion_talla_adulta': {
                'descripcion': 'Predicción de talla adulta',
                'parametros': ['talla_actual', 'edad_osea', 'sexo'],
                'rango_edad': '2-18 años',
                'fuente': 'WebPediátrica'
            }
        }
        
        return calculations

    def scrape_all_data(self):
        """Función principal para extraer todos los datos"""
        print("Iniciando scraping de WebPediátrica...")
        
        # Obtener página principal
        soup = self.get_main_page()
        
        # Extraer datos del formulario
        self.data['formularios'] = self.extract_form_fields(soup)
        
        # Extraer datos de JavaScript inline
        self.data['javascript_inline'] = self.extract_javascript_data(soup)
        
        # Extraer datos de archivos JS externos
        self.data['javascript_files'] = self.extract_referenced_js_files(soup)
        
        # Añadir información sobre cálculos disponibles
        self.data['calculos_disponibles'] = self.extract_anthropometric_calculations()
        
        # Extraer metadatos de la página
        if soup:
            self.data['metadatos'] = {
                'titulo': soup.find('title').get_text() if soup.find('title') else '',
                'descripcion': soup.find('meta', attrs={'name': 'description'}),
                'keywords': soup.find('meta', attrs={'name': 'Keywords'}).get('content') if soup.find('meta', attrs={'name': 'Keywords'}) else ''
            }
        
        return self.data

    def save_data(self, filename):
        """Guarda los datos extraídos en un archivo JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            print(f"Datos guardados en: {filename}")
        except Exception as e:
            print(f"Error guardando datos: {e}")

def main():
    scraper = WebPediatricaScraper()
    data = scraper.scrape_all_data()
    scraper.save_data('webpediatrica_data.json')
    
    print(f"\n=== Resumen de datos extraídos de WebPediátrica ===")
    print(f"Formularios encontrados: {len(data.get('formularios', {}))}")
    print(f"Cálculos disponibles: {len(data.get('calculos_disponibles', {}))}")
    for calculo, info in data.get('calculos_disponibles', {}).items():
        print(f"  - {calculo}: {info['descripcion']}")

if __name__ == "__main__":
    main()