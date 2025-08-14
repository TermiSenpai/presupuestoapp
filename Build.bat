@echo off
setlocal
cd /d "%~dp0"

REM ==================== CONFIGURACIÓN ====================
set "APP_NAME=DTF_Pricing_Calculator"    REM Nombre de la app y carpeta de salida
set "ICON=PresupuestosDTF.ico"           REM Icono del ejecutable
set "MAIN=main.py"                       REM Archivo principal de Python
set "OUT_DIR=dist\%APP_NAME%"            REM Carpeta donde se genera la app
set "ZIP_PATH=dist\%APP_NAME%.zip"       REM Ruta final del ZIP
set "LOG_FILE=build_log.txt"             REM Archivo de log

REM ==================== INICIO DEL LOG ====================
> "%LOG_FILE%" echo ===== INICIO DEL PROCESO [%DATE% %TIME%] =====
>> "%LOG_FILE%" echo.

echo ===== INICIO DEL PROCESO =====
echo Fecha: %DATE% %TIME%
echo.

REM ==================== LIMPIEZA ====================
echo [1/5] Limpiando carpetas previas...
>> "%LOG_FILE%" echo [1/5] Limpiando carpetas previas...
if exist "build" rmdir /s /q "build"
if exist "dist"  rmdir /s /q "dist"

REM ==================== COMPILACIÓN ====================
echo [2/5] Compilando con PyInstaller...
>> "%LOG_FILE%" echo [2/5] Compilando con PyInstaller...
pyinstaller --noconfirm --clean --noconsole --onedir ^
  --name "%APP_NAME%" ^
  --icon "%ICON%" ^
  "%MAIN%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto :fail

REM Verificar que la carpeta de salida exista
if not exist "%OUT_DIR%\" (
  echo ERROR: No se encontró la carpeta "%OUT_DIR%".
  >> "%LOG_FILE%" echo ERROR: No se encontró la carpeta "%OUT_DIR%".
  goto :fail
)

REM ==================== CREACIÓN DEL ZIP ====================
echo [3/5] Empaquetando en ZIP...
>> "%LOG_FILE%" echo [3/5] Empaquetando en ZIP...

if exist "%ZIP_PATH%" del /f /q "%ZIP_PATH%"

REM Intento A: Usar API .NET para comprimir
echo - Intento A: .NET ZipFile
>> "%LOG_FILE%" echo - Intento A: .NET ZipFile
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$src = '%OUT_DIR%'; $dst = '%ZIP_PATH%';" ^
  "Add-Type -AssemblyName 'System.IO.Compression.FileSystem';" ^
  "try { [IO.Compression.ZipFile]::CreateFromDirectory($src, $dst, [IO.Compression.CompressionLevel]::Optimal, $false); exit 0 } catch { Write-Host $_; exit 1 }" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 goto :verify_zip

REM Intento B: Usar tar (Windows 10+)
echo - Intento B: tar
>> "%LOG_FILE%" echo - Intento B: tar
tar -a -c -f "%ZIP_PATH%" -C "dist" "%APP_NAME%" >> "%LOG_FILE%" 2>&1
if not errorlevel 1 goto :verify_zip

REM Intento C: Usar Compress-Archive como último recurso
echo - Intento C: Compress-Archive
>> "%LOG_FILE%" echo - Intento C: Compress-Archive
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$src = '%OUT_DIR%'; $dst = '%ZIP_PATH%';" ^
  "if (Test-Path -LiteralPath $dst) { Remove-Item -LiteralPath $dst -Force }" ^
  "try { Compress-Archive -LiteralPath $src -DestinationPath $dst -CompressionLevel Optimal -Force; exit 0 } catch { Write-Host $_; exit 1 }" >> "%LOG_FILE%" 2>&1
if errorlevel 1 goto :fail

REM ==================== VERIFICACIÓN DEL ZIP ====================
:verify_zip
echo [4/5] Verificando ZIP generado...
>> "%LOG_FILE%" echo [4/5] Verificando ZIP generado...
for %%A in ("%ZIP_PATH%") do set "ZIP_SIZE=%%~zA"
if not defined ZIP_SIZE goto :fail
if %ZIP_SIZE% LSS 1024 (
  echo ERROR: ZIP inválido (tamaño %ZIP_SIZE% bytes).
  >> "%LOG_FILE%" echo ERROR: ZIP inválido (tamaño %ZIP_SIZE% bytes).
  goto :fail
)

REM ==================== ÉXITO ====================
echo [5/5] Proceso completado con éxito.
>> "%LOG_FILE%" echo [5/5] Proceso completado con éxito.
echo ZIP creado: %ZIP_PATH% (tamaño: %ZIP_SIZE% bytes)
>> "%LOG_FILE%" echo ZIP creado: %ZIP_PATH% (tamaño: %ZIP_SIZE% bytes)
>> "%LOG_FILE%" echo ===== FIN DEL PROCESO [%DATE% %TIME%] =====
goto :end

REM ==================== ERROR ====================
:fail
echo ==========================================
echo ❌ ERROR en el proceso. Revisa "%LOG_FILE%" para más detalles.
echo ==========================================
>> "%LOG_FILE%" echo ❌ ERROR en el proceso. Revisa este log para más detalles.
pause
exit /b 1

:end
endlocal
