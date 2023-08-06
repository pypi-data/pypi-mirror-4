def makeFieldsInvisible(schema=None, fields=[]):
    """ Makes schemata fields respective widgets invisible in the view page or edit form.
        
        @schema: Archetypes schema object
        @fields: list of field ids/names
    """

    if schema is not None:
        for field in fields:
            schema[field].widget.visible = {
                'view':'visible',
                'edit':'invisible'
                }
        
def changeFieldsSchemata(schema=None, fields=[]):
    """ Moves fields into different schemata parts like categorisation or settings etc.
        "fields" parameter is expected to be a list of dicts with key: (field) id and
        (schemata id) schemata
    """

    if schema is not None:
        for field in fields:
            schema.changeSchemataForField(field['id'], field['schemata'])

