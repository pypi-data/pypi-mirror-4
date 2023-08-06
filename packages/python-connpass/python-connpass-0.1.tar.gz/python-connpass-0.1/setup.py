from setuptools import setup, find_packages
import os

__version__ = "0.1"
here = os.path.dirname(__file__)

requires = [
    "requests",
    "six",
]

tests_require = [
    "pytest",
    "mock",
    "pytest-cov",
    "testfixtures",
]

points = {
    "console_scripts": [
        "connpass=connpass.commands:main",
    ]
}

readme = open(os.path.join(here, 'README.txt')).read()
changes = open(os.path.join(here, 'CHANGES.txt')).read()

setup(name="python-connpass",
      version=__version__,
      description="connpass client",
      long_description=readme+"\n"+changes,
      url="https://bitbucket.org/aodag/python-connpass",
      author="Atsushi Odagiri",
      author_email="aodagx@gmail.com",
      classifiers=[
          "Development Status :: 3 - Alpha",
          "Environment :: Console",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3.2",
          "Programming Language :: Python :: 3.3",
          "Programming Language :: Python :: Implementation :: CPython",
          "Programming Language :: Python :: Implementation :: PyPy",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Software Development :: Libraries",
      ],
      install_requires=requires,
      tests_require=tests_require,
      extras_require={
          "testing": tests_require,
          },
      packages=find_packages("src"),
      package_dir={"": "src"},
      entry_points=points,
      license='MIT',
  )
