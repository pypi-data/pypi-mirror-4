Source checking/linting tool
----------------------------

It's easy to use.

Import the package you want to check:

  >>> import refline.srccheck

Import the checker:

  >>> from refline.srccheck.checker import checker

Run the checks.
It will pinpoint the problems found.

  >>> c = checker(refline.srccheck)
  >>> c.run()
  <BLANKLINE>
  testing/bad.css
  ---------------
    PropertyValue: No match: ('CHAR', u':', 4, 10)
    PropertyValue: Unknown syntax or no value:  10px
      width: 20
  <BLANKLINE>
    CSSStyleDeclaration: Syntax Error in Property: height: 10px
      width: 20
  <BLANKLINE>
  <BLANKLINE>
  testing/bad.py
  --------------
    Tab found in file
    9: 	print "there's a tab"
       ^
  <BLANKLINE>
  testing/bad.py
  --------------
    undefined name 'bar'
    6:     foo = bar
  <BLANKLINE>
  testing/some.js
  ---------------
    Breakpoint found in line
    2:     console.log("blabla");
  <BLANKLINE>
  testing/z3c.form.po
  -------------------
    Fuzzy/untranslated found
    1: 1 untranslated items
    Fuzzy/untranslated found
    1: 1 fuzzy items


Just in case you cannot / do not want to avoid those problems,
fix them in the doctest as above.

To ignore files:

- With the string `checker_ignore_this_file` in the file

- With the checker `ignoreFiles` parameter

- With `##ignore PyflakesChecker##` in the file