from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='pyucallerapi',
    version='0.1.0',
    description='Python service for convenient work with uCaller API',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['pyucallerapi'],
    author='kebrick',
    author_email='ruban.kebr@gmail.com',
    license='MIT',
    project_urls={
        'Source': 'https://github.com/kebrick/pyucallerapi',
        'Tracker': 'https://github.com/kebrick/pyucallerapi/issues',
    },
    install_requires=['requests', ],
    python_requires='>=3.10',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Operating System :: OS Independent',
    ],
    zip_safe=False
)