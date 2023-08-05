Django Development Email
========================

This was developed as an alternative to having small if checks to send all mail to a development
 address.  We initially wanted to just override the ``_send`` method, but since it's marked as private,
 we decided to copy the class and rewrite the parts I needed.  We are certainly open to other ways
  and methods of implementing this.

Installation
------------

    pip install django-dev-email

Add the class to your ``EMAIL_BACKEND`` setting
 
 	EMAIL_BACKEND = 'dev_email.backends.development.EmailBackend'
 	
Add the email address to your settings file

	DEV_EMAIL = 'yourdevaddress@whatever.com'
	
	
Suggestions, Bugs, Comments?  Open a Github issue.

What's Next?
------------

