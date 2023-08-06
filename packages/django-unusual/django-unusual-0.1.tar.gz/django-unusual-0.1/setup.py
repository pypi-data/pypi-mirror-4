from setuptools import setup, find_packages

setup(
    name="django-unusual",
    url="https://github.com/dvogel/django-unusual",
    version='0.1',
    packages=find_packages(),
    description="Allows django apps to raise HttpResponse objects as exceptions.",
    author="Drew Vogel",
    author_email="drewpvogel@gmail.com",
    license='BSD',
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=['django']
)
