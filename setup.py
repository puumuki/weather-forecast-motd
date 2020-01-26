
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='weather-forecast-motd',  
     version='1.0.2',
     scripts=['motd'] ,
     author="Teemu Puukko",
     author_email="teemuki@gmail.com",
     description="RasberryPI weather forecast message of the day",
     long_description=long_description,
     long_description_content_type="text/markdown",
     url="https://github.com/puumuki/weather-forecast-motd",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License"
     ],
     package_data={'motdcore': ['data/*']}          
 )