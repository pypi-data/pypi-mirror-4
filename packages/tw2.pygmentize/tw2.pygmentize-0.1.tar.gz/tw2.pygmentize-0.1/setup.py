from setuptools import setup, find_packages

setup(
    name='tw2.pygmentize',
    version='0.1',
    description='Syntax Highlighting using Pygments within a ToscaWidgets2 widget',
    long_description=open('README.rst').read(),
    author='Moritz Schlarb',
    author_email='moschlar@metalabs.de',
    url='https://github.com/moschlar/tw2.pygmentize',
    install_requires=[
        "tw2.core",
        ## Add other requirements here
        # "Genshi",
        "Pygments >= 1.6",
        ],
    packages=find_packages(exclude=['ez_setup', 'tests']),
    namespace_packages = ['tw2'],
    zip_safe=False,
    include_package_data=True,
    test_suite = 'nose.collector',
    entry_points="""
        [tw2.widgets]
        # Register your widgets so they can be listed in the WidgetBrowser
        widgets = tw2.pygmentize
    """,
    keywords = [
        'toscawidgets.widgets',
    ],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Environment :: Web Environment :: ToscaWidgets',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Widget Sets',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
