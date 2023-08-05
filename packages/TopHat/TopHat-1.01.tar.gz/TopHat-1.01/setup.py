from distutils.core import setup
files=['TopHat_Platform/*']
setup(name = "TopHat",
    version = "1.01",
    description = "TopHat Platform",
    author = "TopHat Software",
    author_email = "hello@tophat.ie",
    url = "http://tophat.ie",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['TopHat_Platform'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    package_data = {'TopHat_Platform' : files },
    #'runner' is in the root.
    scripts = ["server"],
    long_description = """Really long text here.""" 
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 
