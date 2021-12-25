import setuptools

setuptools.setup(
	name = "ElectroAutomatikGmbHPy",
	version = "0",
	author = "Matias H. Senger",
	author_email = "m.senger@hotmail.com",
	description = "Control the Electro Automatik GmbH power supply from Python",
	url = "https://github.com/ElectroAutomatikGmbHPy",
	packages = setuptools.find_packages(),
	classifiers = [
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	install_requires = [
		'pandas',
	],
)
