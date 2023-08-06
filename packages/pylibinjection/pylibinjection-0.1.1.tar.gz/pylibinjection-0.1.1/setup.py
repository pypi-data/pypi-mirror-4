from distutils.core import setup
from distutils.extension import Extension


sourcefiles = ["src/pylibinjection.c", "/opt/libinjection/c/sqlparse.c"]


setup(
    name="pylibinjection",
    packages=["src"],
    version="0.1.1",
    description="Libinjection Python wrapper",
    url="https://github.com/glastopf/pylibinjection",
    author="Angelo Dell'Aera",
    author_email="angelo.dellaera@honeynet.org",
    classifiers=[
        "Programming Language :: Cython",
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: Unix",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Security",
    ],
    ext_modules=[Extension("pylibinjection",
                           sourcefiles,
                           include_dirs=["/opt/libinjection/c"],
                           library_dirs=["/opt/libinjection/c"],
                           )
    ],
)
