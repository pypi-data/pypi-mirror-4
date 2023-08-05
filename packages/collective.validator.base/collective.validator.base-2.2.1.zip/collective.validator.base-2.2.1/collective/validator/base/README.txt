ValidationTool
==============
Introduction
------------

ValidationTool is a web validator for Plone 3. It validate all the pages of the plone site that we want.
This package is a base-tool that set some option fields and needs plugin-packages to do the effective validation.
Each plugin allows to set a different type of validation (like Css,xhtml Strict or Transitional).

Every package has some tests and is also translated in italian.

The base-tool is an installing product, and the plugins needs only to  be placed in the "src" directory and registered in buiildout.cfg.

The log of the validation can be stored in a separate log.
To save into a separate log you need to set an environment-vars named VALIDATOR_LOG_FILE into the instance section of buidout.cfg 
with the path of your log file. (eg: /opt/validator.buildout/val/log/validator.log)

There is the possibility to set an enviorment-var named VALIDATOR_PORTAL_URL into the instance section of buildout.cfg.
This var is used as url of portal during the creation of reports of our validations.
The var is usefull if we have to call the validation directly from the server, like wget, and the url contains 'localhost' and 
the port of instance.

Once installed the package with quick installer, you can see it and set its fields in site setup->additional products.
If you click it,you go in a page that allows us to see the report list of validations, or configure our tool.

It is also possible validate a single page by clicking on "validate XHTML some_validator" link at the bottom, if the page belongs to 
the selected types.

An other functionality is the remote validation. It allows to run a validation of the site using "url_of_the_site/remote_validator".
This functionality can be used for example if you want to schedule a periodical validation with probrams like "cron".


Content
-------

In the configuration page there are the following fields divided into 3 parts:

Config:

* Validation type: a selection field to set the validator type for integrated validation
* Validator url: text filed where can be set the url of the w3c validator to use. For example the official w3c validator, or a local validator with w3c's sources
* Sleep interval: set a delay between each validation call
* Enable integrated validation code: enable an option that allows to validate a single page

Validation:

* Validation type: a selection field to set the validator type for portal validation
* Portal types to validate: a multi-selection field that lists all the available portal_types to be validated
* Review states to validate:a multi-selection field that lists the review states to be validated
* Anonymous validation: if this control is checked, the tool take html's pages code like an anonymous user view
* Max days from last modification: max number of days from last modification of contents. Keep 0 to ignore filter
* Create report document: create the report in a special document object called "ATReport"
* Create file document: create the report in a .txt file. This file is lighter than ATReport
* Send report to email address: if you want to send the report by email,you select that field
* Delivery addresses: a list of the addresses to send reports

Debug:

* Portal types to validate: a multi-selection field that lists all the available portal_types to be debugged
* Send report to email address: if you want to send the report by email,you select that field
* Delivery addresses: a list of the addresses to send reports

Proxy:

* Proxy address
* Proxy port
* Proxy userid
* Proxy password

Then you can Save the options, cancel changes, save and run validation/debug or go to the report page.

Every time that you validate the site, a report page with the validation results is created and stored in the tool, and if you want it is
also delivered to you by email.

Adding new validators
---------------------

to create a new validator you have to do the following steps:

Create an egg with "paster create -t nested_namespace collective.validator.type_to_validate".

In collective.validator.your_validator/collective/validator/your_validator/ should be the following files:

* configure.zcml with this string: <adapter factory=".adapter.class_name_of_the_adapter" />.
* adapter.py that extend "Parser" class, implements "Iadapter_name" interface and adapts "IVTPLone" interface.
  It should have "val_url" and "val_type" strings that contains the validator url and the type
  of validator that you want use (look how i write it in the other adapters). then it should have a
  "getValidationResults" metohd that set up the connection with the remoe validator and call the xml interpreter.
  "runValidation" method that search the pages selected,call "getValidationResults" for each page and create the report
  "runDebugValidation" method that try to validate alternative views,like edit and news.
  "getValidatorUrl" and "getValidatorType" methods that return url and type values
  
* interfaces folder that contains init.py module and interfaces.py file that define the adapter class
* i18n folder that conatins translation files
* tests folder that contains test files

Put this package in "src" folder of the buildout, register it in the buildout.cfg, rebuild buildout and it  will should work.

Credits
-------

This is a project started from Luca Fabbri and Mirco Angelini, i've just modified it and finished its functionalities.
Thanks to all RedTurtle Technology team that helps me to do this project.

Contacts
--------

Andrea Cecchi: andrea.cecchi@redturtle.net

Mirco Angelini: mirco.angelini@redturtle.net

Luca Fabbri: luca.fabbri@redturtle.net

RedTurtle Technology: info@redturtle.net

