from pathlib import Path

from truepass import __version__


REQUIRED_DOCS = {
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/INSTALLATION.md",
    "docs/CONFIGURATION.md",
    "docs/SECURITY.md",
    "docs/PRIVACY.md",
    "docs/EVIDENCE_MODEL.md",
    "docs/RF_PIPELINE.md",
    "docs/CORRELATION_ENGINE.md",
    "docs/API.md",
    "docs/DEVELOPMENT.md",
    "docs/TROUBLESHOOTING.md",
    "docs/THREAT_MODEL.md",
    "docs/DEVELOPMENT_STATUS.md",
    "docs/RELEASE_CHECKLIST.md",
    "CHANGELOG.md",
}


def test_final_release_version() -> None:
    assert __version__ == "1.0.0"


def test_required_release_documentation_exists() -> None:
    missing = sorted(path for path in REQUIRED_DOCS if not Path(path).is_file())
    assert not missing, f"missing release documents: {missing}"


def test_deployment_artifacts_exist() -> None:
    for path in ["Dockerfile", "docker-compose.yml", "deploy/prometheus.yml", ".env.example"]:
        assert Path(path).is_file(), path
