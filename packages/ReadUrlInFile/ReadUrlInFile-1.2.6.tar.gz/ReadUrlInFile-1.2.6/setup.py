from distutils.core import setup
setup(
	name		= 'ReadUrlInFile',
	version		= '1.2.6',
	py_modules	= ['ReadUrlInFile'],
	author		= 'Chen',
	author_email	= 'chen.yang.fr@gmail.com',
	url		= 'http://www.yangchen.fr',
	description	= 'Sometimes you may want to read the URLs in a file(line by line), and use it directly in a method such like http.client.HTTPConnection(url). In order to avoid a mistake, you need to delete the last char "\\n" in each URL. So this is a simple example, the programe ReadUrlInFile.py reads the URLs in a file named "list", and sends HTTP requesets to these URLs using the module http.client. (You need to manually creat a file including the URLs line by line)',
)
