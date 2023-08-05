from setuptools import setup

setup(
    name='thebot-translate',
    version='0.1.0',
    description='Uses translate.yandex.ru, to translate the texts.',
    keywords='thebot language plugin',
    license = 'New BSD License',
    author="Alexander Artemenko",
    author_email='svetlyak.40wt@gmail.com',
    url='http://github.com/svetlyak40wt/thebot-translate/',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
    ],
    py_modules=['thebot_translate'],
    install_requires=[
        'thebot>=0.2.0',
        'requests',
        'anyjson',
    ],
)
