import nox
from nox_poetry import Session

nox.options.sessions = "lint"
locations = ["src"]


@nox.session(python=["3.11.5"])
def lint(session: Session) -> None:
    """Lint using flake8."""
    args = session.posargs or locations
    session.install(
        "flake8",
        "flake8-black",
        "flake8-isort",
        "flake8-import-order",
        "flake8-docstrings",
    )
    session.run("flake8", *args)


@nox.session(python="3.11.5")
def black(session: Session) -> None:
    """Run black code formatter."""
    args = session.posargs or locations
    session.install("black", "isort")
    session.run("isort", *args)
    session.run("black", *args)

