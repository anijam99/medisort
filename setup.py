from setuptools import setup, find_packages

setup(
    name="medisort",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pillow>=9.0.0',
        'opencv-python>=4.5.0',
    ],
    entry_points={
        'console_scripts': [
            'medisort=medisort.medisort:main',
        ],
    },
    python_requires='>=3.6',
)