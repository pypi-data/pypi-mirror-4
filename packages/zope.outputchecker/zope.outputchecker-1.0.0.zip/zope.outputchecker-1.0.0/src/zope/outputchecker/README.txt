==============
Output Checker
==============

The output checker normalizes HTML and regular expressions. I have already
setup a checker for this file, so let's check it out.

  >>> print('<p id="greet" class="highlight">Hi</p>')
  <p class="highlight" id="greet">Hi</p>

You can see that the order of the attributes deos not matter. Next a regular
expression replacement:

  >>> print('Good morning Stephan!')
  Guten Tag Stephan!

We can also combine the two:

  >>> print('<p id="greet" class="highlight">Good morning Stephan!</p>')
  <p class="highlight" id="greet">Guten Tag Stephan!</p>
