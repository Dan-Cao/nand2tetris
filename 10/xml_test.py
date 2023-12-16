import xml.etree.ElementTree as ET

a = ET.Element("a")
b = ET.SubElement(a, "b")
c = ET.SubElement(a, "c", attrib={"text": "bar"})
d = ET.SubElement(c, "d")

d.text = " foo "
a.attrib["123"] = "234"

ET.indent(a)
tree = ET.tostring(a, encoding="unicode", short_empty_elements=False)
print(tree)
