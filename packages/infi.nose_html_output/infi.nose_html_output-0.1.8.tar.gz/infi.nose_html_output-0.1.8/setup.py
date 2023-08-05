
SETUP_INFO = dict(
    name = 'infi.nose_html_output',
    version = '0.1.8',
    author = 'Arnon Yaari',
    author_email = 'wiggin15@yahoo.com',

    url = 'https://github.com/Infinidat/infi.nose_html_output',
    license = 'PSF',
    description = """HTML Plugin for Nose""",
    long_description = """HTML Plugin for Nose""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'lxml==2.3', 'nose'],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': ['static/*.css', 'static/*.js']},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        'console_scripts': [],
        'gui_scripts': [],
        'nose.plugins.0.10': ['infi.nose_html_output = infi.nose_html_output:NosePlugin', ],
        },
    )

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

