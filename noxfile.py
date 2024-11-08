import os
import tempfile

import nox

# Separating Black away from the rest of the sessions
nox.options.sessions = "lint", "safety", "tests"
code_locations = "scigateway_auth", "test", "noxfile.py"


@nox.session(reuse_venv=True)
def black(session):
    args = session.posargs or code_locations
    session.run("poetry", "install", "--only=dev", external=True)
    session.run("black", *args, external=True)


@nox.session(reuse_venv=True)
def lint(session):
    args = session.posargs or code_locations
    session.run("poetry", "install", "--only=dev", external=True)
    session.run("flake8", *args)


@nox.session(reuse_venv=True)
def safety(session):
    session.install("safety")
    # Ignore 70612, 72731 and 70624 as they have not yet been fixed
    session.run(
        "safety",
        "check",
        "--file=poetry.lock",
        "--full-report",
        "--ignore",
        "70612",
        "--ignore",
        "72731",
        "--ignore",
        "70624",
    )


@nox.session(python=["3.11"], reuse_venv=True)
def tests(session):
    args = session.posargs
    session.run("poetry", "install", "--with=dev", external=True)
    session.run("pytest", "--config-file=test/pytest.ini", *args)
