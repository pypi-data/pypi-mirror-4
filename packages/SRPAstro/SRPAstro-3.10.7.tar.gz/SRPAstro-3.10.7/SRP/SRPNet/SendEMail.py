""" Utility functions and classes for SRP

Context : SRP
Module  : Net.py
Version : 1.0.0
Author  : Stefano Covino
Date    : 14/11/2010
E-mail  : stefano.covino@brera.inaf.it
URL:    : http://www.merate.mi.astro.it/utenti/covino

Usage   : to be imported

History : (14/11/2010) First version.

"""

import os, smtplib



def SendEMail (message, emaillist, smtp, emailsubj, fromemail):
    try:
        s = smtplib.SMTP(smtp)
    except socket.gaierror:
        return False
    s.set_debuglevel(False)
    SenderEMail = "Sender: %s" % fromemail
    MessageToBeSent = SenderEMail+os.linesep+"Subject: "+emailsubj+os.linesep*2+message
    if emaillist != []:
        s.sendmail(fromemail, emaillist, MessageToBeSent)
        s.quit()
    return True

