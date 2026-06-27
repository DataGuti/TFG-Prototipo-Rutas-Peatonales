@echo off
setlocal

echo ==========================================
echo Preparando el prototipo del TFG
echo ==========================================

if not exist ".venv\Scripts\python.exe" (
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat

echo Instalando dependencias...
python -m pip install --upgrade pip
if errorlevel 1 goto :error

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo Ejecutando el flujo analitico...
jupyter nbconvert --to notebook --execute notebooks\01_pipeline_analitico.ipynb --inplace --ExecutePreprocessor.timeout=-1
if errorlevel 1 goto :error

echo Iniciando la aplicacion...
python -m streamlit run app\app.py
goto :end

:error
echo.
echo La ejecucion se interrumpio debido a un error.
pause
exit /b 1

:end
endlocal
