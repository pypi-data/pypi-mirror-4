import codecs
from setuptools import setup


classifiers = '''\
Framework :: Django
Environment :: Web Environment
Intended Audience :: Developers
Topic :: Internet :: WWW/HTTP
License :: OSI Approved :: Apache Software License
Development Status :: 4 - Beta
Natural Language :: English
Programming Language :: Python :: 2.6
Programming Language :: Python :: 2.7
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: Unix
Programming Language :: Python
Programming Language :: Python :: Implementation :: CPython
'''

description = 'Easy to use active url highlighting for django'

packages = ['django_activeurl', 'django_activeurl.templatetags', ]


def long_description():
    with codecs.open('README.rst', encoding='utf8') as f:
        rst = f.read()
    return rst

setup(
    name='django-activeurl',
    version='0.0.3',
    packages=packages,
    description=description,
    long_description=long_description(),
    author='hellysmile',
    author_email='hellysmile@gmail.com',
    url='https://github.com/hellysmile/django-activeurl/',
    zip_safe=False,
    install_requires=[
        'django >= 1.3, <1.5',
        'lxml >= 2.3.5',
        'django-classy-tags >= 0.4',
    ],
    license='http://www.apache.org/licenses/LICENSE-2.0',
    classifiers=filter(None, classifiers.split('\n')),
    keywords=[
        "django", "url", "link", "active", "css", "templatetag",
    ],
    setup_requires=['nose>=1.2.1']
)
