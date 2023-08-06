from distutils.core import setup
import platform

system=platform.system()
if system=="Windows":
    import py2exe
    
setup(
    name='fengshui',
    version='0.0.2',
    description='caluclate ming gua',
    author='Cornelius Koelbel',
    license='GPL v3',
    author_email='corny@cornelinux.de',
    url='http://www.cornelinux.de',
    packages = ["fengshui_utils"],
    scripts = ["fengshui.py"],
    setup_requires=[],
    include_package_data=True,
    data_files=[ ("share/fengshui", ["main.glade"]),
                ('share/locale/de/LC_MESSAGES',['locale/de/LC_MESSAGES/fengshui.mo']),
       ],
    classifiers=[
		"Development Status :: 2 - Pre-Alpha",
		"Programming Language :: Python",
	],
    zip_safe=False,

)
