

class LeadRecord:

    def __init__(self):
        self.attributes = {}

    def __str__(self):
        return "Lead (%s - %s)" % (self.id, self.email)

    def __repr__(self):
        return self.__str__()


def unwrap(xml):
    lead = LeadRecord()
    lead.id = xml.find('Id').text
    lead.email = xml.find('Email').text

    for attribute in xml.findall('.//attribute'):
        name = attribute.find('attrName').text
        attr_type = attribute.find('attrType').text
        val = attribute.find('attrValue').text

        if attr_type == 'integer':
            val = int(val)

        lead.attributes[name] = val

    return lead
