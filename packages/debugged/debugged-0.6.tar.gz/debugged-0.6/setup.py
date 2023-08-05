from setuptools import setup

setup(
    name='debugged',
    version='0.6',
    url='https://github.com/RokkinCat/debugged-python',
    license='BSD',
    author='Nick Gartmann',
    author_email='nick@rokkincat.com',
    description='A developer tool to prepare for and respond to '
                'unexpected problems.',
    py_modules=['debugged'],
    zip_safe=True,
    platforms='any',
    install_requires=[
        'requests>=0.14.2'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
