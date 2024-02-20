from setuptools import setup, find_packages

setup(
    name="gamenpc",
    version="0.1",
    packages=find_packages(),
    description="A game npc python package.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="shikanon",
    author_email="your.email@example.com",
    url="https://github.com/shikanon/game-npc",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)