# This file is used as template to create a user specific configuration 
# of the cpe.py and cpdb.py applications in case it does not exist.
#
# Currently there are just a few entries available, which may be configured.
# To change the configuration, uncomment the appropriate line starting with
# DEFAULT_CONFIG.
# and adjust the configuration parameter to you needs.

# for simpler notation we import  os.path functions 'join' and 'expanduser'.
from os.path import join, expanduser

# When reading \city{...} commands from within diagrams, the application splits
# the information into country and city. The default implementation
# uses a regular expression based approach to split the given city and country.
# You may register another implementation, which accepts a single string and returns
# an array containing the country-code and the city name - or the city name only, if no country-code is given.
#
# DEFAULT_CONFIG.city_split = default_city_split

# You may configure the size of the chess images in pixels
# Possible values are: 32, 36, 40, 44 and 48 pixels
#
# DEFAULT_CONFIG.image_pixel_size=40

# You may configure when the legend around the board is displayed.
# Possible values are:
#   'always':    the legend is always displayed - this is the default
#   'never':     the legend is never displayed
#   'automatic': the legend is displayed, when the scrollbars are displayed (rows/columns > 8)
# DEFAULT_CONFIG.legend_display='always'

# The cpe.py and cpdb.py applications access a database to store authors, cities, countries and sources.
# The following configuration option is used to specify the sqlite url of the database
#
# DEFAULT_CONFIG.database_url = 'sqlite:///' + join(CONFIGDIR, 'cpe.db')


# Within the cpe.py application, there is menu entry named 'Compile', which allows to 
# write all current problems to a file and call a latex compiler and viewer.
# To have entries within this menu, you must fill the
# DEFAULT_CONFIG.compile_menu_actions array with 5-valued tuples as shown below.
# 
# ----- example config start -----
# _dias34_dir = join(expanduser('~'), '.cpe', 'dias34')
# 
# DEFAULT_CONFIG.compile_menu_actions = [
#        ('fs dias3', _dias34_dir, 'dias3.tex', 'dias3.inc', 'dias3.dvi'),
#        ('fs dias4', _dias34_dir, 'dias4.tex', 'dias4.inc', 'dias4.dvi')]
# ----- example config start -----
#
# The following describes the elements of the tuple:
# 1. the text of the menu entry
# 2. the directory, which contains all the files and is used for compilation.
#    this directory needs to be created manually
# 3. the filename to compile - this file needs to be created manually and must
#    contain an \include{<4. element>} somewhere
# 4. the name of the include file - where all problems of the current edit session are 
#    written to. This file needs to be included in (3.).
# 5. the name of the resulting output file, which is finally shown in a viewer


# The name of the viewer application to view the result of the latex compiler output.
# Unix users may use 'xdvi'.
# Miktex users on windows should specify 'yap'
# As per default there is no compile_menu_actions entry, the default value for the viewer is None.
#
# DEFAULT_CONFIG.compiled_latex_viewer = None

