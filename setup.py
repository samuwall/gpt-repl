from setuptools import setup, find_packages

with open('requirements.txt') as f:
  requirements = f.read().splitlines()

setup(
  name='gpt-repl',
  version='0.1.0',
  packages=find_packages(),
  include_package_data=True,
  install_requires=requirements,
  entry_points={
    'console_scripts': [
      'gpt=gpt_repl.main:main',  # "gpt" command points to the main function in main.py
    ],
  },
)
