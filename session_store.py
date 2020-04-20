import base64
import os

class SessionStore:

    def __init__(self):
        self.sessions = {}
    
    # load the session data
    def getSessionData(self, sessionId):
        # check dictionary for the given sessionId
        if sessionId in self.sessions:
            # if found, return it
            return self.sessions[sessionId]
        else:
            # otherwise return None
            return None
            
    # create new session
    def createSession(self):
        # create a new session ID
        sessionId = self.generateSessionId()
        # create a new session (an empty dictionary), save into the session store
        self.sessions[sessionId] = {}
        return sessionId
        
        
    def generateSessionId(self):
        rnum = os.urandom(32)
        rstr = base64.b64encode(rnum).decode("utf-8")
        return rstr
    
    
    
