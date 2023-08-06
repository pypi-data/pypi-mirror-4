WTF - Web Test Framework
======
https://github.com/wiredrive/wtframework


Wiredrive Test Framework (referred to as WTF for short) provides a structured testing 
framework for testing a Web Applications in a maintainable manner.  It helps QA/SDET
professionals quickly setup and develop acceptance level web tests.


Install
=======

Installation via PYPI

	pip install wtframework


Setting up your project
=======================

Run the following command to initialize an empty project structure for a WTF test.
	
	wtf_init.py YourProjectName

Windows Note: .py files may not be executable, you may have to prefix these commands 
with the python command. 
	python wtf_init.py YourProject

Next you'll need to setup your python path.

	export PYTHONPATH=$PYTHONPATH:path/to/project/tests
	
Now the directory structure and your python path is setup so nosetests can run tests 
you write in the WTF framework.


Configuring Eclipse/PyDev Environment
-------------------------------------
1. Download/Install Eclipse. http://www.eclipse.org/
2. Install the PyDev plugin. http://pydev.org/
3. Goto Eclipse -> Preferences (Or on windows, this Window -> Preferences )
4. Goto PyDev -> Interpretor Python then open the Libraries tab.
5. Add you python site-packages (where pip installs packages to)
At this point your PyDev enviornment should be able to recognize your 
installed packages.
6. In Eclipse,  goto "File" and create a new PyDev project.
7. Fill out the required fields and use your generated project structure as
your Project folder.  This should create the PyDev project files necessary to
allow you to work on this project as a PyDev project.


Running your tests
==================

Run your tests using nosetests.

	./runtests.py


WTF Framework Features
======================

PageObjects
-----------
WTF provides handy generators for quickly generating PageObjects.  The following 
command will generate a PageObject given a name and URL. To use PageObject generator,
type the following command.

	wtf_tools generate-page NameOfPageObject http://your.site.com/page/location
	
This will do the following:
1. Creates a new file named after your page object.
2. Within the file, it'll create a new class that extends PageObject base class.
3. It will generate a page validation method, which will validate the page by url.
4. It will scan the target page location for non-hidden input tags, and create 
object mappings for those inputs.  The 'name' attribute will be used for identifying 
and naming the mapped objects.

Note: I have not implemented any sort of session support yet. So this will not work in 
pages that require a session.

You can now use this page object you created like this:

	from wtframework.wtf.web.PageFactory import PageFactory
	...
	my_login_page = PageFactory.create_page(webdriver, LoginPage)
	my_login_page.login(myusername, password)

Alternatively, you can use the WebUtils to wait for the page to load.  This will allow 
you to specify a timeout period to wait for this page to finish loading.

	from wtframework.wtf.web.WebUtils import WebUtils
	...
	slow_loading_page = WebUtils.wait_until_page_loaded(webdriver, MyPage, 60)

Note: This will use the PageObject's `_validate_page()` to check if the page is 
matching the expected page.  It's good to not use URL validation in cases you expect 
the page to take a long time to load, and instead verify on a list of expected 
elements you want to have loaded.


Once you have created a PageOjbect, you'll want to go in and edit the file and make any 
changes to the mappings and page verification routines.  As a good practice, it's good 
to write methods to expose your transactional logic as a higher level method call 
to avoid cluttering your high level tests and test flows with low level UI logic.

See: http://engineeringquality.blogspot.com/2012/12/python-quick-and-dirty-pageobject.html


Configurable Tests
------------------
Being able to run tests across different environments and settings is a powerful tool.
WTF has a powerful tool for working with configurations called `CONFIG_READER`.  By 
default, it'll look at the default.yaml file in the /configs directory.  But you may 
specify using other config files by setting the `WTF_ENV` variable.  This is useful to 
have different config files for your different test environments.  Then in your CI 
system, you can just specify which config file to use.

In your tests, you can pull the values you have stored in your config file using the 
`CONFIG_READER` like this:

	base_url = CONFIG_READER.get_value("baseurl")
	webdriver.get( base_url + "/somelocation" )

This allows you to make your test environment agnostic, runnable across multiple 
configurations with just a switch of an environment variable.
	

License
-------
This framework is free and open source.  Licensed under GPLv3. See 'LICENSE.TXT' for 
license details.

Credits
------------
David Lai <david@wiredrive.com>