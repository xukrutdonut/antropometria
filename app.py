#!/usr/bin/env python3
"""
Aplicación Flask para cálculos antropométricos
"""

from flask import Flask, render_template, request, jsonify, send_file
import json
import pandas as pd
import numpy as np
from datetime import datetime, date
import os
import math

app = Flask(__name__)

class AnthropometricCalculator:
    def __init__(self):
        self.data = {}
        self.load_anthropometric_data()
    
    def load_anthropometric_data(self):
        """Carga los datos antropométricos fusionados"""
        try:
            if os.path.exists('fused_anthropometric_data.json'):
                with open('fused_anthropometric_data.json', 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            else:
                print("Archivo de datos no encontrado, usando datos por defecto")
                self.create_default_data()
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.create_default_data()
    
    def create_default_data(self):
        """Crea datos por defecto si no hay archivo de datos"""
        self.data = {
            'metadatos': {
                'titulo': 'Calculadora Antropométrica',
                'version': '1.0'
            },
            'tablas_percentiles': {},
            'funciones_calculo': {}
        }
    
    def calcular_imc(self, peso_kg, talla_cm):
        """Calcula el IMC"""
        if talla_cm <= 0:
            return None
        talla_m = talla_cm / 100
        return round(peso_kg / (talla_m ** 2), 2)
    
    def calcular_talla_diana_familiar(self, talla_padre, talla_madre, sexo_hijo):
        """Calcula la talla diana familiar"""
        if sexo_hijo.lower() == 'masculino':
            talla_diana = (talla_padre + talla_madre + 13) / 2
        else:
            talla_diana = (talla_padre + talla_madre - 13) / 2
        
        return {
            'talla_diana': round(talla_diana, 1),
            'rango_inferior': round(talla_diana - 8.5, 1),
            'rango_superior': round(talla_diana + 8.5, 1)
        }
    
    def calcular_velocidad_crecimiento(self, talla_inicial, talla_actual, tiempo_meses):
        """Calcula la velocidad de crecimiento"""
        if tiempo_meses <= 0:
            return None
        
        diferencia_talla = talla_actual - talla_inicial
        velocidad_cm_mes = diferencia_talla / tiempo_meses
        velocidad_cm_año = velocidad_cm_mes * 12
        
        return round(velocidad_cm_año, 2)
    
    def estimar_percentil(self, medida, edad_meses, sexo, tipo_medida):
        """Estima el percentil de una medida"""
        # Función simplificada para estimación de percentiles
        # En una implementación real, usaríamos las tablas de datos reales
        
        percentiles_ref = [3, 10, 25, 50, 75, 90, 97]
        
        # Valores de referencia simplificados por tipo de medida y edad
        if tipo_medida == 'peso':
            if edad_meses <= 12:
                valores_ref = [7, 8.5, 9.5, 10.5, 11.5, 13, 14.5] if sexo == 'masculino' else [6.5, 8, 9, 10, 11, 12.5, 14]
            elif edad_meses <= 36:
                valores_ref = [10, 12, 13.5, 15, 16.5, 18, 20] if sexo == 'masculino' else [9.5, 11.5, 13, 14.5, 16, 17.5, 19]
            else:
                edad_años = edad_meses / 12
                base = 2 * edad_años + 8 if sexo == 'masculino' else 2 * edad_años + 7.5
                valores_ref = [base*0.8, base*0.87, base*0.93, base, base*1.15, base*1.30, base*1.45]
        
        elif tipo_medida == 'talla':
            if edad_meses <= 12:
                valores_ref = [68, 72, 75, 78, 81, 84, 87] if sexo == 'masculino' else [66, 70, 73, 76, 79, 82, 85]
            else:
                edad_años = edad_meses / 12
                base = 85 + (edad_años - 1) * 6 if sexo == 'masculino' else 83 + (edad_años - 1) * 5.5
                valores_ref = [base*0.92, base*0.95, base*0.97, base, base*1.03, base*1.06, base*1.09]
        
        elif tipo_medida == 'imc':
            if edad_meses < 24:
                return None  # IMC no se calcula antes de los 2 años
            valores_ref = [14, 15, 15.5, 16.5, 18, 19.5, 21.5]
        
        else:
            return None
        
        # Encontrar el percentil más cercano
        for i, valor_ref in enumerate(valores_ref):
            if medida <= valor_ref:
                return percentiles_ref[i]
        
        return percentiles_ref[-1]  # Mayor al P97

calculator = AnthropometricCalculator()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/calcular_imc', methods=['POST'])
def api_calcular_imc():
    """API para calcular IMC"""
    try:
        data = request.get_json()
        peso = float(data['peso'])
        talla = float(data['talla'])
        
        imc = calculator.calcular_imc(peso, talla)
        
        return jsonify({
            'success': True,
            'imc': imc,
            'clasificacion': clasificar_imc(imc) if imc else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/calcular_talla_diana', methods=['POST'])
def api_calcular_talla_diana():
    """API para calcular talla diana familiar"""
    try:
        data = request.get_json()
        talla_padre = float(data['talla_padre'])
        talla_madre = float(data['talla_madre'])
        sexo_hijo = data['sexo_hijo']
        
        resultado = calculator.calcular_talla_diana_familiar(talla_padre, talla_madre, sexo_hijo)
        
        return jsonify({
            'success': True,
            'resultado': resultado
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/calcular_percentil', methods=['POST'])
def api_calcular_percentil():
    """API para calcular percentiles"""
    try:
        data = request.get_json()
        medida = float(data['medida'])
        edad_meses = int(data['edad_meses'])
        sexo = data['sexo']
        tipo_medida = data['tipo_medida']
        
        percentil = calculator.estimar_percentil(medida, edad_meses, sexo, tipo_medida)
        
        return jsonify({
            'success': True,
            'percentil': percentil,
            'interpretacion': interpretar_percentil(percentil) if percentil else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/calcular_velocidad_crecimiento', methods=['POST'])
def api_calcular_velocidad_crecimiento():
    """API para calcular velocidad de crecimiento"""
    try:
        data = request.get_json()
        talla_inicial = float(data['talla_inicial'])
        talla_actual = float(data['talla_actual'])
        tiempo_meses = int(data['tiempo_meses'])
        
        velocidad = calculator.calcular_velocidad_crecimiento(talla_inicial, talla_actual, tiempo_meses)
        
        return jsonify({
            'success': True,
            'velocidad_cm_año': velocidad,
            'evaluacion': evaluar_velocidad_crecimiento(velocidad) if velocidad else None
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/datos_completos')
def api_datos_completos():
    """Retorna todos los datos antropométricos disponibles"""
    return jsonify(calculator.data)

def clasificar_imc(imc):
    """Clasifica el IMC según rangos estándar"""
    if imc < 18.5:
        return {"categoria": "Bajo peso", "color": "blue"}
    elif 18.5 <= imc < 25:
        return {"categoria": "Peso normal", "color": "green"}
    elif 25 <= imc < 30:
        return {"categoria": "Sobrepeso", "color": "orange"}
    else:
        return {"categoria": "Obesidad", "color": "red"}

def interpretar_percentil(percentil):
    """Interpreta el percentil obtenido"""
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
    app.run(debug=True, host='0.0.0.0', port=5000)