# Calculadora Antropométrica

Una aplicación web moderna para cálculos antropométricos pediátricos basada en datos de SEGHNP y WebPediátrica.

## Características

- **Cálculo de IMC**: Calcula el índice de masa corporal y su clasificación
- **Talla Diana Familiar**: Estima la talla esperada basada en la talla de los padres
- **Percentiles**: Calcula percentiles para peso, talla e IMC por edad y sexo
- **Velocidad de Crecimiento**: Evalúa la velocidad de crecimiento en cm/año
- **Interfaz Moderna**: Diseño responsivo con Bootstrap 5
- **API REST**: Endpoints para integración con otros sistemas

## Fuentes de Datos

- **SEGHNP**: Sociedad Española de Gastroenterología, Hepatología y Nutrición Pediátrica
- **WebPediátrica**: Recursos de endocrinología pediátrica

## Instalación

### Con Docker (Recomendado)

1. Clona el repositorio:
```bash
git clone <repository-url>
cd antropometria-app
```

2. Construye y ejecuta los contenedores:
```bash
docker-compose up -d
```

3. Accede a la aplicación en: http://localhost:8080

### Instalación Manual

1. Crea un entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate     # En Windows
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Ejecuta los scrapers para obtener los datos:
```bash
python scraper_seghnp.py
python scraper_webpediatrica.py
python data_fusion.py
```

4. Inicia la aplicación:
```bash
flask run
# o
python app.py
```

## Estructura del Proyecto

```
antropometria-app/
├── app.py                      # Aplicación Flask principal
├── scraper_seghnp.py           # Scraper para SEGHNP
├── scraper_webpediatrica.py    # Scraper para WebPediátrica
├── data_fusion.py              # Fusión de datos
├── templates/                  # Templates HTML
│   ├── base.html
│   └── index.html
├── static/                     # Archivos estáticos
│   ├── css/
│   ├── js/
│   └── images/
├── nginx/                      # Configuración Nginx
├── data/                       # Datos antropométricos
├── logs/                       # Logs de la aplicación
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Configuración Docker Compose
├── requirements.txt            # Dependencias Python
└── README.md                   # Este archivo
```

## API Endpoints

### POST /api/calcular_imc
Calcula el IMC y su clasificación.

**Parámetros:**
- `peso`: Peso en kg (float)
- `talla`: Talla en cm (float)

**Respuesta:**
```json
{
  "success": true,
  "imc": 18.5,
  "clasificacion": {
    "categoria": "Peso normal",
    "color": "green"
  }
}
```

### POST /api/calcular_talla_diana
Calcula la talla diana familiar.

**Parámetros:**
- `talla_padre`: Talla del padre en cm (float)
- `talla_madre`: Talla de la madre en cm (float)
- `sexo_hijo`: Sexo del hijo ("masculino" o "femenino")

### POST /api/calcular_percentil
Calcula el percentil de una medida antropométrica.

**Parámetros:**
- `medida`: Valor de la medida (float)
- `edad_meses`: Edad en meses (int)
- `sexo`: Sexo ("masculino" o "femenino")
- `tipo_medida`: Tipo de medida ("peso", "talla", "imc")

### POST /api/calcular_velocidad_crecimiento
Calcula la velocidad de crecimiento.

**Parámetros:**
- `talla_inicial`: Talla inicial en cm (float)
- `talla_actual`: Talla actual en cm (float)
- `tiempo_meses`: Tiempo transcurrido en meses (int)

### GET /api/datos_completos
Retorna todos los datos antropométricos disponibles.

## Configuración

### Variables de Entorno

- `FLASK_ENV`: Entorno de Flask (development/production)
- `FLASK_APP`: Archivo principal de la aplicación (app.py)

### Docker Compose

El archivo `docker-compose.yml` incluye:
- **antropometria-app**: Aplicación Flask principal
- **nginx**: Proxy reverso y balanceador de carga
- **redis**: Cache opcional para mejorar el rendimiento

## Desarrollo

### Ejecutar en modo desarrollo
```bash
export FLASK_ENV=development
flask run --debug
```

### Actualizar datos
```bash
python scraper_seghnp.py
python scraper_webpediatrica.py
python data_fusion.py
```

### Tests
```bash
python -m pytest tests/
```

## Seguridad

- Rate limiting implementado en Nginx
- Validación de entrada en todos los endpoints
- Headers de seguridad configurados
- Usuario no-root en contenedores Docker

## Performance

- Compresión gzip habilitada
- Cache de archivos estáticos
- Proxy buffering configurado
- Health checks implementados

## Contribuir

1. Fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit de tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## Soporte

Para soporte o preguntas:
- Crea un issue en GitHub
- Contacta al equipo de desarrollo

## Disclaimer

Esta herramienta está diseñada para uso profesional médico. Los resultados deben ser interpretados por profesionales de la salud calificados. No sustituye el criterio clínico profesional.# antropometria
