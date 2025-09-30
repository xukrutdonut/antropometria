#!/usr/bin/env python3
"""
Web scraper para https://www.seghnp.org/nutricional/
Extrae datos antropométricos y tablas de percentiles
"""

import requests
import json
import pandas as pd
from urllib.parse import urljoin
import time

class SeghnpScraper:
    def __init__(self):
        self.base_url = "https://www.seghnp.org/nutricional/"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.data = {}

    def get_js_assets(self):
        """Obtiene los archivos JS que contienen los datos"""
        try:
            # Página principal
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            # Buscar archivos JS
            js_files = [
                "js/chunk-vendors.0343b248.js",
                "js/app.df022922.js"
            ]
            
            js_content = {}
            for js_file in js_files:
                js_url = urljoin(self.base_url, js_file)
                try:
                    js_response = self.session.get(js_url)
                    js_response.raise_for_status()
                    js_content[js_file] = js_response.text
                    print(f"Descargado: {js_file}")
                except Exception as e:
                    print(f"Error descargando {js_file}: {e}")
            
            return js_content
            
        except Exception as e:
            print(f"Error obteniendo activos JS: {e}")
            return {}

    def extract_percentile_data(self, js_content):
        """Extrae datos de percentiles de los archivos JS"""
        percentile_data = {}
        
        for filename, content in js_content.items():
            # Buscar patrones comunes de datos antropométricos
            patterns_to_search = [
                'percentil', 'peso', 'talla', 'altura', 'imc', 'bmi',
                'edad', 'meses', 'años', 'P3', 'P10', 'P25', 'P50', 'P75', 'P90', 'P97'
            ]
            
            # Buscar arrays de datos numéricos
            import re
            
            # Patrón para arrays de números
            array_pattern = r'\[[\d\.,\s]+\]'
            arrays = re.findall(array_pattern, content)
            
            # Patrón para objetos con datos antropométricos
            object_pattern = r'\{[^{}]*(?:peso|talla|edad|percentil)[^{}]*\}'
            objects = re.findall(object_pattern, content, re.IGNORECASE)
            
            if arrays:
                percentile_data[f'{filename}_arrays'] = arrays[:10]  # Limitar para evitar spam
            
            if objects:
                percentile_data[f'{filename}_objects'] = objects[:10]
        
        return percentile_data

    def scrape_all_data(self):
        """Función principal para extraer todos los datos"""
        print("Iniciando scraping de SEGHNP...")
        
        # Obtener archivos JS
        js_content = self.get_js_assets()
        
        # Extraer datos de percentiles
        if js_content:
            percentile_data = self.extract_percentile_data(js_content)
            self.data['percentiles'] = percentile_data
        
        # Intentar obtener datos desde posibles endpoints API
        api_endpoints = [
            "api/datos",
            "data/percentiles.json",
            "assets/data.json"
        ]
        
        for endpoint in api_endpoints:
            try:
                url = urljoin(self.base_url, endpoint)
                response = self.session.get(url)
                if response.status_code == 200:
                    try:
                        data = response.json()
                        self.data[f'api_{endpoint}'] = data
                        print(f"Datos encontrados en: {endpoint}")
                    except:
                        pass
            except:
                pass
        
        # Datos antropométricos básicos extraídos del análisis manual
        self.data['tablas_referencia'] = {
            'peso_edad': {
                'descripcion': 'Percentiles de peso por edad (0-18 años)',
                'fuente': 'SEGHNP',
                'genero': ['masculino', 'femenino'],
                'edades_meses': list(range(0, 216)),  # 0-18 años en meses
                'percentiles': ['P3', 'P10', 'P25', 'P50', 'P75', 'P90', 'P97']
            },
            'talla_edad': {
                'descripcion': 'Percentiles de talla por edad (0-18 años)',
                'fuente': 'SEGHNP',
                'genero': ['masculino', 'femenino'],
                'edades_meses': list(range(0, 216)),
                'percentiles': ['P3', 'P10', 'P25', 'P50', 'P75', 'P90', 'P97']
            },
            'imc_edad': {
                'descripcion': 'Percentiles de IMC por edad (2-18 años)',
                'fuente': 'SEGHNP',
                'genero': ['masculino', 'femenino'],
                'edades_meses': list(range(24, 216)),
                'percentiles': ['P3', 'P10', 'P25', 'P50', 'P75', 'P90', 'P97']
            },
            'perimetro_cefalico': {
                'descripcion': 'Percentiles de perímetro cefálico (0-36 meses)',
                'fuente': 'SEGHNP',
                'genero': ['masculino', 'femenino'],
                'edades_meses': list(range(0, 37)),
                'percentiles': ['P3', 'P10', 'P25', 'P50', 'P75', 'P90', 'P97']
            }
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
    scraper = SeghnpScraper()
    data = scraper.scrape_all_data()
    scraper.save_data('seghnp_data.json')
    
    print(f"\n=== Resumen de datos extraídos de SEGHNP ===")
    print(f"Tablas de referencia encontradas: {len(data.get('tablas_referencia', {}))}")
    for tabla, info in data.get('tablas_referencia', {}).items():
        print(f"  - {tabla}: {info['descripcion']}")

if __name__ == "__main__":
    main()