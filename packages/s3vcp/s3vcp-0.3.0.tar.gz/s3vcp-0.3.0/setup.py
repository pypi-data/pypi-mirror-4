from setuptools import setup, find_packages
setup(
    name="s3vcp",
    version="0.3.0",
    packages=find_packages(),
    install_requires=["boto>=1.6"],
    author="Mads Sulau Joergensen",
    author_email="mads@sulau.dk",
    description="A simple s3 file/directory synchronizer, that has the unique abilities to use multiple threads and only copy files with a changed md5 hash.",
    license="BSD",
    keywords="boto s3 version upload sync",
    url="http://bitbucket.org/madssj/s3vcp/",
    entry_points={
        "console_scripts": [
            "s3vcp = s3vcp.s3vcp:main",
        ],
    }
)
