import os
import tempfile

import nox

# Separating Black away from the rest of the sessions
nox.options.sessions = "lint", "safety", "tests"
code_locations = "scigateway_auth", "test", "noxfile.py"


def install_with_constraints(session, *args, **kwargs):
    # Auto file deletion is turned off to prevent a PermissionError experienced on
    # Windows
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install(f"--constraint={requirements.name}", *args, **kwargs)

        try:
            # Due to delete=False, the file must be deleted manually
            requirements.close()
            os.unlink(requirements.name)
        except IOError:
            session.log("Error: The temporary requirements file could not be closed")


@nox.session(reuse_venv=True)
def black(session):
    args = session.posargs or code_locations

    install_with_constraints(session, "black")
    session.run("black", *args, external=True)


@nox.session(reuse_venv=True)
def lint(session):
    args = session.posargs or code_locations
    install_with_constraints(
        session,
        "flake8",
        "flake8-bandit",
        "flake8-black",
        "flake8-broken-line",
        "flake8-bugbear",
        "flake8-builtins",
        "flake8-commas",
        "flake8-comprehensions",
        "flake8-import-order",
        "flake8-logging-format",
        "pep8-naming",
    )
    session.run("flake8", *args)


@nox.session(reuse_venv=True)
def safety(session):
    install_with_constraints(session, "safety")
    with tempfile.NamedTemporaryFile(delete=False) as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        # Ignore 51457 as the vulnerability has not yet being fixed
        # Ignore 52322 and 52518 as the latest version of Gitpython does not
        # support python 3.6 which is still used in production
        # Ignore 53325, 53326, 54456, and 55261 as the fixed versions do not support
        # python 3.6
        session.run(
            "safety",
            "check",
            f"--file={requirements.name}",
            "--full-report",
            "--ignore",
            "51457",
            "--ignore",
            "52322",
            "--ignore",
            "52518",
            "--ignore",
            "53325",
            "--ignore",
            "53326",
            "--ignore",
            "54456",
            "--ignore",
            "55261",
        )

        try:
            # Due to delete=False, the file must be deleted manually
            requirements.close()
            os.unlink(requirements.name)
        except IOError:
            session.log("Error: The temporary requirements file could not be closed")


@nox.session(python=["3.6", "3.7", "3.8", "3.9"], reuse_venv=True)
def tests(session):
    args = session.posargs
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)
