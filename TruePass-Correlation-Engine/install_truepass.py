#!/usr/bin/env python3
"""TruePass (SDR) Correlation-Engine — one-file installer.

Cross-platform installer for Windows, macOS, and Linux.

Examples:
    python install_truepass.py
    python install_truepass.py --mode local --dev
    python install_truepass.py --mode local --start
    python install_truepass.py --mode docker --start
    python install_truepass.py --mode docker --start --monitoring

The installer is intentionally non-destructive:
  * It reuses an existing .venv.
  * It never overwrites an existing .env.
  * It never removes Docker volumes or project data.
"""
from __future__ import annotations

import argparse
import os
import platform
import secrets
import shutil
import string
import subprocess
import sys
import sysconfig
from pathlib import Path

APP_NAME = "TruePass (SDR) Correlation-Engine"
PACKAGE_NAME = "truepass-correlation-engine"
MIN_PYTHON = (3, 13)
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000

SCRIPT_DIR = Path(__file__).resolve().parent


class InstallerError(RuntimeError):
    """Raised for a friendly installer failure."""


def banner() -> None:
    print(
        "\n"
        "============================================================\n"
        "  TruePass (SDR) Correlation-Engine\n"
        "  One-File Installer\n"
        "============================================================"
    )


def find_project_root() -> Path:
    """Locate the actual runnable project even inside the repository wrapper."""
    candidates = [
        SCRIPT_DIR,
        SCRIPT_DIR / "TruePass-Correlation-Engine",
    ]

    for candidate in candidates:
        if _is_truepass_project(candidate):
            return candidate.resolve()

    # Fall back to a shallow recursive search so the installer still works if
    # the GitHub archive gains another wrapper directory later.
    matches: list[Path] = []
    for pyproject in SCRIPT_DIR.glob("*/*/pyproject.toml"):
        if _is_truepass_project(pyproject.parent):
            matches.append(pyproject.parent.resolve())
    for pyproject in SCRIPT_DIR.glob("*/pyproject.toml"):
        if _is_truepass_project(pyproject.parent):
            matches.append(pyproject.parent.resolve())

    unique_matches = sorted(set(matches))
    if len(unique_matches) == 1:
        return unique_matches[0]
    if len(unique_matches) > 1:
        rendered = "\n  - ".join(str(path) for path in unique_matches)
        raise InstallerError(
            "Multiple TruePass project folders were found. Keep the installer "
            f"next to the intended project folder.\n  - {rendered}"
        )

    raise InstallerError(
        "Could not locate the TruePass project. Expected pyproject.toml and "
        "src/truepass next to this installer or in TruePass-Correlation-Engine/."
    )


def _is_truepass_project(path: Path) -> bool:
    pyproject = path / "pyproject.toml"
    package_dir = path / "src" / "truepass"
    if not pyproject.is_file() or not package_dir.is_dir():
        return False
    try:
        text = pyproject.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return f'name = "{PACKAGE_NAME}"' in text


def command_text(command: list[str]) -> str:
    """Produce readable command output without requiring shell quoting logic."""
    return " ".join(f'"{part}"' if " " in part else part for part in command)


def run(
    command: list[str],
    *,
    cwd: Path,
    check: bool = True,
    quiet: bool = False,
) -> int:
    if not quiet:
        print(f"\n> {command_text(command)}")

    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
    )
    if check and completed.returncode != 0:
        raise InstallerError(
            f"Command failed with exit code {completed.returncode}: "
            f"{command_text(command)}"
        )
    return completed.returncode


def python_is_supported() -> bool:
    return sys.version_info >= MIN_PYTHON


def check_python() -> None:
    current = platform.python_version()
    required = ".".join(map(str, MIN_PYTHON))
    if not python_is_supported():
        raise InstallerError(
            f"Local installation requires Python {required}+; this installer is "
            f"running on Python {current}. Install Python {required}+ or use "
            "--mode docker."
        )
    print(f"[OK] Python {current} on {platform.system()}")


def docker_compose_available(project_root: Path) -> bool:
    if shutil.which("docker") is None:
        return False
    return (
        run(
            ["docker", "compose", "version"],
            cwd=project_root,
            check=False,
            quiet=True,
        )
        == 0
    )


def check_docker(project_root: Path) -> None:
    if shutil.which("docker") is None:
        raise InstallerError(
            "Docker was not found in PATH. Install Docker Desktop/Engine or use "
            "--mode local with Python 3.13+."
        )
    if not docker_compose_available(project_root):
        raise InstallerError("Docker Compose v2 is required (`docker compose`).")

    # `docker compose version` can succeed while the Docker daemon is stopped.
    if run(["docker", "info"], cwd=project_root, check=False, quiet=True) != 0:
        raise InstallerError(
            "Docker is installed, but the Docker daemon is not reachable. Start "
            "Docker Desktop/Engine and run the installer again."
        )
    print("[OK] Docker and Docker Compose are available")


def choose_mode(requested: str, project_root: Path) -> str:
    if requested != "auto":
        return requested

    if python_is_supported():
        print("[INFO] Auto mode selected local installation (Python 3.13+ detected).")
        return "local"

    if docker_compose_available(project_root):
        print("[INFO] Auto mode selected Docker installation.")
        return "docker"

    required = ".".join(map(str, MIN_PYTHON))
    raise InstallerError(
        f"No supported install path was detected. Install Python {required}+ "
        "or Docker with Compose v2."
    )


def venv_python(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def venv_truepass(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "truepass.exe"
    return venv_dir / "bin" / "truepass"


def install_local(
    project_root: Path,
    *,
    dev: bool,
    start: bool,
    host: str,
    port: int,
    skip_doctor: bool,
) -> None:
    check_python()

    venv_dir = project_root / ".venv"
    python = venv_python(venv_dir)

    if not python.exists():
        print(f"[INFO] Creating virtual environment: {venv_dir}")
        run([sys.executable, "-m", "venv", str(venv_dir)], cwd=project_root)
    else:
        print(f"[OK] Reusing virtual environment: {venv_dir}")

    if not python.exists():
        raise InstallerError(f"Virtual-environment Python was not created: {python}")

    # Arch/Manjaro ship SoapySDR's Python extension with the system package.
    # A normal venv hides that package even when its Python ABI matches.  Add
    # only the system purelib path when it actually contains SoapySDR, rather
    # than enabling every system package wholesale.
    if os.name != "nt":
        system_purelib = Path(sysconfig.get_paths().get("purelib", ""))
        if system_purelib and (system_purelib / "SoapySDR.py").exists():
            probe = subprocess.run(
                [str(python), "-c", "import site; print(site.getsitepackages()[0])"],
                cwd=str(project_root), capture_output=True, text=True, check=False,
            )
            if probe.returncode == 0 and probe.stdout.strip():
                venv_site = Path(probe.stdout.strip())
                pth = venv_site / "truepass-system-soapysdr.pth"
                pth.write_text(str(system_purelib) + "\n", encoding="utf-8")
                print(f"[OK] Exposed system SoapySDR bindings to TruePass: {system_purelib}")

    python_cmd = str(python)
    run([python_cmd, "-m", "pip", "install", "--upgrade", "pip"], cwd=project_root)

    package_spec = ".[dev]" if dev else "."
    dependency_label = "runtime + development" if dev else "runtime"
    print(f"[INFO] Installing TruePass {dependency_label} dependencies")
    run([python_cmd, "-m", "pip", "install", package_spec], cwd=project_root)

    truepass = venv_truepass(venv_dir)
    if not truepass.exists():
        raise InstallerError(f"TruePass CLI was not created: {truepass}")

    truepass_cmd = str(truepass)
    run([truepass_cmd, "--version"], cwd=project_root)

    if not skip_doctor:
        print("\n[INFO] Running TruePass diagnostics.")
        print(
            "[INFO] A local PostgreSQL 17+/pgvector server is not installed by "
            "this script; an unavailable database is therefore a warning here."
        )
        doctor_code = run(
            [truepass_cmd, "doctor"],
            cwd=project_root,
            check=False,
        )
        if doctor_code != 0:
            print(
                "[WARN] TruePass is installed, but diagnostics could not reach "
                "the configured PostgreSQL database. Use Docker mode or configure "
                "PostgreSQL before relying on database-backed features."
            )

    print("\n[SUCCESS] Local installation completed.")
    print(f"Project:   {project_root}")
    if os.name == "nt":
        print(f"Activate:  {venv_dir}\\Scripts\\Activate.ps1")
    else:
        print(f"Activate:  source {venv_dir}/bin/activate")
    print(f"Run:       {truepass_cmd} run --host {host} --port {port}")
    print(f"Dashboard: http://{host}:{port}/dashboard")
    print(f"API docs:  http://{host}:{port}/docs")

    if start:
        print("\n[INFO] Starting TruePass. Press Ctrl+C to stop.")
        run(
            [truepass_cmd, "run", "--host", host, "--port", str(port)],
            cwd=project_root,
        )


def generate_secret(length: int = 40) -> str:
    # URL-safe for use inside the PostgreSQL connection string in Compose.
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(length))


def prepare_docker_env(project_root: Path) -> None:
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"

    if env_file.exists():
        print("[OK] Existing .env preserved")
        return
    if not env_example.is_file():
        raise InstallerError(f"Missing required file: {env_example}")

    content = env_example.read_text(encoding="utf-8")
    placeholder = "POSTGRES_PASSWORD=change-me-before-deployment"
    replacement = f"POSTGRES_PASSWORD={generate_secret()}"

    if placeholder in content:
        content = content.replace(placeholder, replacement, 1)
    elif "POSTGRES_PASSWORD=" not in content:
        content += f"\n{replacement}\n"

    env_file.write_text(content, encoding="utf-8")
    print("[OK] Created .env with a generated PostgreSQL password")


def read_env_value(path: Path, name: str, default: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return default

    prefix = f"{name}="
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(prefix):
            value = stripped[len(prefix) :].strip().strip('"').strip("'")
            return value or default
    return default


def install_docker(
    project_root: Path,
    *,
    start: bool,
    monitoring: bool,
) -> None:
    check_docker(project_root)
    prepare_docker_env(project_root)

    compose = ["docker", "compose"]
    command = compose.copy()
    if monitoring:
        command += ["--profile", "monitoring"]
    command += ["up", "--build"]
    if start:
        command += ["-d"]
    else:
        command += ["--no-start"]

    run(command, cwd=project_root)

    env_file = project_root / ".env"
    truepass_port = read_env_value(env_file, "TRUEPASS_PORT", str(DEFAULT_PORT))
    prometheus_port = read_env_value(env_file, "PROMETHEUS_PORT", "9090")

    if start:
        print("\n[SUCCESS] Docker installation completed and TruePass is running.")
        print(f"Dashboard: http://127.0.0.1:{truepass_port}/dashboard")
        print(f"API docs:  http://127.0.0.1:{truepass_port}/docs")
        if monitoring:
            print(f"Prometheus: http://127.0.0.1:{prometheus_port}")
        print("Stop:       docker compose down")
    else:
        print("\n[SUCCESS] Docker images and containers are prepared but not started.")
        if monitoring:
            print("Start: docker compose --profile monitoring up -d")
        else:
            print("Start: docker compose up -d")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=f"Install {APP_NAME} with one cross-platform script.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=("auto", "local", "docker"),
        default="auto",
        help="Installation mode. Auto prefers local Python 3.13+, then Docker.",
    )
    parser.add_argument(
        "--dev",
        action="store_true",
        help="Local mode: also install development and test dependencies.",
    )
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start TruePass after installation.",
    )
    parser.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help="Local mode: API bind host.",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Local mode: API port.",
    )
    parser.add_argument(
        "--monitoring",
        action="store_true",
        help="Docker mode: enable the Prometheus Compose profile.",
    )
    parser.add_argument(
        "--skip-doctor",
        action="store_true",
        help="Local mode: skip post-install TruePass diagnostics.",
    )
    return parser.parse_args()


def main() -> int:
    banner()
    args = parse_args()

    if not 1 <= args.port <= 65535:
        print("[ERROR] --port must be between 1 and 65535.", file=sys.stderr)
        return 2

    try:
        project_root = find_project_root()
        print(f"[OK] Project located: {project_root}")
        mode = choose_mode(args.mode, project_root)

        if mode == "docker":
            if args.dev:
                print("[WARN] --dev applies only to local mode and will be ignored.")
            if args.host != DEFAULT_HOST or args.port != DEFAULT_PORT:
                print(
                    "[WARN] --host/--port apply only to local mode. For Docker, "
                    "set TRUEPASS_PORT in .env."
                )
            install_docker(
                project_root,
                start=args.start,
                monitoring=args.monitoring,
            )
        else:
            if args.monitoring:
                print("[WARN] --monitoring applies only to Docker mode and will be ignored.")
            install_local(
                project_root,
                dev=args.dev,
                start=args.start,
                host=args.host,
                port=args.port,
                skip_doctor=args.skip_doctor,
            )

    except InstallerError as exc:
        print(f"\n[ERROR] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"\n[ERROR] Operating-system error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[INFO] Installation cancelled.")
        return 130

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
