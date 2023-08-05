from setuptools import setup, Extension

setup(name='mongomem',
    version='0.1',
    author='Adam Flynn',
    author_email='adam@contextlogic.com',
    description="A tool to analyze MongoDB memory usage by collection",
    keywords="mongodb",
    license="MIT",
    url="http://www.github.com/ContextLogic/mongodbtools",

    ext_modules=[
          Extension('ftools', ['src/python-ftools/ftools.c']),
    ],
    install_requires=[
        'pymongo',
        'argparse==1.2.1 ',
    ],
    scripts=['src/mongomem.py']
)
