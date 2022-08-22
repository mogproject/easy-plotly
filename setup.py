from setuptools import setup, find_packages

SRC_DIR = 'src'


def get_version():
    import sys

    sys.path[:0] = [SRC_DIR]
    return __import__('easy_plotly').__version__


setup(
    name='easy-plotly',
    python_requires='>=3.6.0',
    version=get_version(),
    description='Unofficial extension of Plotly for Python',
    author='mogproject',
    author_email='mogproj@gmail.com',
    url='https://github.com/mogproject/easy-plotly',
    install_requires=[
        'pyyaml',
        'networkx',
        'jupyterlab',
        'plotly',
    ],
    tests_require=[
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
    test_suite='test',
)
