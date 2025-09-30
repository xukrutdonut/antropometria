#!/bin/bash

# Script para ejecutar la aplicación antropométrica

echo "🏗️  Iniciando aplicación antropométrica..."

# Verificar si Docker está disponible
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Por favor instale Docker primero."
    exit 1
fi

# Construir la imagen si es necesario
echo "🔨 Construyendo imagen Docker..."
docker build -t antropometria-app .

# Detener contenedor existente si está corriendo
if [ $(docker ps -q -f name=antropometria-web) ]; then
    echo "🛑 Deteniendo contenedor existente..."
    docker stop antropometria-web
    docker rm antropometria-web
fi

# Buscar puerto disponible
PORT=8082
while netstat -tlnp 2>/dev/null | grep -q ":$PORT "; do
    PORT=$((PORT + 1))
    echo "Puerto $((PORT - 1)) ocupado, probando puerto $PORT..."
done

echo "🚀 Iniciando aplicación en puerto $PORT..."
docker run -d --name antropometria-web -p $PORT:5000 antropometria-app

# Esperar a que la aplicación esté lista
echo "⏳ Esperando a que la aplicación esté lista..."
sleep 10

# Verificar estado
if [ $(docker ps -q -f name=antropometria-web) ]; then
    echo "✅ Aplicación iniciada correctamente!"
    echo "🌐 Accede a: http://localhost:$PORT"
    echo ""
    echo "📊 Endpoints disponibles:"
    echo "  • Aplicación principal: http://localhost:$PORT"
    echo "  • API IMC: POST http://localhost:$PORT/api/calcular_imc"
    echo "  • API Percentiles: POST http://localhost:$PORT/api/calcular_percentil"
    echo "  • API Talla Diana: POST http://localhost:$PORT/api/calcular_talla_diana"
    echo "  • API Velocidad: POST http://localhost:$PORT/api/calcular_velocidad_crecimiento"
    echo ""
    echo "🔧 Para ver logs: docker logs -f antropometria-web"
    echo "🛑 Para detener: docker stop antropometria-web"
else
    echo "❌ Error al iniciar la aplicación"
    echo "Ver logs: docker logs antropometria-web"
    exit 1
fi