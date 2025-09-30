# 🍓 Calculadora Antropométrica - Raspberry Pi 5

Aplicación web dockerizada optimizada específicamente para **Raspberry Pi 5** que combina datos antropométricos de SEGHNP y WebPediátrica.

## 🎯 Optimizaciones para Raspberry Pi 5

### ✅ **Arquitectura ARM64 Nativa**
- Dockerfile específico para ARM64/aarch64
- Dependencias optimizadas para Raspberry Pi
- Compilación nativa sin emulación

### 🧠 **Gestión de Memoria Optimizada**
- Límite de memoria: 1GB por contenedor
- Cache inteligente con limpieza automática
- Garbage collection optimizado para ARM
- Workers reducidos (2 en lugar de 4)

### ⚡ **Rendimiento CPU**
- Máximo 2 cores utilizados
- 4 threads por worker (gthread)
- Timeouts optimizados para hardware ARM
- Proceso de construcción paralelo

### 🌡️ **Monitoreo Térmico**
- Monitoreo de temperatura del SoC
- Alertas por sobrecalentamiento
- Recomendaciones de refrigeración

## 🚀 Instalación en Raspberry Pi 5

### Prerrequisitos

1. **Raspberry Pi OS** (64-bit recomendado)
```bash
# Verificar arquitectura
uname -m  # Debe mostrar aarch64
```

2. **Docker instalado**
```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Reiniciar sesión
sudo reboot
```

3. **Recursos mínimos recomendados**
- RAM: 2GB+ (4GB recomendados)
- Almacenamiento: 8GB libres
- Conexión a Internet estable

### Instalación Rápida

```bash
# Clonar y acceder al directorio
cd /home/pi/
git clone <repository-url> antropometria
cd antropometria

# Ejecutar script optimizado para RPi
./run.rpi.sh
```

### Instalación Manual

```bash
# Construir imagen específica para RPi
docker build -f Dockerfile.rpi -t antropometria-rpi .

# Ejecutar con límites de recursos
docker run -d \
  --name antropometria-rpi5 \
  --restart unless-stopped \
  --memory="1g" \
  --cpus="2.0" \
  -p 8080:5000 \
  -v "$(pwd)/logs:/app/logs" \
  antropometria-rpi
```

## 📊 Monitoreo y Gestión

### Script de Monitoreo
```bash
# Hacer ejecutable el monitor
chmod +x monitor.rpi.sh

# Estadísticas completas
./monitor.rpi.sh

# Monitoreo continuo
./monitor.rpi.sh continuous

# Solo estadísticas
./monitor.rpi.sh stats

# Test de conectividad
./monitor.rpi.sh test
```

### Comandos Útiles

```bash
# Ver logs en tiempo real
docker logs -f antropometria-rpi5

# Estadísticas de recursos
docker stats antropometria-rpi5

# Acceso al contenedor
docker exec -it antropometria-rpi5 /bin/bash

# Reiniciar aplicación
docker restart antropometria-rpi5

# Detener aplicación
docker stop antropometria-rpi5
```

## 🌡️ Monitoreo del Sistema

### Temperatura del CPU
```bash
# Temperatura actual
cat /sys/class/thermal/thermal_zone0/temp | awk '{print $1/1000"°C"}'

# Monitor continuo de temperatura
watch -n 2 'cat /sys/class/thermal/thermal_zone0/temp | awk "{print \$1/1000\"°C\"}"'
```

### Memoria y CPU
```bash
# Uso de memoria
free -h

# Procesos principales
htop

# Estadísticas del sistema
vcgencmd measure_temp
vcgencmd measure_volts
```

## ⚙️ Configuraciones Específicas RPi5

### Dockerfile.rpi
- Base: `python:3.11-slim-bookworm`
- Optimizaciones ARM64 nativas
- Dependencias mínimas para reducir tamaño
- Variables de entorno optimizadas

### docker-compose.rpi.yml
- Límites de recursos específicos
- Health checks adaptados
- Logging optimizado
- Network configurado para RPi

### app.rpi.py
- Cache inteligente con limpieza automática
- Gestión de memoria optimizada
- Logging específico para RPi
- Error handling robusto

## 🔧 Resolución de Problemas

### Problemas Comunes

#### 1. **Memoria Insuficiente**
```bash
# Verificar memoria disponible
free -m

# Aumentar swap si es necesario
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=2048
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

#### 2. **Temperatura Alta**
```bash
# Verificar temperatura
vcgencmd measure_temp

# Si > 70°C:
# - Verificar ventilación
# - Reducir overclock
# - Limpiar polvo del RPi
```

#### 3. **Espacio en Disco**
```bash
# Limpiar Docker
docker system prune -a

# Limpiar logs del sistema
sudo journalctl --vacuum-size=100M

# Verificar espacio
df -h
```

#### 4. **Contenedor No Inicia**
```bash
# Ver logs detallados
docker logs antropometria-rpi5

# Verificar puertos ocupados
sudo netstat -tlnp | grep :8080

# Reiniciar Docker
sudo systemctl restart docker
```

### Optimizaciones Adicionales

#### GPU Memory Split
```bash
# Reducir memoria GPU si no se usa
sudo raspi-config
# Advanced Options > Memory Split > 16
```

#### Overclock Moderado
```bash
# Editar config.txt (OPCIONAL y con cuidado)
sudo nano /boot/config.txt

# Añadir (solo si la temperatura se mantiene <65°C):
# arm_freq=2200
# gpu_freq=750
```

## 📱 Acceso Remoto

### Desde la Red Local
```bash
# Obtener IP del RPi
hostname -I

# Acceder desde otro dispositivo
# http://[IP_DEL_RPI]:8080
```

### Túnel SSH (Acceso Externo)
```bash
# En el RPi
ssh -R 8080:localhost:8080 usuario@servidor-externo

# Desde el servidor externo
curl http://localhost:8080
```

### Nginx Reverse Proxy
```bash
# Usar configuración nginx.rpi.conf
docker run -d \
  --name nginx-rpi \
  -p 80:80 \
  -v $(pwd)/nginx/nginx.rpi.conf:/etc/nginx/nginx.conf:ro \
  --link antropometria-rpi5 \
  nginx:alpine
```

## 📈 Benchmarks Esperados en RPi5

### Rendimiento Típico
- **Tiempo respuesta API**: 50-200ms
- **Carga simultánea**: 10-20 usuarios
- **Uso CPU**: 15-30% en uso normal
- **Uso RAM**: 200-400MB
- **Temperatura**: 45-65°C (con ventilación)

### Límites Recomendados
- **Máximo usuarios simultáneos**: 50
- **Requests por minuto**: 300-500
- **Uptime objetivo**: >99%

## 🛡️ Seguridad en RPi

### Configuraciones Básicas
```bash
# Cambiar contraseña por defecto
sudo passwd pi

# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Firewall básico
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 8080
```

### SSL/TLS (Opcional)
```bash
# Generar certificados auto-firmados
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

## 📞 URLs de Acceso

Una vez instalado, la aplicación estará disponible en:

- **Local**: http://localhost:8080
- **Red local**: http://[IP_DEL_RPI]:8080
- **Health check**: http://[IP_DEL_RPI]:8080/health

## 🎉 Características Completas

✅ **Totalmente optimizado para ARM64**  
✅ **Gestión inteligente de recursos**  
✅ **Monitoreo térmico integrado**  
✅ **Scripts de automatización**  
✅ **Cache optimizado para memoria limitada**  
✅ **Logging específico para RPi**  
✅ **Health checks adaptados**  
✅ **Documentación completa**  

---
*Optimizado para Raspberry Pi 5 con 🍓 y mucho ❤️*