from setuptools import setup, find_packages

setup(
    name='gpt-repl',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "prompt-toolkit",
        "litellm",
        "rich",
        "pyperclip",
        "ansiwrap_hotoffthehamster",
        "pygments",
    ],
    entry_points={
        'console_scripts': [
        'gpt=gpt_repl.main:main',  # "gpt" command points to the main function in main.py
        ],
    },
)
