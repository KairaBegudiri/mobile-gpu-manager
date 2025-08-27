#!/bin/bash

APP_NAME="Mobile GPU Manager"
APP_EXEC="$HOME/.kmgm/kmgm.py"
APP_ICON="$HOME/.kmgm/qyzyl.png"
DESKTOP_FILE="$HOME/.local/share/applications/kmgm.desktop"

echo "Mobile GPU Manager kurulumu başlıyor..."

echo "Bağımlılıklar yükleniyor..."
if command -v pacman &> /dev/null
then
    sudo pacman -S --needed python-gobject gtk3
elif command -v apt &> /dev/null
then
    sudo apt update
    sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
else
    echo "Paket yöneticisi desteklenmiyor. Lütfen bağımlılıkları manuel yükle."
fi

echo "Uygulama klasörü oluşturuluyor..."
mkdir -p "$HOME/.kmgm"
cp kmgm.py "$APP_EXEC"

if [ -f "qyzyl.png" ]; then
    cp qyzyl.png "$APP_ICON"
fi

echo "Masaüstü kısayolu oluşturuluyor..."
cat > "$DESKTOP_FILE" << EOL
[Desktop Entry]
Name=$APP_NAME
Comment=Mobile GPU Manager Python GTK Uygulaması
Exec=python3 $APP_EXEC
Icon=$APP_ICON
Terminal=false
Type=Application
Categories=Utility;
EOL

chmod +x "$DESKTOP_FILE"

echo "Kurulum tamamlandı! Uygulama menüsünden Mobile GPU Manager'yi bulabilirsin."
