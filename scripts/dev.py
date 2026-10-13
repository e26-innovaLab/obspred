"""Script para orquestar la ejecución simultánea de backend y frontend en desarrollo."""

import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"


def get_python_executable() -> str:
    """Detecta el ejecutable de Python del entorno virtual o del sistema."""
    # Buscar entorno virtual en la raíz o en backend
    candidates = [
        ROOT_DIR / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"),
        BACKEND_DIR / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"),
        ROOT_DIR / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"),
        BACKEND_DIR / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python"),
    ]

    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)

    return sys.executable


def main() -> None:
    """Inicia backend (FastAPI/Uvicorn) y frontend (Vite) de forma concurrente."""
    py_exec = get_python_executable()
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"

    print(f"[*] Root dir: {ROOT_DIR}")
    print(f"[*] Python:   {py_exec}")
    print(f"[*] Frontend: {FRONTEND_DIR}")
    print("[*] Levantando Backend (FastAPI :8000) y Frontend (Vite :5173)...")
    print("    Presione Ctrl+C para detener ambos servicios.\n")

    # Comando Backend
    backend_cmd = [
        py_exec,
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        "8000",
    ]

    # Comando Frontend
    frontend_cmd = [npm_cmd, "run", "dev"]

    processes: list[subprocess.Popen] = []

    try:
        p_back = subprocess.Popen(backend_cmd, cwd=str(BACKEND_DIR))
        processes.append(p_back)

        p_front = subprocess.Popen(frontend_cmd, cwd=str(FRONTEND_DIR))
        processes.append(p_front)

        # Esperar a que alguno termine o se envíe señal
        while True:
            for p in processes:
                ret = p.poll()
                if ret is not None:
                    print(f"[-] Proceso {p.pid} finalizó con código {ret}")
                    return
            signal.pause() if hasattr(signal, "pause") else None
            import time
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[*] Deteniendo servicios...")
    finally:
        for p in processes:
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("[*] Servicios finalizados.")


if __name__ == "__main__":
    main()
