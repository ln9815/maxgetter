from setuptools import find_packages, setup
setup(
    name='getmax',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'requests', 'sqlalchemy', 'pymysql', 'Click', 'schedule','Dynaconf'
    ],

    entry_points={
        'console_scripts': [
            'runmax = getmax.scripts.runmax:do',
        ],
    },
)
