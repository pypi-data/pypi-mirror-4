from os.path import join, dirname

from setuptools import setup, find_packages

here = dirname(__file__)

long_description = (open(join(here, "README.rst")).read() + "\n\n" +
                    open(join(here, "CHANGES.rst")).read() + "\n\n" +
                    open(join(here, "TODO.rst")).read())

def get_version():
    fh = open(join(here, "jstemplate", "__init__.py"))
    try:
        for line in fh.readlines():
            if line.startswith("__version__ ="):
                return line.split("=")[1].strip().strip('"')
    finally:
        fh.close()

setup(
    name="django-jstemplate",
    version=get_version(),
    description="A Django template tag for embedding Mustache.js -- or other JavaScript templates -- templates safely.",
    long_description=long_description,
    author="Mjumbe Wawatu Ukweli",
    author_email="mjumbewu@gmail.com",
    url="https://github.com/mjumbewu/django-jstemplate/",
    packages=find_packages(),
    package_data={'jstemplate': ['static/libs/*.js']},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django",
    ],
    zip_safe=False,
    tests_require=["Django>=1.2", "mock"],
    test_suite="runtests.runtests"
)
