from distutils.core import setup, Extension

setup(
		name = "circle",
		version = "1.1",
		ext_modules = [Extension("circle", ["circle.c"])]
	)