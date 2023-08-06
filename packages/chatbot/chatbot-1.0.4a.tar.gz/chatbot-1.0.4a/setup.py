from setuptools import setup, find_packages

setup(name='chatbot',
      version='1.0.4a',
      description='Allows users on wikia wikis to create a chatbot for Special:Chat',
      long_description="""This is a chat bot making module for wikia's Special:Chat.
It allows you to connect to the chat and execute actions and retrieve events all specified by
the author.  Very function for beginners to advanced python users.""",
      author='Matthew Cunningham',
      author_email='hairrazerrr@gmail.com',
      url='http://packages.python.org/chatbot/',
      download_url='https://github.com/hairr/chatbot/archive/master.zip',
      requires="requests",
      py_modules=['chatbot'],
      keywords= "hairr wikia xhr chat bot",
      license= "MIT License",
      classifiers = [
      	"Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.7",
        "Topic :: Communications :: Chat"
      ]
     )