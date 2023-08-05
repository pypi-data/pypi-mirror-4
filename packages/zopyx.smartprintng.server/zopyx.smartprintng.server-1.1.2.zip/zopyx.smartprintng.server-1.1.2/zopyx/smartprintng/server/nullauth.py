##########################################################################
# zopyx.smartprintng.server
# (C) 2008, 2009, ZOPYX Ltd & Co. KG, Tuebingen, Germany
##########################################################################

def authenticateRequest(username, password):
    """ Anonymous authentication """

    return True


def authorizeRequest(auth_token):
    """ Anonymous authorization """

    return True
