#!/bin/bash

# Script optimizado para ejecutar en Raspberry Pi 5
# Calculadora Antropométrica

echo "🍓 Iniciando aplicación antropométrica en Raspberry Pi 5..."

# Verificar arquitectura del sistema
ARCH=$(uname -m)
echo "🔍 Arquitectura detectada: $ARCH"

if [[ "$ARCH" != "aarch64" && "$ARCH" != "arm64" ]]; then
    echo "⚠️  Advertencia: Este script está optimizado para ARM64/aarch64 (Raspberry Pi 5)"
    echo "   Arquitectura actual: $ARCH"
    read -p "¿Continuar de todos modos? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado."
    echo "💡 Para instalar Docker en Raspberry Pi 5:"
    echo "   curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "   sudo sh get-docker.sh"
    echo "   sudo usermod -aG docker \$USER"
    exit 1
fi

# Verificar memoria disponible
MEMORY_KB=$(grep MemAvailable /proc/meminfo | awk '{print $2}')
MEMORY_MB=$((MEMORY_KB / 1024))
echo "🧠 Memoria disponible: ${MEMORY_MB} MB"

if [ $MEMORY_MB -lt 512 ]; then
    echo "⚠️  Advertencia: Memoria baja (${MEMORY_MB} MB). Se recomienda al menos 512 MB libres."
fi

# Verificar espacio en disco
DISK_SPACE=$(df / | awk 'NR==2 {print $4}')
DISK_SPACE_MB=$((DISK_SPACE / 1024))
echo "💾 Espacio disponible: ${DISK_SPACE_MB} MB"

if [ $DISK_SPACE_MB -lt 2048 ]; then
    echo "⚠️  Advertencia: Poco espacio en disco (${DISK_SPACE_MB} MB)"
fi

# Detener contenedor existente
if [ $(docker ps -q -f name=antropometria-rpi5) ]; then
    echo "🛑 Deteniendo contenedor existente..."
    docker stop antropometria-rpi5
    docker rm antropometria-rpi5
fi

# Limpiar imágenes antiguas si hay poco espacio
if [ $DISK_SPACE_MB -lt 1024 ]; then
    echo "🧹 Limpiando imágenes Docker antiguas..."
    docker system prune -f
fi

# Construir imagen optimizada para RPi
echo "🔨 Construyendo imagen Docker para Raspberry Pi 5..."
echo "   (Esto puede tardar varios minutos en la primera ejecución)"

# Usar buildx para arquitectura ARM64 si está disponible
if docker buildx version &> /dev/null; then
    echo "🏗️  Usando Docker Buildx para optimización ARM64..."
    docker buildx build --platform linux/arm64 -f Dockerfile.rpi -t antropometria-rpi .
else
    echo "🏗️  Usando Docker build estándar..."
    docker build -f Dockerfile.rpi -t antropometria-rpi .
fi

# Verificar si la construcción fue exitosa
if [ $? -ne 0 ]; then
    echo "❌ Error al construir la imagen Docker"
    echo "💡 Consejos para resolver problemas:"
    echo "   - Verificar conexión a internet"
    echo "   - Liberar espacio en disco: docker system prune -a"
    echo "   - Reintentar después de reiniciar el RPi"
    exit 1
fi

# Buscar puerto disponible
PORT=8080
while netstat -tlnp 2>/dev/null | grep -q ":$PORT "; do
    PORT=$((PORT + 1))
    echo "Puerto $((PORT - 1)) ocupado, probando puerto $PORT..."
done

# Crear directorios necesarios
mkdir -p logs data

echo "🚀 Iniciando aplicación en puerto $PORT..."
echo "⏳ Configuración optimizada para Raspberry Pi 5:"
echo "   - Memoria limitada: 1GB"
echo "   - CPU limitada: 2 cores"
echo "   - Workers: 2 (optimizado para RPi)"
echo "   - Threads: 4 por worker"

# Ejecutar contenedor optimizado para RPi
docker run -d \
  --name antropometria-rpi5 \
  --restart unless-stopped \
  --memory="1g" \
  --cpus="2.0" \
  --oom-kill-disable=false \
  -p $PORT:5000 \
  -v "$(pwd)/logs:/app/logs" \
  -v "$(pwd)/data:/app/data:ro" \
  -e TZ="Europe/Madrid" \
  -e FLASK_ENV="production" \
  antropometria-rpi

# Verificar que el contenedor esté corriendo
sleep 15
echo "🔍 Verificando estado del contenedor..."

if [ $(docker ps -q -f name=antropometria-rpi5) ]; then
    echo "✅ ¡Aplicación iniciada correctamente en Raspberry Pi 5!"
    echo ""
    echo "🌐 Acceso:"
    echo "   URL Local: http://localhost:$PORT"
    
    # Detectar IP local
    LOCAL_IP=$(hostname -I | awk '{print $1}')
    if [ -n "$LOCAL_IP" ]; then
        echo "   URL Red:   http://$LOCAL_IP:$PORT"
    fi
    
    echo ""
    echo "📊 Endpoints API disponibles:"
    echo "   • POST /api/calcular_imc"
    echo "   • POST /api/calcular_percentil" 
    echo "   • POST /api/calcular_talla_diana"
    echo "   • POST /api/calcular_velocidad_crecimiento"
    echo "   • GET  /health (monitoreo)"
    echo ""
    echo "🔧 Comandos útiles:"
    echo "   Ver logs:     docker logs -f antropometria-rpi5"
    echo "   Estadísticas: docker stats antropometria-rpi5"
    echo "   Detener:      docker stop antropometria-rpi5"
    echo "   Reiniciar:    docker restart antropometria-rpi5"
    echo ""
    echo "📊 Monitoreo del sistema:"
    echo "   CPU:    docker stats --no-stream antropometria-rpi5 | awk 'NR==2{print \$3}'"
    echo "   Memoria: docker stats --no-stream antropometria-rpi5 | awk 'NR==2{print \$7}'"
    echo ""
    
    # Mostrar estadísticas iniciales
    echo "📈 Estadísticas iniciales:"
    docker stats --no-stream antropometria-rpi5
    
    # Test rápido de la aplicación
    echo "🧪 Realizando test rápido..."
    sleep 5
    
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        echo "✅ Test de conectividad: OK"
    else
        echo "⚠️  Test de conectividad: Falló (la app puede necesitar más tiempo para iniciar)"
    fi
    
else
    echo "❌ Error al iniciar la aplicación"
    echo ""
    echo "🔍 Diagnóstico:"
    echo "Logs del contenedor:"
    docker logs antropometria-rpi5 2>/dev/null || echo "No hay logs disponibles"
    echo ""
    echo "💡 Posibles soluciones:"
    echo "   1. Verificar logs: docker logs antropometria-rpi5"
    echo "   2. Liberar memoria: free -m"
    echo "   3. Reiniciar RPi: sudo reboot"
    echo "   4. Limpiar Docker: docker system prune -a"
    exit 1
fi