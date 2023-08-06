from setuptools import setup
setup(
    name = "django-boreas",
    version = "0.1",
    package_dir = {'': 'src'},
    packages = [
        'djboreas',
        'djboreas.management',
        'djboreas.management.commands',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        'django>=1.5',
        'boreas>=0.1',
    ],

    package_data = {},

    author = "Karol Majta",
    author_email = "karol@karolmajta.com",
    description = "Django management commands for boreas",
    license = "JSON License",
    keywords = "websocket pub sub pubsub boreas django",
    url = "http://django.boreas.readthedocs.org/",
)