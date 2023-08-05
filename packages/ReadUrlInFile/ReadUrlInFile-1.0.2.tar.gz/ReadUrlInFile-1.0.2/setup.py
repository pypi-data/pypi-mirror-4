from distutils.core import setup
setup(
	name		= 'ReadUrlInFile',
	version		= '1.0.2',
	py_modules	= ['ReadUrlInFile'],
	author		= 'Chen',
	author_email	= 'chen.yang.hack@gmail.com',
	url		= 'http://www.yangchen.fr',
	description	= 'Sometimes you may want to read the URLs in a file(line by line), and use it directly in a method such like http.client.HTTPConnection(url), to avoid a mistake, you need to delete the last char "\\n" in each URL. So it\'s a simple textline reader, it can delete the last char "\\n" in the end of each line.',
)
