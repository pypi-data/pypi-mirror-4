from setuptools import setup

setup_requires = [
    'd2to1',
    'nose',
    'nosexcover',
    'coverage',
    'mock',
    'webtest',
    'sphinx',
]

setup(
    setup_requires=setup_requires,
    d2to1=True,
    entry_points="""\
        [paste.app_factory]
        main = pyramid_restlogging:main
        """
)
