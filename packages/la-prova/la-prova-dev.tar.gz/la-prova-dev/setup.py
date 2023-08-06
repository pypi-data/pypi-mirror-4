from setuptools import setup

__version__ = 'dev'

description = '''autorun stuff based on changes'''

setup(
    name='la-prova',
    version=__version__,
    description=description,
    author='Bulkan Evcimen',
    author_email='bulkan@gmail.com',
    url='https://github.com/bulkan/la-prova',
    py_modules=['prova'],
    install_requires=[
        'pyinotify'
    ],
    scripts=[
        'prova.py'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
    ]
)
