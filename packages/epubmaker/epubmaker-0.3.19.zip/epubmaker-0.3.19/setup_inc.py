#
# epubmaker common setup all flavors
#

VERSION = '0.3.19'

package_dir = {
    'epubmaker': 'src', 
    }

# The documentation is pretty ambiguous about which 'requires' to use
# so we just provide both.

requires = [
    'setuptools',
    'docutils (>= 0.8.1)',
    'lxml (>= 2.3)',
    'cssutils (>= 0.9.8a1)',
    'PIL (>= 1.1.7)',
    ]
    
install_requires = [
    'setuptools',
    'docutils >= 0.8.1',
    'lxml >= 2.3',
    'cssutils >= 0.9.8a1',
    'PIL >= 1.1.7',
    ]
    
pypi_packages = [
    'epubmaker.parsers',
    'epubmaker.packagers',
    'epubmaker.mydocutils',
    'epubmaker.mydocutils.parsers',
    'epubmaker.mydocutils.transforms',
    'epubmaker.mydocutils.writers',
    'epubmaker.mydocutils.gutenberg',
    'epubmaker.mydocutils.gutenberg.parsers',
    'epubmaker.mydocutils.gutenberg.transforms',
    'epubmaker.mydocutils.gutenberg.writers',
    ]

ibiblio_packages = pypi_packages + [
    'epubmaker',
    'epubmaker.lib',
    'epubmaker.writers',
    ]
    
pypi_py_modules = [
    'epubmaker.CSSApplicator',
    'epubmaker.CommonOptions',
    'epubmaker.EpubMaker',
    'epubmaker.HTMLChunker',
    'epubmaker.ParserFactory',
    'epubmaker.Spider',
    'epubmaker.Unitame',
    'epubmaker.UnitameData',
    'epubmaker.Version',

    'epubmaker.lib.DublinCore',
    'epubmaker.lib.GutenbergGlobals',
    'epubmaker.lib.Logger',
    'epubmaker.lib.MediaTypes',

    'epubmaker.WriterFactory',
    'epubmaker.writers.EpubWriter',
    'epubmaker.writers.HTMLWriter',
    'epubmaker.writers.KindleWriter',
    'epubmaker.writers.PDFWriter',
    'epubmaker.writers.PicsDirWriter',
    'epubmaker.writers.RSTWriter',
    'epubmaker.writers.TxtWriter',
    ]

pypi_package_data = {
    'epubmaker.parsers': ['broken.png'],
    'epubmaker.mydocutils.parsers': ['*.rst'],
    'epubmaker.mydocutils.writers': ['*.css'],
    'epubmaker.mydocutils.gutenberg.parsers': ['*.rst'],
    }

ibiblio_package_data = {
    'epubmaker.parsers': ['broken.png'],
    'epubmaker.writers': ['cover.jpg', 'qioo-skeleton.zip'],
    'epubmaker.mydocutils.parsers': ['*.rst'],
    'epubmaker.mydocutils.writers': ['*.css'],
    'epubmaker.mydocutils.gutenberg.parsers': ['*.rst'],
    }
    
pypi_data_files = [
    ('', ['CHANGES', 'setup_inc.py']),
    ('epubmaker/writers', ['src/writers/cover.jpg']),
    ]
    
ibiblio_data_files = [
    ('epubmaker', ['CHANGES', 'setup_inc.py']),
    ]
    
pypi_entry_points = {
    'console_scripts':
        ['epubmaker = epubmaker.EpubMaker:main'],
    }

ibiblio_entry_points = {
    'console_scripts':
        ['makepub = epubmaker.make:main',
         'epubmaker = epubmaker.EpubMaker:main'],
    }

ibiblio_scripts = [
    'scripts/convert_unitame.py',
    'scripts/rhyme_compiler.py'
    ]

# metadata for upload to PyPI
    
author = "Marcello Perathoner"
author_email = "webmaster@gutenberg.org"
description = "The Project Gutenberg tool to generate EPUBs and other ebook formats."
long_description = open ('README').read ()
license = "GPL v3"
keywords = "ebook epub kindle pdf rst reST reStructuredText project gutenberg format conversion"
url = "http://pypi.python.org/pypi/epubmaker/"

classifiers = [
    "Topic :: Text Processing",
    "License :: OSI Approved :: GNU General Public License (GPL)",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Intended Audience :: Other Audience",
    "Development Status :: 4 - Beta"
    ]
                   
platforms = 'OS-independent'

