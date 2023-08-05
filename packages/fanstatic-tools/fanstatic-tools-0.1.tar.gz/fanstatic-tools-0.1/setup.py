from setuptools import setup, Command

class PyTest(Command):
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)

class PyTestWithCov(PyTest):
    def run(self):
        import sys,subprocess
        errno = subprocess.call([sys.executable, 'runtests.py', '--cov-report=html', '--cov=.', '--pdb'])
        raise SystemExit(errno)

setup(
    name='fanstatic-tools',
    version='0.1',
    description="fanstatic tools",
    classifiers=[
      "Programming Language :: Python :: 2.6",
      "Programming Language :: Python :: 2.7",
      "Programming Language :: Python :: 3.2",
      "Programming Language :: Python :: 3.3",
      "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords='',
    author='ENDOH takanao',
    long_description=open('README.rst').read(),
    license='BSD',
    url='http://fanstatic.org',
    install_requires=['six'],
    packages=['fanstatic'],
    py_modules=['mkfanstaticsymlink'],
    entry_points={
      'console_scripts': [
        'mkfanstaticsymlink = mkfanstaticsymlink:main',
        ]
    },
    zip_safe=False,
    cmdclass = {
      'test': PyTest,
      'cov': PyTestWithCov,
    },
)
