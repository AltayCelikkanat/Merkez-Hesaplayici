@echo off
chcp 65001 >nul
echo ------------------------------------------
echo   A-Terminal v6.2 Kurulum ve Baslatma
echo ------------------------------------------
echo Gerekli kutuphaneler kontrol ediliyor...
pip install -r requirements.txt

echo.
echo Kurulum tamamlandi. Program baslatiliyor...
python hesaplayıcı.py

echo.
echo Islem tamamlandi. Pencereyi kapatabilirsiniz.
pause