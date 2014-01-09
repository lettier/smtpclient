![Alt text](https://raw.github.com/lettier/smtpclient/master/screenshot.jpg)

# SMTP Client

This simple SMTP client allows one to send emails from the command line. It offers the option of either using the standard SMTP port 25 or the secure TLS port 587. When using port 587, you will need to specify the user-name and password to your remote email provider account. The client will attempt to guess the SMTP server host name from the specified `From:` input but if it cannot, you will need to specify your email provider's SMTP server host name. For example, `smtp.gmail.com`.

Needs [DNSPython](http://www.dnspython.org/).

_(C) 2014 David Lettier._  
http://www.lettier.com/