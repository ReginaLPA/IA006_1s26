import os
import sys
import json
import socket
import platform
import getpass
import datetime
import importlib.util
import importlib.metadata
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


DEFAULT_PACKAGES = {
    "jupyterlab_lsp": "jupyterlab-lsp",
    "jupyter_lsp": "jupyter-lsp",
    "pylsp": "python-lsp-server",
    "jedi": "jedi",
    "numpy": "numpy",
    "pandas": "pandas",
    "matplotlib": "matplotlib",
    "requests": "requests",
    "IPython": "ipython",
    "ipykernel": "ipykernel",
}


def check_package(module_name: str, package_name: str | None = None) -> dict:
    package_name = package_name or module_name
    found = importlib.util.find_spec(module_name) is not None

    version = None
    if found:
        try:
            version = importlib.metadata.version(package_name)
        except importlib.metadata.PackageNotFoundError:
            version = "versão não identificada"

    return {
        "package": package_name,
        "module": module_name,
        "found": found,
        "version": version,
    }


def check_directories(paths: list[str | Path]) -> list[dict]:
    results = []
    for raw_path in paths:
        path = Path(raw_path).expanduser()
        exists = path.exists()
        results.append({
            "path": str(path),
            "exists": exists,
            "readable": os.access(path, os.R_OK) if exists else False,
            "writable": os.access(path, os.W_OK) if exists else False,
        })
    return results


def check_proxy() -> dict:
    keys = ["http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "no_proxy", "NO_PROXY"]
    return {k: os.environ.get(k) for k in keys if os.environ.get(k)}


def check_url(url: str = "https://pypi.org/simple/", timeout: int = 5) -> dict:
    try:
        request = Request(url, headers={"User-Agent": "jupyter-health-check"})
        with urlopen(request, timeout=timeout) as response:
            return {"url": url, "ok": True, "status": response.status, "error": None}
    except HTTPError as e:
        return {"url": url, "ok": False, "status": e.code, "error": str(e)}
    except URLError as e:
        return {"url": url, "ok": False, "status": None, "error": str(e)}
    except Exception as e:
        return {"url": url, "ok": False, "status": None, "error": repr(e)}


def check_ollama(base_urls: list[str] | None = None, timeout: int = 3) -> dict:
    if base_urls is None:
        base_urls = [
            "http://localhost:11434",
            "http://127.0.0.1:11434",
            "http://ollama:11434",
            "http://simserv-ollama-ui:11434",
        ]

    for base in base_urls:
        url = base.rstrip("/") + "/api/tags"
        result = check_url(url, timeout=timeout)
        if result["ok"]:
            try:
                request = Request(url, headers={"User-Agent": "jupyter-health-check"})
                with urlopen(request, timeout=timeout) as response:
                    data = json.loads(response.read().decode("utf-8"))
                models = [m.get("name", "") for m in data.get("models", [])]
                return {"available": True, "base_url": base, "models": models, "error": None}
            except Exception as e:
                return {"available": True, "base_url": base, "models": [], "error": repr(e)}

    return {"available": False, "base_url": None, "models": [], "error": "Ollama não respondeu nas URLs testadas"}


def collect_health_check(full: bool = False) -> dict:
    home = Path.home()

    data = {
        "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "user": getpass.getuser(),
        "python_version": sys.version,
        "python_executable": sys.executable,
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "cwd": str(Path.cwd()),
        "home": str(home),
        "packages": [check_package(m, p) for m, p in DEFAULT_PACKAGES.items()],
    }

    if full:
        data["directories"] = check_directories([
            Path.cwd(),
            home,
            home / "ambiente_laboratorio",
            home / "laboratorio",
            home / "shared",
            home / "exercicios_e_recursos",
            Path("/sobre_ambientes_simserv"),
        ])
        data["proxy"] = check_proxy()
        data["network"] = {
            "pypi": check_url("https://pypi.org/simple/"),
            "google": check_url("https://www.google.com/"),
        }
        data["ollama"] = check_ollama()

    return data


def format_text_report(data: dict) -> str:
    lines = []
    lines.append("HEALTH CHECK - PYTHON/JUPYTER")
    lines.append("=" * 40)
    lines.append(f"Data/hora: {data.get('generated_at')}")
    lines.append(f"Usuário: {data.get('user')}")
    lines.append(f"Host: {data.get('hostname')}")
    lines.append(f"Python: {data.get('python_version')}")
    lines.append(f"Executável Python: {data.get('python_executable')}")
    lines.append(f"Sistema: {data.get('platform')}")
    lines.append(f"Pasta atual: {data.get('cwd')}")
    lines.append(f"HOME: {data.get('home')}")
    lines.append("")

    lines.append("PACOTES")
    lines.append("-" * 40)
    for item in data.get("packages", []):
        status = "OK" if item["found"] else "NÃO ENCONTRADO"
        version = item["version"] or "-"
        lines.append(f"{item['package']:24s} | {item['module']:18s} | {status:15s} | {version}")

    if "directories" in data:
        lines.append("")
        lines.append("PASTAS E PERMISSÕES")
        lines.append("-" * 40)
        for d in data["directories"]:
            lines.append(
                f"{d['path']} | existe={d['exists']} | leitura={d['readable']} | escrita={d['writable']}"
            )

    if "proxy" in data:
        lines.append("")
        lines.append("PROXY")
        lines.append("-" * 40)
        if data["proxy"]:
            for k, v in data["proxy"].items():
                lines.append(f"{k}={v}")
        else:
            lines.append("Nenhuma variável de proxy encontrada.")

    if "network" in data:
        lines.append("")
        lines.append("REDE")
        lines.append("-" * 40)
        for name, result in data["network"].items():
            lines.append(f"{name}: ok={result['ok']} status={result['status']} erro={result['error']}")

    if "ollama" in data:
        lines.append("")
        lines.append("IA LOCAL - OLLAMA")
        lines.append("-" * 40)
        lines.append(f"Disponível: {data['ollama']['available']}")
        lines.append(f"URL: {data['ollama']['base_url']}")
        lines.append("Modelos: " + (", ".join(data["ollama"]["models"]) if data["ollama"]["models"] else "nenhum listado"))

    return "\n".join(lines)