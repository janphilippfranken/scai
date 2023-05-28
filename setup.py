import setuptools

with open("requirements.txt", "r") as file:
    requirements = file.read().splitlines()

setuptools.setup(
    name="scai",
    version="0.0.1",
    author="Your Name",
    author_email="your-email@example.com",
    description="A small example package",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8.1,<4.0',
    install_requires=requirements,
    dependency_links=[
        "git+https://github.com/stanford-crfm/helm.git@main#egg=helm",
    ],
)
