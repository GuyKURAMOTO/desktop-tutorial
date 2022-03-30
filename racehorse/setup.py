import setuptools

def _requires_from_file(filename):
    return open(filename).read().splitlines()

setuptools.setup(
    name="netkeibaDataCollector",
    version="0.0.1",
    install_requires=_requires_from_file('requirements.txt'),
    entry_points={
        'console_scripts': [
            'collect=netkeiba:main',
        ],
    },
    author="kg",
    author_email="g.kurarymond@gmail.com",
    description="A tool for collecting race results from netkeiba",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)