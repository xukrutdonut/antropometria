# 🍓 Guía de Instalación Rápida - Raspberry Pi 5

## 📋 Instalación en 5 Minutos

### 1️⃣ **Copiar archivos al Raspberry Pi**
```bash
# Desde el PC actual, copiar la carpeta completa al RPi
scp -r /home/arkantu/docker/antropometria pi@[IP_DEL_RPI]:/home/pi/

# O usar rsync para mayor eficiencia
rsync -av /home/arkantu/docker/antropometria/ pi@[IP_DEL_RPI]:/home/pi/antropometria/
```

### 2️⃣ **En el Raspberry Pi 5**
```bash
# Conectar al RPi por SSH
ssh pi@[IP_DEL_RPI]

# Acceder al directorio
cd /home/pi/antropometria

# Ejecutar instalación automática
./run.rpi.sh
```

### 3️⃣ **Verificar Instalación**
```bash
# Monitorear el sistema
./monitor.rpi.sh

# Acceder a la aplicación
# http://[IP_DEL_RPI]:8080
```

## ⚡ Instalación Express (Una línea)

```bash
# Ejecutar en el Raspberry Pi 5
curl -fsSL https://raw.githubusercontent.com/[tu-repo]/main/install-rpi.sh | bash
```

## 🔧 Comandos Esenciales RPi5

### Gestión de la Aplicación
```bash
# Iniciar
./run.rpi.sh

# Monitorear
./monitor.rpi.sh continuous

# Ver logs
docker logs -f antropometria-rpi5

# Reiniciar
docker restart antropometria-rpi5

# Detener
docker stop antropometria-rpi5
```

### Monitoreo del Sistema
```bash
# Temperatura
vcgencmd measure_temp

# Memoria
free -h

# CPU
htop

# Red
ip addr show
```

## 🚨 Resolución Rápida de Problemas

### ❌ Error: "No se puede conectar"
```bash
# Verificar que Docker esté corriendo
sudo systemctl status docker

# Verificar puerto
sudo netstat -tlnp | grep :8080

# Reiniciar Docker
sudo systemctl restart docker
./run.rpi.sh
```

### 🌡️ Error: "Temperatura alta"
```bash
# Ver temperatura
vcgencmd measure_temp

# Si >70°C, parar temporalmente
docker stop antropometria-rpi5

# Mejorar ventilación y reiniciar
./run.rpi.sh
```

### 💾 Error: "Sin espacio"
```bash
# Limpiar Docker
docker system prune -a

# Limpiar logs
sudo journalctl --vacuum-size=100M

# Verificar espacio
df -h
```

### 🧠 Error: "Sin memoria"
```bash
# Liberar memoria
sudo systemctl stop [servicios-no-necesarios]

# Aumentar swap
sudo dphys-swapfile swapoff
sudo sed -i 's/CONF_SWAPSIZE=.*/CONF_SWAPSIZE=2048/' /etc/dphys-swapfile
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📱 Acceso desde Otros Dispositivos

### Desde PC/Móvil en la misma red
1. Obtener IP del RPi: `hostname -I`
2. Abrir navegador: `http://[IP_DEL_RPI]:8080`

### Desde Internet (Opcional)
```bash
# Configurar port forwarding en router
# Puerto externo: 8080 → IP_RPi:8080

# O usar túnel SSH
ssh -L 8080:localhost:8080 pi@[IP_DEL_RPI]
# Luego acceder a http://localhost:8080
```

## 🎯 Optimizaciones Específicas RPi5

### Archivo `/boot/config.txt` (Opcional)
```bash
# Editar configuración
sudo nano /boot/config.txt

# Añadir al final (SOLO si temperatura <65°C):
# Overclock moderado
arm_freq=2200
gpu_freq=750

# Memoria GPU mínima (solo si no usas GUI)
gpu_mem=16

# Reiniciar para aplicar
sudo reboot
```

### Configuración de Red
```bash
# IP estática (opcional)
sudo nano /etc/dhcpcd.conf

# Añadir:
# interface eth0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=8.8.8.8
```

## 📊 Métricas de Rendimiento RPi5

### Valores Normales
- **CPU**: 15-30% en uso normal
- **Temperatura**: 45-65°C
- **RAM**: 200-400MB usados
- **Respuesta API**: 50-200ms

### Alarmas
- **CPU**: >80% sostenido
- **Temperatura**: >70°C
- **RAM**: >80% usada
- **Respuesta**: >1000ms

## 🛠️ Mantenimiento

### Diario
```bash
# Check rápido
./monitor.rpi.sh stats
```

### Semanal
```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Limpiar Docker
docker system prune

# Verificar logs
docker logs antropometria-rpi5 --tail 50
```

### Mensual
```bash
# Backup de configuración
tar -czf backup-antropometria-$(date +%Y%m%d).tar.gz antropometria/

# Verificar salud del SD
sudo fsck -f /dev/mmcblk0p2
```

## 📞 Soporte

### Información del Sistema
```bash
# Información completa para soporte
echo "=== INFORMACIÓN DEL SISTEMA ===" > support-info.txt
uname -a >> support-info.txt
cat /proc/cpuinfo | grep Model >> support-info.txt
free -h >> support-info.txt
df -h >> support-info.txt
docker --version >> support-info.txt
docker ps >> support-info.txt
./monitor.rpi.sh stats >> support-info.txt
```

### Enlaces Útiles
- [Raspberry Pi OS](https://www.raspberrypi.org/software/)
- [Docker for ARM](https://docs.docker.com/engine/install/debian/)
- [Overclock RPi5](https://www.raspberrypi.org/documentation/configuration/config-txt/)

---

## ✅ ¡Listo para Raspberry Pi 5!

Tu aplicación antropométrica está **completamente optimizada** para Raspberry Pi 5 con:

🍓 **ARM64 nativo**  
⚡ **Gestión inteligente de recursos**  
🌡️ **Monitoreo térmico**  
📊 **Scripts de monitoreo**  
🔧 **Instalación automatizada**  
📱 **Acceso desde cualquier dispositivo**  

**Disfruta de tu calculadora antropométrica en Raspberry Pi 5!** 🎉