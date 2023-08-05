from setuptools import setup, find_packages

setup(
        name = 'spiralweb',
        version = '0.2',
        packages = ['spiralweb'],
        description = 'A lightweight-markup based literate programming system',    
        author = 'Michael McDermott',
        author_email = 'mmcdermott@mad-computer-scientist.com',
        url = 'https://gitorious.org/spiralweb',
        keywords = ['literate programming', 'lp', 'markdown'],
        license = 'MIT',
        entry_points = {
            'console_scripts': [
                'spiralweb = spiralweb.main:main'
            ]},
        long_description = """\
SpiralWeb is a literate programming system that uses lightweight text
markup (Markdown, with Pandoc extensions being the only option at the
moment) as its default backend and provides simple, pain-free build
integration to make building real-life systems easy.
"""
)
