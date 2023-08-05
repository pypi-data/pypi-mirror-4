from setuptools import setup

setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
]

setup(
    setup_requires=setup_requires,
    d2to1=True,
)
