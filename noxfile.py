# Licensed to Elasticsearch B.V under one or more agreements.
# Elasticsearch B.V licenses this file to you under the Apache 2.0 License.
# See the LICENSE file in the project root for more information

import os
import subprocess
from pathlib import Path
import nox
import elasticsearch


BASE_DIR = Path(__file__).parent
SOURCE_FILES = (
    "setup.py",
    "noxfile.py",
    "eland/",
    "docs/",
    "utils/",
)

# Whenever type-hints are completed on a file it should
# be added here so that this file will continue to be checked
# by mypy. Errors from other files are ignored.
TYPED_FILES = {
    "eland/actions.py",
    "eland/arithmetics.py",
    "eland/common.py",
    "eland/etl.py",
    "eland/filter.py",
    "eland/index.py",
    "eland/query.py",
    "eland/tasks.py",
    "eland/ml/__init__.py",
    "eland/ml/_model_serializer.py",
    "eland/ml/imported_ml_model.py",
    "eland/ml/transformers/__init__.py",
    "eland/ml/transformers/base.py",
    "eland/ml/transformers/sklearn.py",
    "eland/ml/transformers/xgboost.py",
}


@nox.session(reuse_venv=True)
def blacken(session):
    session.install("black")
    session.run("python", "utils/license-headers.py", "fix", *SOURCE_FILES)
    session.run("black", "--target-version=py36", *SOURCE_FILES)
    lint(session)


@nox.session(reuse_venv=True)
def lint(session):
    session.install("black", "flake8", "mypy")
    session.run("python", "utils/license-headers.py", "check", *SOURCE_FILES)
    session.run("black", "--check", "--target-version=py36", *SOURCE_FILES)
    session.run("flake8", "--ignore=E501,W503,E402,E712", *SOURCE_FILES)

    # TODO: When all files are typed we can change this to .run("mypy", "--strict", "eland/")
    session.log("mypy --strict eland/")
    for typed_file in TYPED_FILES:
        if not os.path.isfile(typed_file):
            session.error(f"The file {typed_file!r} couldn't be found")
        popen = subprocess.Popen(
            f"mypy --strict {typed_file}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        popen.wait()
        errors = []
        for line in popen.stdout.read().decode().split("\n"):
            filepath = line.partition(":")[0]
            if filepath in TYPED_FILES:
                errors.append(line)
        if errors:
            session.error("\n" + "\n".join(sorted(set(errors))))


@nox.session(python=["3.6", "3.7", "3.8"])
def test(session):
    session.install("-r", "requirements-dev.txt")
    session.run("python", "-m", "eland.tests.setup_tests")
    session.run("pytest", "--doctest-modules", *(session.posargs or ("eland/",)))

    session.run("python", "-m", "pip", "uninstall", "--yes", "scikit-learn", "xgboost")
    session.run("pytest", "eland/tests/ml/")


@nox.session(python=["3.6", "3.7", "3.8"], name="test-ml-deps")
def test_ml_deps(session):
    def session_uninstall(*deps):
        session.run("python", "-m", "pip", "uninstall", "--yes", *deps)

    session.install("-r", "requirements-dev.txt")
    session.run("python", "-m", "eland.tests.setup_tests")

    session_uninstall("xgboost", "scikit-learn")
    session.run("pytest", *(session.posargs or ("eland/tests/ml/",)))

    session.install(".[scikit-learn]")
    session.run("pytest", *(session.posargs or ("eland/tests/ml/",)))


@nox.session(reuse_venv=True)
def docs(session):
    # Run this so users get an error if they don't have Pandoc installed.
    session.run("pandoc", "--version", external=True)

    session.install("-r", "docs/requirements-docs.txt")
    session.install(".")

    # See if we have an Elasticsearch cluster active
    # to rebuild the Jupyter notebooks with.
    try:
        es = elasticsearch.Elasticsearch("localhost:9200")
        es.info()
        if not es.indices.exists("flights"):
            session.run("python", "-m", "eland.tests.setup_tests")
        es_active = True
    except Exception:
        es_active = False

    # Rebuild all the example notebooks inplace
    if es_active:
        session.install("jupyter-client", "ipykernel")
        for filename in os.listdir(BASE_DIR / "docs/source/examples"):
            if filename.endswith(".ipynb"):
                session.run(
                    "jupyter",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--inplace",
                    "--execute",
                    str(BASE_DIR / "docs/source/examples" / filename),
                )

    session.cd("docs")
    session.run("make", "clean", external=True)
    session.run("make", "html", external=True)
