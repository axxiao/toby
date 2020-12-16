import setuptools
from images_to_pdf import create_pdf_from_images

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="images_to_pdf",
    version="1.0.0",
    author="Alex Xiao",
    author_email="axiao@mail.com",
    description="A tool to combine images into PDF file(s)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/axxiao/toby/tree/master/tools/images_to_pdf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': ['images_to_pdf=images_to_pdf.create_pdf_from_images:main']
    },
    python_requires='>=3.6',
)
