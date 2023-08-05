from setuptools import setup


setup(
    name='tattler',
    author='Joe Friedl',
    author_email='joe@joefriedl.net',
    version='0.1',
    description='A nose plugin that tattles on functions.',
    keywords='nose plugin test testing mock',
    url='https://github.com/grampajoe/tattler',
    license='MIT',
    py_modules=['tattler'],
    install_requires=[
        'mock',
    ],
    entry_points = {
        'nose.plugins.0.10': [
            'tattler = tattler:Tattler',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Testing',
    ],
)
