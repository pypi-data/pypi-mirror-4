from distutils.core import setup

setup(
    name         = 'pytkapp',
    version      = '0.2.151.3',
    author       = 'Paul "Mid.Tier"',
    author_email = 'mid.tier@gmail.com',
    url          = 'http://pypi.python.org/pypi/pytkapp',
    description  = 'Python package to develop a simple application (MDI/SDI) using tkinter library.',

    packages=['pytkapp','pytkapp.tkw','pytkapp.cpr','pytkapp.demo','pytkapp.dia'],
    keywords = "tkinter mdi/sdi application widgets tablelist",
    license='LICENSE.txt',
    long_description=open('README.txt').read(),    
)