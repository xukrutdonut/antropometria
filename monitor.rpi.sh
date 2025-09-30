#!/bin/bash

# Script de monitoreo para Raspberry Pi 5
# Calculadora Antropométrica

echo "📊 Monitor de sistema - Calculadora Antropométrica RPi5"
echo "=================================================="

# Función para mostrar estadísticas del sistema
show_system_stats() {
    echo "🖥️  ESTADÍSTICAS DEL SISTEMA"
    echo "----------------------------"
    
    # CPU
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    echo "CPU: ${CPU_USAGE}% usado"
    
    # Memoria
    MEMORY_TOTAL=$(free -m | awk 'NR==2{printf "%.0f", $2}')
    MEMORY_USED=$(free -m | awk 'NR==2{printf "%.0f", $3}')
    MEMORY_PERCENT=$(free -m | awk 'NR==2{printf "%.1f", $3*100/$2}')
    echo "Memoria: ${MEMORY_USED}/${MEMORY_TOTAL} MB (${MEMORY_PERCENT}%)"
    
    # Temperatura del CPU (específico para RPi)
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
        TEMP_C=$((TEMP/1000))
        echo "Temperatura CPU: ${TEMP_C}°C"
        
        if [ $TEMP_C -gt 70 ]; then
            echo "⚠️  Temperatura alta detectada!"
        fi
    fi
    
    # Espacio en disco
    DISK_USAGE=$(df / | awk 'NR==2 {print $5}')
    echo "Disco: ${DISK_USAGE} usado"
    
    echo ""
}

# Función para mostrar estadísticas de Docker
show_docker_stats() {
    echo "🐳 ESTADÍSTICAS DE DOCKER"
    echo "-------------------------"
    
    if [ $(docker ps -q -f name=antropometria-rpi5) ]; then
        echo "Estado del contenedor: ✅ ACTIVO"
        
        # Estadísticas detalladas
        docker stats --no-stream antropometria-rpi5 | awk '
        NR==1 {print "Contenedor\t\tCPU\t\tMemoria\t\tRed I/O\t\tDisco I/O"}
        NR==2 {printf "%-15s\t%s\t\t%s\t%s\t%s\n", $1, $3, $7, $8, $11}
        '
        
        echo ""
        
        # Logs recientes
        echo "📝 LOGS RECIENTES (últimas 10 líneas):"
        echo "--------------------------------------"
        docker logs --tail 10 antropometria-rpi5 2>/dev/null
        
    else
        echo "Estado del contenedor: ❌ INACTIVO"
        echo ""
        echo "💡 Para iniciar la aplicación:"
        echo "   ./run.rpi.sh"
    fi
    
    echo ""
}

# Función para mostrar conectividad
test_connectivity() {
    echo "🌐 TEST DE CONECTIVIDAD"
    echo "----------------------"
    
    if [ $(docker ps -q -f name=antropometria-rpi5) ]; then
        # Detectar puerto
        PORT=$(docker port antropometria-rpi5 5000/tcp | cut -d':' -f2)
        
        if [ -n "$PORT" ]; then
            echo "Puerto detectado: $PORT"
            
            # Test health check
            if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
                echo "Health check: ✅ OK"
            else
                echo "Health check: ❌ FALLO"
            fi
            
            # Test API básico
            API_TEST=$(curl -s -X POST "http://localhost:$PORT/api/calcular_imc" \
                -H "Content-Type: application/json" \
                -d '{"peso": 70, "talla": 170}' | jq -r '.success' 2>/dev/null)
                
            if [ "$API_TEST" = "true" ]; then
                echo "API Test: ✅ OK"
            else
                echo "API Test: ❌ FALLO"
            fi
            
            # Mostrar URLs de acceso
            LOCAL_IP=$(hostname -I | awk '{print $1}')
            echo ""
            echo "🔗 URLs de acceso:"
            echo "   Local: http://localhost:$PORT"
            if [ -n "$LOCAL_IP" ]; then
                echo "   Red:   http://$LOCAL_IP:$PORT"
            fi
        else
            echo "❌ No se pudo detectar el puerto"
        fi
    else
        echo "❌ Contenedor no está corriendo"
    fi
    
    echo ""
}

# Función para mostrar recursos recomendados
show_recommendations() {
    echo "💡 RECOMENDACIONES DE OPTIMIZACIÓN"
    echo "=================================="
    
    # Verificar memoria
    MEMORY_PERCENT=$(free -m | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ $MEMORY_PERCENT -gt 80 ]; then
        echo "⚠️  Uso de memoria alto (${MEMORY_PERCENT}%)"
        echo "   - Reiniciar contenedor: docker restart antropometria-rpi5"
        echo "   - Limpiar cache: docker exec antropometria-rpi5 python -c 'import gc; gc.collect()'"
    fi
    
    # Verificar temperatura
    if [ -f /sys/class/thermal/thermal_zone0/temp ]; then
        TEMP_C=$(cat /sys/class/thermal/thermal_zone0/temp | awk '{print int($1/1000)}')
        if [ $TEMP_C -gt 65 ]; then
            echo "🌡️  Temperatura elevada (${TEMP_C}°C)"
            echo "   - Verificar ventilación"
            echo "   - Considerar reducir carga de trabajo"
        fi
    fi
    
    # Verificar espacio en disco
    DISK_PERCENT=$(df / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    if [ $DISK_PERCENT -gt 85 ]; then
        echo "💾 Espacio en disco bajo (${DISK_PERCENT}%)"
        echo "   - Limpiar Docker: docker system prune -a"
        echo "   - Limpiar logs: docker logs antropometria-rpi5 --tail 100 > temp.log"
    fi
    
    echo ""
}

# Función principal de monitoreo continuo
continuous_monitor() {
    echo "🔄 MONITOREO CONTINUO INICIADO"
    echo "Presiona Ctrl+C para salir"
    echo "=============================="
    
    while true; do
        clear
        echo "📊 Monitor Antropométrica RPi5 - $(date '+%Y-%m-%d %H:%M:%S')"
        echo "============================================================="
        
        show_system_stats
        show_docker_stats
        test_connectivity
        
        # Esperar 30 segundos antes del siguiente update
        sleep 30
    done
}

# Menú principal
case "$1" in
    "stats"|"s")
        show_system_stats
        show_docker_stats
        ;;
    "test"|"t")
        test_connectivity
        ;;
    "recommendations"|"r")
        show_recommendations
        ;;
    "continuous"|"c"|"monitor"|"m")
        continuous_monitor
        ;;
    "all"|"")
        show_system_stats
        show_docker_stats
        test_connectivity
        show_recommendations
        ;;
    *)
        echo "🍓 Monitor Calculadora Antropométrica - Raspberry Pi 5"
        echo "======================================================"
        echo ""
        echo "Uso: $0 [opción]"
        echo ""
        echo "Opciones:"
        echo "  stats|s           - Mostrar estadísticas del sistema y Docker"
        echo "  test|t            - Probar conectividad y APIs"
        echo "  recommendations|r - Mostrar recomendaciones de optimización"
        echo "  continuous|c|m    - Monitoreo continuo (actualización cada 30s)"
        echo "  all               - Mostrar todo (por defecto)"
        echo ""
        echo "Ejemplos:"
        echo "  $0                # Mostrar todo"
        echo "  $0 stats          # Solo estadísticas"
        echo "  $0 continuous     # Monitor en tiempo real"
        ;;
esac