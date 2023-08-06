try:
    from setuptools import setup
except:
    from distutils.core import setup

setup(
    name='pydataframe',
    version='0.1.6.180',
    packages=['pydataframe',],
    license='BSD',
    url='http://code.google.com/p/pydataframe/',
    author='Florian Finkernagel',
    description = "A DataFrame (table like datastructure) for Python, similar to R's dataframe based on numpy arrays",
    author_email='finkernagel@coonabibba.de',
    long_description=open('README.txt').read(),
    install_requires=[
        'numpy>=1.3',
        ]
)
