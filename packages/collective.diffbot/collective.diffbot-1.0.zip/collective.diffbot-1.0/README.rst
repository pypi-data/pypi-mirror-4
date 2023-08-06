==================
collective.diffbot
==================
This tool allows you to use diffbot.com API within your Plone site

Install
=======

- Add collective.diffbot to your eggs and zcml section in your buildout
  and re-run buildout.
- Install collective.diffbot within Site Setup > Add-ons
- Register for a diffbot token at: http://diffbot.com/pricing/
- Within your Plone Site > Site Setup > Diffbot API add token and other diffbot
  settings

Upgrade
=======

- Within "Plone > Site setup > Add-ons" click on upgrade button available for
  collective.diffbot (if any)

Usage
=====

1. Add **diffbot** CSS class to your links::

    <a href="http://www.bbc.co.uk/news/uk-21375594"
       class="diffbot">

2. Add **rel** attribute to tell to the system where to display diffbot.com results::

    <div class=".diffbot-container"></div>
    <a href="http://www.bbc.co.uk/news/uk-21375594"
       class="diffbot"
       rel=".diffbot-container">
