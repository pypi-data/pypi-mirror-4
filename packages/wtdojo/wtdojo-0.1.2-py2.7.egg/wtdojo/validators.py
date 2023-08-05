"""
Module for translating WTForms validators to Dojo validation constraints
"""

import fields as dojo_fields


def get_dojo_constraint(field, V):
    """
    Given a WTForms validator object, returns the dojo contraints string required to implement the same
    validator using Dojo
    """

    validator_type = V.__class__.__name__

    #<wtforms.validators.Required object at 0x96a3c2c>
    #<wtforms.validators.Length object at 0x96a3eac>
    #<wtforms.validators.Email object at 0x96a3ecc>
    if 'Required' == validator_type:
        return ('property', 'required=True')
    #elif 'Length' == validator_type:
    #
    #    if issubclass(field.__class__, dojo_fields.DojoStringField):
    #        #x{min,max} will match x between min and max times
    #        #x{min,} will match x at least min times
    #        #x{,max} will match x at most max times
    #        #x{n} will match x exactly n times
    #
    #        s = ""
    #
    #        #print(V.min)
    #        if int(V.min) < 0:
    #            V.min = 0
    #
    #        if V.min and V.max:
    #            if V.min == V.max:
    #                s = "regExp:'\\\\w{%s}'" % (str(V.min))
    #            else:
    #                s = "regExp:'\\\\w{%s,%s}'" % (str(V.min), str(V.max))
    #        elif V.max:
    #            s = "regExp:'\\\\w{,%s}'" % (str(V.max))
    #        elif V.min:
    #            s = "regExp:'\\\\w{%,s}'" % (str(V.min))
    #
    #        return ('dojo_property', s)

    else:
        return ('', '')


def get_dojo_constraints(field):
    """
    Given a list of WTForms validator objects, returns the dojo properties and constraints lists required to implement
    the same validators using Dojo
    """

    properties = []
    constraints = []
    dojo_properties = []

    for V in field.validators:
        vt, s = get_dojo_constraint(field, V)
        if '' != s:

            if 'property' == vt:
                properties.append(s)
            elif 'dojo_property' == vt:
                dojo_properties.append(s)
            elif 'constraint' == vt:
                constraints.append(s)

            ## add validator's message to dojo data props
            #if vt in ['property', 'dojo_property', 'constraint']:
            #    dojo_properties.append("invalidMessage: '%s'" % V.message)

    return (properties, dojo_properties, constraints)


def get_validation_str(field):
    """
    Given a field, returns a string suitable for placing inside the
    <input> or <div> etc tags to actually implement the validation according to the field's validators
    """
    props_str = ''
    dojo_props_str = ''
    dojo_constraints_str = ''
    use_comma = ''

    # check if field has validators and if it has add dojo constraints accordingly
    if len(field.validators) > 0:
        properties, dojo_properties, constraints = get_dojo_constraints(field)

        if len(properties) > 0:
            props_str = " ".join(properties)

        if len(dojo_properties) > 0:
            dojo_props_str = ", ".join(dojo_properties)
            use_comma = ','

        if len(constraints) > 0:
            dojo_constraints_str = ", ".join(constraints)

    return '%s data-dojo-props="%s%s constraints: {%s}"' % (props_str, dojo_props_str, use_comma, dojo_constraints_str)

