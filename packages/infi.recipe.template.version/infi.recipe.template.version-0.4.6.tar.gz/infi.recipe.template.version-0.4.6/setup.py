
SETUP_INFO = dict(
    name = 'infi.recipe.template.version',
    version = '0.4.6',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'http://www.infinidat.com',
    license = 'PSF',
    description = """'an extension to collective.recipe.template'""",
    long_description = """None""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Python Software Foundation License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = ['distribute', 'zc.buildout', 'collective.recipe.template', 'git-py', 'infi.execute'],
    namespace_packages = ['infi', 'infi.recipe', 'infi.recipe.template'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = """
    [zc.buildout]
    default = infi.recipe.template.version.recipe:Recipe
    """
    )

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

