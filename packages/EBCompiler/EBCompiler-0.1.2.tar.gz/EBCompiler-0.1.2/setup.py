from distutils.core import setup

setup(
    name='EBCompiler',
    version='0.1.2',
    description='Compiles simple statements of existence and boolean truth into valid SQL (i.e. for check constraints).',
    packages=['ebcompiler'],
    package_dir={'ebcompiler': 'ebcompiler'},
    license='MIT',
    author='Joel Verhagen',
    author_email='joel.verhagen@gmail.com',
    url='https://bitbucket.org/knapcode/ebcompiler',
    classifiers=(
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ),
)
