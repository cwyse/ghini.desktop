import toml
from bauble import version

def create_pyproject():
    pyproject_data = {
        "build-system": {
            "requires": ["setuptools>=40.8.0", "wheel"],
            "build-backend": "setuptools.build_meta",
        },
        "project_urls": {
            "homepage": "http://ghini.github.io/",
            "repository": "https://github.com/ghini/ghini.desktop",
            "documentation": "http://ghini.github.io/docs"
        },
        "project": {
            "name": "ghini-desktop",
            "version": version,
            "description": "Ghini: a biodiversity collection manager",
            "readme": {
                "file": "README.rst",  # Use README.rst instead of README.md
                "content-type": "text/x-rst",  # Specify reStructuredText format
            },
            "keywords": [ "database", "biodiversity", "botany", "collection", "herbarium", "arboretum"],

            "license": {"text": "GPLv2+"},
            "authors": [{"name": "Mario Frasca", "email": "mario@anche.no"},
                        {"name": "Chris Wyse", "email": "chris.wyse@wysechoice.net"}],
            "platforms": ["Linux", "Windows", "macOS"],
            "dependencies": [
                # Main requirements from requirements.txt and constraints.txt
                #                                        Latest as of 11/19/24
                "certifi==2024.8.30",                    # 2024.8.30
                "chardet==4.0.0",                        # 5.2.0
                "ecdsa==0.19.0",                         # 0.19.0
                "fibra==0.0.20",                         # 0.0.20
                "gdata-python3==3.0.1",                  # 3.0.1
                "idna==2.10",                            # 3.4
                "Jinja2==2.10",                          # 3.1.2
                "lxml==5.3.0",                           # 5.3.0
                "Mako==1.0.7",                           # 1.2.4
                "MarkupSafe==3.0.2",                     # 3.1.1
                "Pillow==2.3.0",                         # 10.0.1
                "psycopg2==2.9.10",                      # 2.9.10
                "pycairo==1.27.0",                       # 1.27.0
                "PyGObject==3.50.0",                     # 3.50.0
                "pyparsing==2.2.0",                      # 3.1.1
                "PyQRCode==1.2.1",                       # 1.2.1
                "python-dateutil==2.7.3",                # 2.8.2
                "raven==6.7.0",                          # 6.10.0
                "requests==2.25.1",                      # 2.31.0
                "six==1.16.0",                           # 1.16.0
                "SQLAlchemy==1.3.0",                     # 2.1.0
                "tlslite-ng==0.7.6",                     # 0.7.6
                "urllib3==1.26.20",                      # 2.1.0
            ],
            "optional-dependencies": {
                "dev": [
                    # Development dependencies from dev-requirements.txt and dev-constraints.txt
                    "pytest==6.2.5",                     # 7.4.0
                    "pytest-cov==2.12.1",                # 6.0.0
                    "tox==3.24.4",                       # 4.8.0
                    # Add additional dev dependencies here
                ],
                "docs": [
                    # Documentation dependencies from doc-requirements.txt and doc-constraints.txt
                    "Sphinx==4.2.0",                     # 7.1.2
                    "sphinx-rtd-theme==1.0.0",           # 1.2.0
                    "sphinx-autodoc-typehints==1.12.0",  # 1.25.0
                    # Add additional doc dependencies here
                ],
            },
        },
    }

    # Write to pyproject.toml
    with open("/app/pyproject.toml", "w") as file:
        toml.dump(pyproject_data, file)
    print("pyproject.toml has been generated successfully.")

if __name__ == "__main__":
    create_pyproject()
