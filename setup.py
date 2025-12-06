from setuptools import setup, find_packages
import sys

# Custom setup for portable mode
def post_install():
    """Ask user if they want portable mode after installation"""
    try:
        response = input("\nDo you want to enable portable mode? (y/N): ").strip().lower()
        if response == 'y':
            print("\n=== Portable Mode Setup ===")
            print("Portable mode stores all data in the same folder as Ghosty.")
            print("This is useful for USB drives or keeping everything together.")
            print("\nTo enable portable mode manually:")
            print("1. Navigate to where ghosty.py is installed")
            print("2. Create an empty file called 'portable.txt'")
            print("3. Create a folder called '.ghosty_data'")
            print("\nData will then be stored in the '.ghosty_data' folder.")
            print("Without portable.txt, data goes to ~/.ghosty_todo/")
            print("===========================\n")
    except:
        pass  # Don't crash if input fails

setup(
    name='ghosty-todo',
    version='1.0.0',
    description='A minimalist todo list manager',
    author='AK',
    py_modules=['ghosty'],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'ghosty=ghosty:main',
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)

# Only run post-install if we're doing an install
if 'install' in sys.argv:
    post_install()