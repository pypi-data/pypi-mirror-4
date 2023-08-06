from lxml import etree

from . import schema_path

def validate(xml_tree):
    """Validate the supplied ElementTree against the GPX 1.0 schema.

    Args:
        xml_tree (ElementTree): An lxml ElementTree for the document to be
            validated.

    Raises:
        lxml.etree.DocumentInvalid If the document did not validate. The
            exception payload contains details of the validation failure.
    """
    gpx_schema_doc = etree.parse(schema_path('gpx_1_0.xsd'))
    gpx_schema = etree.XMLSchema(gpx_schema_doc)
    gpx_schema.assertValid(xml_tree)

