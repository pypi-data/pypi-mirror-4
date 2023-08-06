from distutils.core import setup

setup(
    name='git-rv',
    version='0.1.2',
    author='Ian Wetherbee',
    author_email='ian.wetherbee@gmail.com',
    packages=[],
    scripts=['bin/git-rv'],
    url='https://github.com/wetherbeei/git-rv',
    license='LICENSE.txt',
    description='Code review tool for git and Rietveld',
    long_description=open('README').read(),
    install_requires=[
        "review"
    ],
)
