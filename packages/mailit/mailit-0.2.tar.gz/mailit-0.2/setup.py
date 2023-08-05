from distutils.core import setup, Extension

setup(name = "mailit",
    version = "0.2",
    description="A simple mass-mailer.",
    packages = ['mailit'],
    package_dir = { 'mailit' : 'mailit' },
    scripts=['massmail.py'],
)