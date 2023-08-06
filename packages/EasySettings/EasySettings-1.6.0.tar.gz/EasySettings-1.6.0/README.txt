Easy Settings
=============

Easy Settings allows you to easily save and retrieve simple application settings.

Example
=======
Example of Easy Settings basic usage::

	#!/usr/bin/env python
	# --------------- Creation ----------------
	
	from easysettings import easysettings
	
	settings = easysettings.easysettings("myconfigfile.conf")
	
	# configfile_exists checks for existing config, creates if needed
	# you can disable the auto-create by passing False to it.
	if not settings.configfile_exists():
		raise Exception("Unable to create config file!")
	
	# ------------- Basic Functions -----------
	# set without saving
	settings.set("username", "cjw")
	
	print settings.get("username")
	# this results in "cjw"
	
	# check if file is saved
	if not settings.is_saved():
		print "you haven't saved the settings to disk yet."
	
	# ...settings are still available even if they haven't
	#    been saved to disk
	
	# save
	settings.save()
	
	# you may also set & save in one line...
	settings.setsave("homedir", "/myuserdir")
 

Other Features::
    
	# check if setting exists if you want
	if settings.has_option('username'):
		print "Yes, settings has 'username'"
	
	# list settings/options/values
	mysettings = settings.list_settings()
	myoptions = settings.list_options()
	myvalues = settings.list_values()
		
	# remove setting
	settings.remove('homedir')
	
	# clear all option names and values
	settings.clear()
	
	# clear all values, leave option names.
	settings.clear_values()


Comparison::

	# compare two settings objects
	settings2 = easysettings.easysettings('myconfigfile2.conf')
	
	if settings.compare_opts(settings2):
		print "these have the same exact options, values may differ"
	if settings.compare_vals(settings2):
		print "these have the exact same values, options may differ"
		
	if settings == settings2:
		print "these have the exact same settings/values"
		# can also be written as settings.compare_settings(settings2)
		# if you like typing.. :)
		
	if settings > settings2:
		print "settings has more options than settings2"
	# all of them work ==, !=, <=, >= , > , <
	# ... the < > features are based on amount of options.
	#     the = features are based on option names and values.


Features
========
Easy Settings has the basic features you would expect out of a settings module,
and it's very easy to use. If your project needs to save simple string settings without
the overhead and complication of other modules then this is for you. Save, load, set, & 
get are very easy to grasp. The more advanced features are there for you to use,
but don't get in the way. Settings, options, & values can be listed, searched,
detected, removed, & cleared.

Easy Settings uses a dictionary to store settings before writing to disk, so you can
also access settings like a dictionary object using ``easysettings.settings``. The
``setsave()`` function will save every time you set an option, and ``is_saved()`` will
tell you whether or not the file has been saved to disk yet. Code is documented for a
newbie, so a ``help('EasySettings')`` in the python console will get you started.

The search_query argument in the list functions lets you find settings, options, and values by search string::

	mydebugoptions = settings.list_options('debug')
	# clear all debug values..
	settings.clear_values(mydebugoptions)

Non-string types were added, so type that can be pickled can be used as an
option's value. This includes all the major types like int, long, float, boolean, and list.
All of these values will be retrieved as the same type that was set::

	es = easysettings.easysettings('myconfigfile.conf)
	
	# Boolean
	es.set("newuser", True)
	if es.get('newuser'):
		print "now you can use get() as a boolean."
	
	# Integer
	es.set('maxwidth', 560)
	halfwidth = es.get('maxwidth') / 2 # this math works.
	
	# Float
	es.set('soda', 1.59)
	f_withtax = es.get('soda') * 1.08
	
	# List
	es.set('users', ['cjw', 'joseph', 'amy']) # lists as settings, very convenient
	for suser in es.get('users'):
		print "retrieved user name: " + suser
		
	# i won't do them all, but if you can pickle it, you can use it with easysettings.
	
	
You can setup an auto load of the whole easysettings instance using the
new pickle features like this::

	from easysettings import easysettings
	es = easysettings.easysettings().load_pickle('myconfigfile.pkl')
	if es is None:
		# first time run, need to make an easysettings object.
		es = easysettings.easysettings() # uses default configfile if none is passed
		es.name = "My Project"
		es.version = "1.0"
		es.set("firstrun", False)
		es.save_pickle()
	else:
		# pickle file was found, everything from the last save_pickle() was loaded.
		print "Loaded name, version, configfile, and all settings/options/values"
		
	# now all you need to do is make sure to save_pickle() before your program exits,
	# everything you set in easysettings will be retrieved next time.
	
	
Errors are more descriptive and can be caught using their proper names::

	try:
		es.get('option_with_a_possibly_illegal_value')
	except esGetError as exErr:
		print "Error getting option!"
	except Exception as exEx:
		print "General Error!"
			
Website
=======
Be sure to visit http://welbornproductions.net for more projects and information from Welborn Productions.
