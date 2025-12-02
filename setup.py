from setuptools import setup, find_packages

setup(
    name='fda_recall_checker',
    version='0.0.1',
    description='FDA Recall Checker',
    author='SurgiShop',
    author_email='gary.starr@surgishop.com',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=['frappe']
)
