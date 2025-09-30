#!/usr/bin/env python3
"""
Aplicación Flask optimizada para Raspberry Pi 5
Calculadora antropométrica con optimizaciones de memoria y CPU
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import math
import gc  # Para gestión de memoria en RPi
import logging

# Configuración optimizada para RPi
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Configurar logging optimizado para RPi
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(name)s %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AnthropometricCalculator:
    def __init__(self):
        self.data = {}
        self._percentile_cache = {}  # Cache para optimizar RPi
        self.load_anthropometric_data()
    
    def load_anthropometric_data(self):
        """Carga los datos antropométricos fusionados con manejo de errores"""
        try:
            data_file = 'fused_anthropometric_data.json'
            if os.path.exists(data_file):
                with open(data_file, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
                logger.info(f"Datos cargados correctamente desde {data_file}")
            else:
                logger.warning(f"Archivo {data_file} no encontrado, usando datos por defecto")
                self.create_default_data()
        except Exception as e:
            logger.error(f"Error cargando datos: {e}")
            self.create_default_data()
    
    def create_default_data(self):
        """Crea datos por defecto optimizados para memoria"""
        self.data = {
            'metadatos': {
                'titulo': 'Calculadora Antropométrica RPi5',
                'version': '1.0-rpi',
                'optimizado_para': 'Raspberry Pi 5'
            },
            'tablas_percentiles': {},
            'funciones_calculo': {}
        }
        logger.info("Datos por defecto creados")
    
    def calcular_imc(self, peso_kg, talla_cm):
        """Calcula el IMC con validación optimizada"""
        try:
            if talla_cm <= 0 or peso_kg <= 0:
                return None
            talla_m = talla_cm / 100
            imc = peso_kg / (talla_m ** 2)
            return round(imc, 2)
        except Exception as e:
            logger.error(f"Error calculando IMC: {e}")
            return None
    
    def calcular_talla_diana_familiar(self, talla_padre, talla_madre, sexo_hijo):
        """Calcula la talla diana familiar con cache"""
        cache_key = f"diana_{talla_padre}_{talla_madre}_{sexo_hijo}"
        
        if cache_key in self._percentile_cache:
            return self._percentile_cache[cache_key]
        
        try:
            if sexo_hijo.lower() == 'masculino':
                talla_diana = (talla_padre + talla_madre + 13) / 2
            else:
                talla_diana = (talla_padre + talla_madre - 13) / 2
            
            resultado = {
                'talla_diana': round(talla_diana, 1),
                'rango_inferior': round(talla_diana - 8.5, 1),
                'rango_superior': round(talla_diana + 8.5, 1)
            }
            
            # Cache del resultado
            self._percentile_cache[cache_key] = resultado
            return resultado
        except Exception as e:
            logger.error(f"Error calculando talla diana: {e}")
            return None
    
    def calcular_velocidad_crecimiento(self, talla_inicial, talla_actual, tiempo_meses):
        """Calcula la velocidad de crecimiento"""
        try:
            if tiempo_meses <= 0:
                return None
            
            diferencia_talla = talla_actual - talla_inicial
            velocidad_cm_mes = diferencia_talla / tiempo_meses
            velocidad_cm_año = velocidad_cm_mes * 12
            
            return round(velocidad_cm_año, 2)
        except Exception as e:
            logger.error(f"Error calculando velocidad: {e}")
            return None
    
    def estimar_percentil(self, medida, edad_meses, sexo, tipo_medida):
        """Estima el percentil con optimizaciones para RPi"""
        cache_key = f"perc_{medida}_{edad_meses}_{sexo}_{tipo_medida}"
        
        if cache_key in self._percentile_cache:
            return self._percentile_cache[cache_key]
        
        try:
            percentiles_ref = [3, 10, 25, 50, 75, 90, 97]
            
            # Simplificación de cálculos para optimizar RPi
            if tipo_medida == 'peso':
                valores_ref = self._get_peso_referencias(edad_meses, sexo)
            elif tipo_medida == 'talla':
                valores_ref = self._get_talla_referencias(edad_meses, sexo)
            elif tipo_medida == 'imc':
                if edad_meses < 24:
                    return None
                valores_ref = [14, 15, 15.5, 16.5, 18, 19.5, 21.5]
            else:
                return None
            
            # Encontrar percentil
            for i, valor_ref in enumerate(valores_ref):
                if medida <= valor_ref:
                    resultado = percentiles_ref[i]
                    self._percentile_cache[cache_key] = resultado
                    return resultado
            
            resultado = percentiles_ref[-1]
            self._percentile_cache[cache_key] = resultado
            return resultado
            
        except Exception as e:
            logger.error(f"Error estimando percentil: {e}")
            return None
    
    def _get_peso_referencias(self, edad_meses, sexo):
        """Referencias de peso optimizadas"""
        if edad_meses <= 12:
            base = 10.5 if sexo == 'masculino' else 10.0
        elif edad_meses <= 36:
            base = 15 if sexo == 'masculino' else 14.5
        else:
            edad_años = edad_meses / 12
            base = 2 * edad_años + 8 if sexo == 'masculino' else 2 * edad_años + 7.5
        
        return [base*0.8, base*0.87, base*0.93, base, base*1.15, base*1.30, base*1.45]
    
    def _get_talla_referencias(self, edad_meses, sexo):
        """Referencias de talla optimizadas"""
        if edad_meses <= 12:
            base = 78 if sexo == 'masculino' else 76
        else:
            edad_años = edad_meses / 12
            base = 85 + (edad_años - 1) * 6 if sexo == 'masculino' else 83 + (edad_años - 1) * 5.5
        
        return [base*0.92, base*0.95, base*0.97, base, base*1.03, base*1.06, base*1.09]
    
    def cleanup_cache(self):
        """Limpia cache periódicamente para liberar memoria"""
        if len(self._percentile_cache) > 100:
            self._percentile_cache.clear()
            gc.collect()  # Fuerza garbage collection
            logger.info("Cache limpiado para liberar memoria")

# Instancia global del calculador
calculator = AnthropometricCalculator()

# Routes optimizados
@app.route('/')
def index():
    """Página principal optimizada"""
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error en página principal: {e}")
        return "Error interno del servidor", 500

@app.route('/health')
def health_check():
    """Health check para monitoreo"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'platform': 'Raspberry Pi 5'
    })

@app.route('/api/calcular_imc', methods=['POST'])
def api_calcular_imc():
    """API para calcular IMC optimizada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos requeridos'}), 400
        
        peso = float(data.get('peso', 0))
        talla = float(data.get('talla', 0))
        
        if peso <= 0 or talla <= 0:
            return jsonify({'success': False, 'error': 'Valores inválidos'}), 400
        
        imc = calculator.calcular_imc(peso, talla)
        
        if imc is None:
            return jsonify({'success': False, 'error': 'Error en cálculo'}), 500
        
        return jsonify({
            'success': True,
            'imc': imc,
            'clasificacion': clasificar_imc(imc)
        })
    except Exception as e:
        logger.error(f"Error en API IMC: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@app.route('/api/calcular_talla_diana', methods=['POST'])
def api_calcular_talla_diana():
    """API para calcular talla diana optimizada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos requeridos'}), 400
        
        talla_padre = float(data.get('talla_padre', 0))
        talla_madre = float(data.get('talla_madre', 0))
        sexo_hijo = data.get('sexo_hijo', '')
        
        if not all([talla_padre > 0, talla_madre > 0, sexo_hijo]):
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        resultado = calculator.calcular_talla_diana_familiar(talla_padre, talla_madre, sexo_hijo)
        
        if resultado is None:
            return jsonify({'success': False, 'error': 'Error en cálculo'}), 500
        
        return jsonify({
            'success': True,
            'resultado': resultado
        })
    except Exception as e:
        logger.error(f"Error en API Talla Diana: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@app.route('/api/calcular_percentil', methods=['POST'])
def api_calcular_percentil():
    """API para calcular percentiles optimizada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos requeridos'}), 400
        
        medida = float(data.get('medida', 0))
        edad_meses = int(data.get('edad_meses', 0))
        sexo = data.get('sexo', '')
        tipo_medida = data.get('tipo_medida', '')
        
        if not all([medida > 0, edad_meses >= 0, sexo, tipo_medida]):
            return jsonify({'success': False, 'error': 'Datos incompletos'}), 400
        
        percentil = calculator.estimar_percentil(medida, edad_meses, sexo, tipo_medida)
        
        if percentil is None:
            return jsonify({'success': False, 'error': 'Error en cálculo'}), 500
        
        # Limpiar cache periódicamente
        calculator.cleanup_cache()
        
        return jsonify({
            'success': True,
            'percentil': percentil,
            'interpretacion': interpretar_percentil(percentil)
        })
    except Exception as e:
        logger.error(f"Error en API Percentil: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

@app.route('/api/calcular_velocidad_crecimiento', methods=['POST'])
def api_calcular_velocidad_crecimiento():
    """API para calcular velocidad optimizada"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Datos requeridos'}), 400
        
        talla_inicial = float(data.get('talla_inicial', 0))
        talla_actual = float(data.get('talla_actual', 0))
        tiempo_meses = int(data.get('tiempo_meses', 0))
        
        if not all([talla_inicial > 0, talla_actual > 0, tiempo_meses > 0]):
            return jsonify({'success': False, 'error': 'Datos inválidos'}), 400
        
        velocidad = calculator.calcular_velocidad_crecimiento(talla_inicial, talla_actual, tiempo_meses)
        
        if velocidad is None:
            return jsonify({'success': False, 'error': 'Error en cálculo'}), 500
        
        return jsonify({
            'success': True,
            'velocidad_cm_año': velocidad,
            'evaluacion': evaluar_velocidad_crecimiento(velocidad)
        })
    except Exception as e:
        logger.error(f"Error en API Velocidad: {e}")
        return jsonify({'success': False, 'error': 'Error interno'}), 500

# Funciones auxiliares optimizadas
def clasificar_imc(imc):
    """Clasifica el IMC de forma optimizada"""
    if imc < 18.5:
        return {"categoria": "Bajo peso", "color": "blue"}
    elif 18.5 <= imc < 25:
        return {"categoria": "Peso normal", "color": "green"}
    elif 25 <= imc < 30:
        return {"categoria": "Sobrepeso", "color": "orange"}
    else:
        return {"categoria": "Obesidad", "color": "red"}

def interpretar_percentil(percentil):
    """Interpreta el percentil de forma optimizada"""
    if percentil <= 3:
        return {"interpretacion": "Por debajo del rango normal", "color": "red"}
    elif percentil <= 10:
        return {"interpretacion": "Límite inferior normal", "color": "orange"}
    elif percentil <= 90:
        return {"interpretacion": "Rango normal", "color": "green"}
    elif percentil <= 97:
        return {"interpretacion": "Límite superior normal", "color": "orange"}
    else:
        return {"interpretacion": "Por encima del rango normal", "color": "red"}

def evaluar_velocidad_crecimiento(velocidad):
    """Evalúa la velocidad de crecimiento"""
    if velocidad < 4:
        return {"evaluacion": "Velocidad lenta", "color": "red"}
    elif 4 <= velocidad <= 7:
        return {"evaluacion": "Velocidad normal", "color": "green"}
    else:
        return {"evaluacion": "Velocidad rápida", "color": "orange"}

if __name__ == '__main__':
    logger.info("Iniciando aplicación antropométrica para Raspberry Pi 5")
    app.run(debug=False, host='0.0.0.0', port=5000)