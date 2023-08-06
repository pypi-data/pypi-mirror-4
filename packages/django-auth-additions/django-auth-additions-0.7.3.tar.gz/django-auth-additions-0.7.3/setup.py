from distutils.core import setup
import auth_additions

setup(
    name = "django-auth-additions",
    version = auth_additions.__version__,
    description = "Additions (monkey-patches) to auth models.",
    long_description = open("README.rst").read(),
    url = "http://bitbucket.org/schinckel/django-auth-additions",
    author = "Matthew Schinckel",
    author_email = "matt@schinckel.net",
    packages = [
        "auth_additions",
        "auth_additions.management",
        "auth_additions.management.commands",
        "auth_additions.migrations"
    ],
    package_data = {
        '': ['templates/admin/auth/*.html', 'VERSION']
    },
    install_requires = [
        "django-admin-additions>=1.0.0",
    ],
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Framework :: Django',
    ],
)
