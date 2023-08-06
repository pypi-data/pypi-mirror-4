dc_namespace_declaration = """xmlns:dc=\"http://purl.org/dc/elements/1.1/\""""

lom_namespace_declaration = """xmlns:lom=\"http://ltsc.ieee.org/xsd/LOM"\ xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://ltsc.ieee.org/xsd/LOM http://ltsc.ieee.org/xsd/lomv1.0/lom.xsd\""""

DC = """
<dc:dc %(namespace)s>
    <description>%(description)s</description>
    <title>%(title)s</title>
    <creator>%(creator)s</creator>
    <date>%(date)</date>
    <identifier>%(url)s</identifier>
    <type>%(type)s</type>
    <subject>%(keywords)s</subject>
</dc:dc>
"""
