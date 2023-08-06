import multiprocessing, logging # Fix atexit bug
from setuptools import setup, find_packages


__version__ = '0.0.0-dev' # False version to help out static analyzers
exec("c=__import__('compiler');a='__version__';l=[];g=lambda:[n.expr.value for"
        " n in l for o in n.nodes if getattr(o,'name',0) and o.name==a].pop();"
        "c.walk(c.parseFile('%s.py'),type('v',(object,),{'visitAssign':lambda "
        "s,n:l.append(n)})());exec(a+'=g()');" % 'urlshots')


def readme():
    try:
        return open('README.rst').read()
    except:
        pass
    return ''


setup(
        name='urlshots-api',
        version=__version__,
        description="UrlShots API Python Client",
        long_description=readme(),
        url='http://bitbucket.org/urlshots/urlshots-api',
        author="Jacob Alheid",
        author_email="jake@about.me",
        py_modules=['urlshots'],
        install_requires=[
            'pytool >= 2.3.2',
            'pyconfig',
            'urllib3',
            ],
        test_suite='nose.collector',
        tests_require=[
            'nose',
            'mock',
            ],
        )



