##############################################################################
#
# Copyright (c) 2010 Projekt01 GmbH.
# All Rights Reserved.
#
##############################################################################
"""
$Id:$
"""

j01_validator_template = """
<script type="text/javascript">
  $(document).ready(function(){
    $("%(expression)s").j01Validate({%(settings)s});
  });
</script>
"""


def getJ01ValidatorJavaScript(data):
    """J01Validator JavaScript generator.
    
    Knows how to generate customization for j01Validator JS with a given
    validation url.
    
    The data argument allows you to set key, value pairs for customized data.
    """
    widgetExpression = data.pop('widgetExpression')
    
    lines = []
    append = lines.append
    for key, value in data.items():
        if key in ['callback']:
            append("\n    %s: %s" % (key, value))
        elif isinstance(value, basestring):
            if value.startswith('$'):
                append("\n    %s: %s" % (key, value))
            else:
                append("\n    %s: '%s'" % (key, value))
        else:
            append("\n    %s: %s" % (key, value))
    settings = ','.join(lines)
    return j01_validator_template % ({'expression': widgetExpression,
                                      'settings': settings})


class J01ValidatorMixin(object):
    """J01Validator mixin class for JSON-RPC forms"""

    # internals
    j01ValidatorMethodName = 'j01Validate'
    j01ValidatorExpression = '.j01Validate'

    @property
    def j01ValidatorURL(self):
        return self.pageURL

    @property
    def j01ValidatorJavaScript(self):
        data = {'url': self.j01ValidatorURL,
                'methodName': self.j01ValidatorMethodName,
                'widgetExpression': self.j01ValidatorExpression,
                }
        return getJ01ValidatorJavaScript(data)
