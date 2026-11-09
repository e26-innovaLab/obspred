# Guía de Instalación y Configuración de Python (`backend`)

> **Propósito:** Esta guía detalla **qué versión de Python** requiere el backend de `obspred`, los motivos técnicos de esta elección, y el procedimiento paso a paso para **instalarlo y configurarlo correctamente** en Windows, macOS y Linux/WSL, previniendo errores habituales de PATH, permisos y dependencias nativas.

---

## 1. ¿Qué versión de Python instalar?

### Requerimiento Oficial
El backend del Observatorio Predictivo requiere:

$$\mathbf{Python \ge 3.11 \quad (64\text{-bit})}$$

| Entorno / Caso | Versión Recomendada | Estado de Soporte |
|---|---|---|
| **Desarrollo Local y Staging (Recomendada)** | **Python 3.11.x** o **3.12.x** | ✅ **Óptimo y 100% probado.** Máxima estabilidad con los paquetes precompilados (*wheels* binarios) de `asyncpg`, `greenlet` y `pydantic-core`. |
| **Versiones Más Recientes** | Python 3.13.x / 3.14.x | ⚠️ **Funcional**, pero algunas librerías compiladas en C/Rust pueden requerir herramientas de compilación locales si aún no disponen de *wheels* oficiales para dicha versión. |
| **Versiones Anteriores** | Python $\le$ 3.10 | ❌ **No soportado.** Incompatible con las directivas de tipo y configuración de `pyproject.toml` (`requires-python = ">=3.11"`). |

### Arquitectura Obligatoria
- **64-bit (`x86_64` / `AMD64` o `ARM64` / `Apple Silicon`):** **No instales la versión de 32-bit**. Los controladores asíncronos de base de datos (`asyncpg`) y extensiones numéricas no tienen soporte garantizado en 32-bit.

### ¿Por qué Python 3.11 o superior?
1. **Rendimiento Mejorado:** Python 3.11 incorporó el proyecto *Faster CPython*, con mejoras de velocidad de entre el 10% y el 60% respecto a versiones previas.
2. **Tipado Estricto Moderno:** Soporte nativo para `typing.Self`, `typing.dataclass_transform` y mejoras en genéricos utilizados extensivamente en nuestra Clean Architecture.
3. **Pydantic V2 & FastAPI:** Máximo rendimiento del motor Rust subyacente (`pydantic-core`) para validación y serialización de DTOs y schemas.
4. **Soporte Asíncrono Robusto:** Gestión avanzada de excepciones en tareas asíncronas (`ExceptionGroup`, `TaskGroup`) y compatibilidad total con SQLAlchemy 2.0 y AnyIO.

---

## 2. Instalación Paso a Paso según tu Sistema Operativo

---

### A. Windows (10 / 11)

Windows es el sistema operativo donde con mayor frecuencia ocurren omisiones de PATH o conflictos con la tienda de aplicaciones. Sigue una de estas alternativas:

#### Opción 1: Instalador Oficial (.exe) — *Recomendada para la mayoría*

1. **Descargar el instalador:**
   - Ve a la página oficial de Python: [python.org/downloads/windows](https://www.python.org/downloads/windows/).
   - Descarga el instalador **Windows installer (64-bit)** de **Python 3.11.x** o **Python 3.12.x**.

2. **Ejecutar el instalador (¡Paso crítico!):**
   - Abre el archivo descargado (`python-3.11.x-amd64.exe` o `python-3.12.x-amd64.exe`).
   - ⚠️ **MUY IMPORTANTE:** En la primera pantalla, en la parte inferior, marca la casilla:
     - **☑ Add python.exe to PATH** *(Agregar python.exe a las variables de entorno)*.
     - **☑ Use admin privileges when installing py.exe**.
   - Haz clic en **Install Now** (o *Customize installation* si deseas cambiar la ruta).

3. **Deshabilitar el límite de longitud de rutas (Recomendado):**
   - En la última pantalla (*Setup was successful*), haz clic en la opción:
     - **Disable path length limit** *(Deshabilitar límite de 260 caracteres de MAX_PATH)*.
   - Cierra el instalador haciendo clic en **Close**.

4. **Desactivar los alias de Microsoft Store (Evita que Windows abra la tienda al escribir `python`):**
   - Abre el menú Inicio de Windows y busca: **Alias de ejecución de aplicaciones** (*Manage app execution aliases*).
   - Busca los elementos llamados **Instalador de la aplicación** correspondientes a `python.exe` y `python3.exe` y **desactívalos (OFF)**.

5. **Verificar la instalación:**
   - Abre una **nueva** ventana de PowerShell o Terminal de Windows y ejecuta:
     ```powershell
     python --version
     # o bien usando el launcher universal de Windows:
     py --version
     pip --version
     ```
   - Debe responder: `Python 3.11.x` (o `3.12.x`) y la versión de pip correspondiente.

---

#### Opción 2: Instalación rápida con `winget` (Windows Package Manager)

Si utilizas la terminal de Windows:

```powershell
# Para instalar Python 3.11 de 64 bits:
winget install Python.Python.3.11 --architecture x64

# O para Python 3.12:
winget install Python.Python.3.12 --architecture x64
```

> 💡 **Nota:** Cierra y vuelve a abrir tu terminal luego de completar la instalación con `winget` para que se refresquen las variables de entorno del sistema.

---

### B. macOS (Apple Silicon M1/M2/M3/M4 o Intel)

#### Opción 1: Vía Homebrew (*Recomendada*)

1. Si no tienes Homebrew instalado, instálalo desde [brew.sh](https://brew.sh):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. Instala Python 3.11 o 3.12:
   ```bash
   brew install python@3.11
   ```

3. Vincula la versión y agrega su ruta a tu shell (`~/.zshrc`):
   ```bash
   brew link --overwrite python@3.11
   echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   ```

4. Verifica:
   ```bash
   python3 --version
   pip3 --version
   ```

#### Opción 2: Instalador oficial Universal (.pkg)
- Descarga el instalador **macOS 64-bit universal2 installer** desde [python.org/downloads/macos](https://www.python.org/downloads/macos/).
- Ejecuta el `.pkg` y sigue las instrucciones del asistente.

---

### C. Linux (Ubuntu / Debian / WSL2)

Las distribuciones de Linux suelen incluir Python, pero en algunos casos requieren paquetes adicionales para entornos virtuales y cabeceras de compilación C:

#### En Ubuntu 22.04 / 24.04 o Debian 12:

1. **Actualizar el índice de paquetes e instalar paquetes base:**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv python3-dev build-essential libpq-dev
   ```

2. **(Opcional) Si tu versión de Ubuntu trae una versión previa y deseas Python 3.11/3.12 específico:**
   ```bash
   sudo apt install -y software-properties-common
   sudo add-apt-repository ppa:deadsnakes/ppa -y
   sudo apt update
   sudo apt install -y python3.11 python3.11-venv python3.11-dev
   ```

3. **Verificar la versión instalada:**
   ```bash
   python3 --version
   # o:
   python3.11 --version
   ```

---

## 3. Preparación del Entorno Virtual del Proyecto (`obspred`)

Una vez instalado Python con su versión correspondiente, sigue estos pasos para configurar el backend:

### Paso 1: Clonar e ingresar a la carpeta `backend`
```bash
git clone <URL_DEL_REPOSITORIO>
cd obspred/backend
```

### Paso 2: Crear el Entorno Virtual (`.venv`)

El entorno virtual aísla las librerías del backend para evitar conflictos con otras aplicaciones del sistema:

- **En Windows:**
  ```powershell
  # Usando el launcher py (recomendado si tienes múltiples versiones):
  py -3.11 -m venv .venv

  # O directamente con python:
  python -m venv .venv
  ```

- **En Linux / macOS:**
  ```bash
  python3 -m venv .venv
  # o si instalaste python3.11 explícitamente:
  python3.11 -m venv .venv
  ```

### Paso 3: Activar el Entorno Virtual

- **En Windows (PowerShell):**
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(Ver sección de solución de problemas si recibes un error de `ExecutionPolicy`).*

- **En Windows (Símbolo del sistema / CMD):**
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **En Linux / macOS:**
  ```bash
  source .venv/bin/activate
  ```

> 💡 **Confirmación:** Verás el prefijo `(.venv)` a la izquierda del prompt de tu terminal.

### Paso 4: Actualizar las herramientas de empaquetado
Con el entorno virtual activo, actualiza siempre `pip`, `setuptools` y `wheel`:
```bash
python -m pip install --upgrade pip setuptools wheel
```

### Paso 5: Instalar las dependencias del backend
```bash
# Instalar dependencias requeridas para ejecutar la API y los tests:
pip install -r requirements.txt
```

*(Opcional para desarrollo extendido con herramientas editables):*
```bash
pip install -e ".[dev]"
```

### Paso 6: Configurar Variables de Entorno y Migraciones
```bash
# Copiar plantilla de variables:
cp .env.example .env

# Ejecutar las migraciones iniciales de base de datos (con SQLite o Docker PostgreSQL corriendo):
alembic upgrade head
```

### Paso 7: Comprobar el funcionamiento
1. **Ejecutar las pruebas unitarias e integración:**
   ```bash
   pytest -v
   ```
2. **Iniciar el servidor de desarrollo:**
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
3. **Acceder a la documentación OpenAPI:** Abre en tu navegador [`http://localhost:8000/docs`](http://localhost:8000/docs).

---

## 4. Preguntas Frecuentes y Solución de Problemas (Troubleshooting)

### 🔴 Error 1: `'python'` o `'pip'` no se reconoce como un comando interno o externo (Windows)
- **Causa:** No se marcó la casilla *"Add python.exe to PATH"* durante la instalación.
- **Solución:**
  1. Vuelve a ejecutar el instalador de Python descargado.
  2. Selecciona la opción **Modify** y asegúrate de tildar la opción de agregar al PATH.
  3. Alternativa manual: Agrega `C:\Users\<TuUsuario>\AppData\Local\Programs\Python\Python311\` y su subcarpeta `Scripts\` a la variable de entorno `Path` de tu usuario.
  4. Cierra y vuelve a abrir tu terminal.

---

### 🔴 Error 2: `no se puede cargar el archivo Activate.ps1 porque la ejecución de scripts está deshabilitada en este sistema` (PowerShell)
- **Causa:** Política de seguridad restrictiva por defecto de Windows PowerShell (`Restricted`).
- **Solución:**
  Ejecuta el siguiente comando en PowerShell para autorizar scripts locales en tu sesión actual o usuario:
  ```powershell
  # Opción A (Para la sesión actual de la terminal):
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

  # Opción B (Permanente para tu usuario sin afectar a otros):
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```
  Luego vuelve a ejecutar `.venv\Scripts\Activate.ps1`.

---

### 🔴 Error 3: Windows abre la tienda "Microsoft Store" al escribir `python`
- **Causa:** Los ejecutables ficticios (*App Execution Aliases*) de Windows toman precedencia sobre tu instalación real.
- **Solución:**
  1. Ve a **Configuración de Windows** $\rightarrow$ **Aplicaciones** $\rightarrow$ **Configuración avanzada de aplicaciones** $\rightarrow$ **Alias de ejecución de aplicaciones**.
  2. Desactiva los selectores correspondientes a:
     - `python.exe` (Instalador de la aplicación)
     - `python3.exe` (Instalador de la aplicación)

---

### 🔴 Error 4: Error en Linux: `The virtual environment was not created successfully because ensurepip is not available`
- **Causa:** En distribuciones basadas en Debian/Ubuntu, el módulo `venv` estándar está separado del paquete base.
- **Solución:**
  Instala el paquete `venv` para tu versión instalada:
  ```bash
  sudo apt install -y python3-venv
  # o si estás en python 3.11:
  sudo apt install -y python3.11-venv
  ```

---

### 🔴 Error 5: Error al instalar `asyncpg` o `greenlet` (`Building wheel for ... failed` o falta de Microsoft Visual C++)
- **Causa:** Se está utilizando una versión de Python muy nueva (ej. 3.14 alpha/beta) para la cual aún no se han publicado paquetes precompilados binarios (*wheels*), o se está ejecutando un Python de 32 bits.
- **Solución:**
  1. Asegúrate de instalar **Python 3.11.x o 3.12.x de 64-bit**.
  2. Actualiza las herramientas de construcción:
     ```bash
     python -m pip install --upgrade pip setuptools wheel
     ```
  3. En Windows, si requieres compilar extensiones locales, puedes instalar los [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) seleccionando *"Desarrollo para el escritorio con C++"*.

---

## 5. Resumen de Comandos Esenciales

| Tarea | Windows (PowerShell) | Linux / macOS (Bash / Zsh) |
|---|---|---|
| **Verificar versión de Python** | `py --version` o `python --version` | `python3 --version` |
| **Crear entorno virtual** | `py -3.11 -m venv .venv` | `python3 -m venv .venv` |
| **Activar entorno virtual** | `.venv\Scripts\Activate.ps1` | `source .venv/bin/activate` |
| **Desactivar entorno virtual** | `deactivate` | `deactivate` |
| **Instalar librerías** | `pip install -r requirements.txt` | `pip install -r requirements.txt` |
| **Correr suite de pruebas** | `pytest -v` | `pytest -v` |
| **Levantar servidor local** | `uvicorn app.main:app --reload` | `uvicorn app.main:app --reload` |

---

## 6. Documentos Relacionados
- [Arquitectura y Capas del Backend](arquitectura-y-capas.md)
- [Guía de Base de Datos y Migraciones Alembic](guia-base-datos-y-migraciones.md)
- [Guía de Testing y Calidad](guia-de-testing-y-calidad.md)
- [Guía de Despliegue y Configuración de Entornos](despliegue-y-entornos.md)
- [README Principal del Backend](../README.md)
