from distutils.core import setup

# Upload to PyPi with this command :
# > python setup.py build sdist upload

setup(
    name = 'django_dynproxy',
    packages = ['dynproxy'],
    version = '0.1.5',
    author = 'Thomas Petillon',
    author_email = 'petillon@topic.fr',
    url = "https://github.com/tomjerry/django_dynproxy",
    description = 'Dynamic proxy models for Django',
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities",
    ]
)
