from distutils.core import setup

setup(
    name='mailsanity',
    version='0.1.4',
    author='KAction, aka Dmitry Bogatov',
    author_email='KAction@gnu.org',
    packages=['mailsanity'],
    scripts=['bin/mailsanity'],
    url='http://pypi.python.org/pypi/rss2email-reformat',
    license='LICENSE.txt',
    description='Useful email reformatting stuff.',
    long_description=open('README.txt').read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.3",
        "Topic :: Communications :: Email :: Filters"
    ],
    required = ['beautifulsoup4']
)
