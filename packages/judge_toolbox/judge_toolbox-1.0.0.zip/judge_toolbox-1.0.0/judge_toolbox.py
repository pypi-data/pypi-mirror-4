"""
This module contains several useful functions, which I simply don't want to
generate over and over, ... again.
"""

# http://code.activestate.com/recipes/65215-e-mail-address-validation/
# This function validates a given E-Mail address to be valid or not, based on regex-rules.
# It returns False or True
def validateEmail(mail):
    import re
    if len(mail) > 5:
        if re.match("^[a-zA-Z0-9._%-+]+@[a-zA-Z0-9._%-]+.[a-zA-Z]{2,6}$", mail) != None:
            if not "@" or not "." in mail:
                return False
            return True
    return False
