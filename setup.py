from setuptools import setup, find_packages

setup(
    name='YahooFinance',
    version='0.1.9',
    packages=find_packages(),
    description='Custom Yahoo Finance utilities package for financial analysis.',
    long_description='A custom package for Yahoo Finance related utilities.', # Simpler default
    long_description_content_type='text/markdown', # Specify content type if using markdown later
    author='John Raitt', # You can change this
    author_email='your.email@example.com', # You can change this
    url='https://github.com/jraitt/YahooFinance.git', # Optional: if you have a repo
    install_requires=[
        'yfinance',
        'pandas',
        'numpy',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License', # Optional: Choose a license
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
