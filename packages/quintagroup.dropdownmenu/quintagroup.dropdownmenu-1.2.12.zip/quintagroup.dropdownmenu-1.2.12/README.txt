Introduction
------------

The product allows you to build a responsive multilevel drop-down menu that will 
provide your visitors with organized and intuitive navigation. On mobile devices 
your top menu bar transforms into one drop-down. By clicking on the title or 
a small arrow next to it all-level menu items appear below the title.

This package allows to build dropdown menu through the web with portal_actions.
Submenus are built from a tree of nested Category Actions and Actions.

The other strategy used to populate submenus is Plone default NavigationStrategy, 
the one used in navigation portlet.  

This project is successor of qPloneDropDownMenu. 

Building you dropdown menu with portal_actions
==============================================

Starting from Plone 3 portal actions introduced CMF Action Category 
containers, it opened opportunity to build nested actions trees. Though CMF Action 
Category does not behave as a regular action, it has different set of properties. 
We introduced convention in quintagroup.dropdownmenu that requires to have 
a specially named Action for each Actions Category. The id of each such action 
must be build using the rule::
  
  action_id = prefix + category_id + suffix
   
where:
  
:category_id: is id of correspondent CMF Action Category    
:prefix: defined in DropDownMenu configlet, default value ''
:suffix: defined in DropDownMenu configlet, default value '_sub'

So, the actions structure can look like::

  + portal_tabs
  |- home
  |- blog_sub
  |-+ blog
  | |-- 2009
  | |-- 2010
     
By default the root of dropdown menu is 'portal_tabs' category.

Menu caching
============

If the menu built with Navigation strategy is entirely public it can be cached for
all users. If Authenticaded users should see some non public items the menu can be
cached for anonymous only.

Caching in case of involving the portal_actions strategy is effective only in case
if all the action are public and have no extra conditions. In case some conditions
are applied per action switch off caching.

 
Compatibility
=============

* **Plone 4.x** sample CSS file based on Sunburst theme provided
* **Plone 3.x** the default CSS file has to be overridden

Installation
============

* add http://good-py.appspot.com/release/plone.app.registry/1.0b2 to versions in your buildout for Plone<4.1
* add quintagroup.dropdownmenu to eggs in your buildout
* install Plone DropDown Menu in Plone via Site Setup -> Add-ons

Find more details on the topic inside docs/INSTALL.txt 

