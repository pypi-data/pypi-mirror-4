drequests
=======

Before install drequests,make sure had installed pydomain("sudo pip install pydomain")

drequests  is an Apache2 Licensed HTTP library, written in Python, for human beings.

Python’s standard pycurl2 module provides most of the HTTP capabilities you need, but the API is thoroughly broken. It was built for a different time — and a different web. It requires an enormous amount of work (even method overrides) to perform the simplest of tasks..

Things shouldn’t be this way. Not in Python.
>>>from drequests import DRequests
>>>resp = DRequests(url = 'http://www.piadu.com')
>>>resp.status_code
200
>>>resp.text
<html ....
