This is an unoffical eggification of the WingDBG product. It includes several patches that make it works better with Plone 4 and Chameleon.

Zope product that allows Wing to debug Python code running under Zope2. For more information on how to use it please refer at the official page: [[http://www.wingware.com/doc/howtos/zope|Using Wing IDE with Zope]].


To use it add following lines in your buildout:

[buildout]
eggs += WingDBG
zcml += WingDBG

 How to build a new release 

Since the WingIDE 4 is released there's no major modification in WingDBG. Between 4.0 and 4.1 only libraries path was modified.

The best way to update this package is to make a diff between the current release (WingDBG-4.1.7-1.tar) and the new release and applys the patch to these sources.

