#!/bin/bash

# --- Resolve API Ortamını Ayarlama (Mac İçin Sabit Yol) ---
RESOLVE_API="/Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules"

# Resolve API modülünün bulunması için PYTHONPATH'e eklenmesi
export PYTHONPATH="$PYTHONPATH:$RESOLVE_API"

# Resolve'un özel ortam değişkeninin ayarlanması
export DAVINCI_RESOLVE_SCRIPT_API="$RESOLVE_API"

# --- Scripti Çalıştırma ---

# Betiğin bulunduğu dizini alır (Bu, /Users/nehiratabek/Projects/batch_renamer/ olmalıdır)
SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

# yaptığım batch_rename.py dosyasının tam yolu
PYTHON_SCRIPT="$SCRIPT_DIR/batch_rename.py"

echo "Resolve API yolu ayarlandı: $RESOLVE_API"
echo "Python scripti çalıştırılıyor: $PYTHON_SCRIPT"
echo "------------------------------------------------------"

# Python 3 ile ana scripti çalıştırır
python3 "$PYTHON_SCRIPT"

# Konsolun hemen kapanmaması için bekletme
echo "------------------------------------------------------"
read -p "İşlem tamamlandı. Kapatmak için Enter'a basın."