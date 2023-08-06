#!/usr/bin/env python

from distutils.core import setup

if __name__ == '__main__':
	import sys
	
	execfile("groupdocs/version.py")

	setup(
		name = __pkgname__,
		version = __version__,
		author = "GroupDocs Team",
		author_email = "support@groupdocs.com",
		description = "A Python interface to the GroupDocs API",
		keywords = "groupdocs, document management, viewer, annotation, signature",
		license = "Apache License (2.0)",
		long_description = open('README.rst').read(),
		platforms = 'any',
		packages = ['groupdocs', 'groupdocs.models'],
		url = "http://groupdocs.com/",
		download_url = "https://github.com/groupdocs/groupdocs-python",
		classifiers = [
			"Development Status :: 4 - Beta",
			"Intended Audience :: Developers",
			"Operating System :: OS Independent",
			"Programming Language :: Python :: 2.6",
			"Programming Language :: Python :: 2.7",
			"Topic :: Software Development :: Libraries :: Python Modules",
			"License :: OSI Approved :: Apache Software License"
		],
		data_files=[('', ['README.rst'])]
	)
