import logging

from jarn.checkinterval.checkinterval import checkinterval

class Recipe(object):
    """ The recipe object """

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.logger = logging.getLogger(self.name)
        self.calculate_value()

    def install(self):
        """ on install... calculate the value """        
        self.calculate_value()
        return ''
    
    def update(self):
        """ on update... calculate the value again """
        self.calculate_value()
        return ''

    def calculate_value(self):
        self.logger.info('Calculating checkinterval, wait please...')
        self.value = str(checkinterval())
        self.options['value'] = self.value
        self.logger.info('Value for checkinterval is: %s' % self.value)
