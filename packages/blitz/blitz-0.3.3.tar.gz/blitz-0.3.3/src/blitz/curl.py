__author__="ghermeto"
__date__ ="$09/05/2012 11:30:00$"

import time
import blitz.rush
import blitz.sprint
from blitz.api import Curl, ValidationError
from blitz.validation import validate

class Test(Curl):
    """ Curl test class that parsers a command and return either a rush or a
        sprint result object. """
    
    def parse(self, command, callback):
        """ Parses the command into a well formatter json object and invokes 
            execute. """
        self._check_authentication() #authenticates
        parse_response = self.client.parse({"command": command})
        self._check_errors(parse_response)
        options = parse_response['command']
        if 'pattern' in options:
            self.module = blitz.rush
        else:
            self.module = blitz.sprint
        time.sleep(2)
        self.execute(options, callback)
    
    def _validate(self, options):
        """ Raises a ValidationError if validation fails. """
        failed = validate(options)
        if len(failed) > 0:
            raise ValidationError('Validation error.', failed)
    
    def _format_result(self, result):
        """ Method should be overriden by subclasses and return the appropritate
            result object to be passed to the callback. """
        if self.module is None:
            pass
        else:
            return self.module.Result(result)
    