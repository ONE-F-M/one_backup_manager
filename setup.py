from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in one_backup_manager/__init__.py
from one_backup_manager import __version__ as version

setup(
	name="one_backup_manager",
	version=version,
	description="Handles Backups of files to External File Storage",
	author="ONE FM",
	author_email="support@one-fm.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
