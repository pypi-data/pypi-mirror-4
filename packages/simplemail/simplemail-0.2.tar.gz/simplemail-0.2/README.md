# simplemail

## Overview
**simplemail** is an easy way to send emails in Python. It will use a sendmail binary which is almost always available and ready to go.

## Dependencies
- Python 2.6 or 2.7

## Sample usecase
The code has docstrings which explains how to use the library. But here's the sample usecase I just made up for showing you the benefits and simplicity of using it.

Let's assume that you have a general announcement which you would like to send out to your mailing list. The message itself is common for every member of your list, but you want to greet every person by his or her name in the beginning of your message.

So you have a list of your customer in a dictionary.

    from simplemail import Simplemail

    mailinglist = {"Bob": "bob@domain.tld",
                   "Alice": "alice@domain.tld"}

Let's fire the default settings for all our emails.

    message = Simplemail(sender="Maillist Owner <postmaster@domain.tld>",
                         subject="Monthly announcement")

Next you are going to write a default message body for everyone.

    body = "We are proudly to present our new feature."

Let's compose a personal greeting for every member of your list and fire an email.

    for person in mailinglist.keys():
        gr = "Hello, %s\n\n%s" % (person, body)
        message.send(recipient=mailinglist[person], body=gr)

Now you have a personal greeting for all of your subscribers.

## Logging handler
There is a special logging handler which utilizes the simplemail library. Here's a code sample:

    import logging
    from simplemail import Simplemail
    from simplemail.handlers import SimplemailLogger

    # Initializing Simplemail
    mail = Simplemail(sender="Application Error <errors@domain.tld>",
                      recipient=["you@domain.tld"])

    # Initializing logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    # Sending SimplemailLogger the Simplemail object, application name
    # and the treshold
    sl = SimplemailLogger(mail, __name__, logging.WARNING)
    logger.addHandler(sl)

    # Writing to the log
    logger.warn("test")

The handler's constructor expects three arguments. One is mandatory: **mailobject** is the Simplemail object itself, which needs to be initialized before. Two others are optional: **app** contains your application name, which will be mentioned in the mail subject; and **level** which is the treshold at which the handler will be triggered.

## Downloads
This library is available at [PyPi](http://pypi.python.org/pypi/simplemail).
