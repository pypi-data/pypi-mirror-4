# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from werkzeug.routing import IntegerConverter


class ActiveRecordConverter(IntegerConverter):
    """
    Works like the Integer Converter but also accepts Model instances
    as a valid argument 
    """
    def __init__(self, url_map, model):
        """
        :param model: If a model is specified, then the instance created
                      will be an instance of that model
        :type model: string or unicode
        """
        super(ActiveRecordConverter, self).__init__(url_map)
        self.model = model

    def to_python(self, value):
        from trytond.pool import Pool
        record_id =  super(ActiveRecordConverter, self).to_python(value)
        return Pool().get(self.model)(record_id)
