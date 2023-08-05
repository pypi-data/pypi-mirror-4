import asciitomathml.asciitomathml 
the_string = 'x^2'
the_string = unicode(the_string.decode('utf8')) # adjust to your own encoding
math_obj =  asciitomathml.asciitomathml.AsciiMathML()
print(math_obj.VERSION)
math_obj.parse_string(the_string)
xml_string = math_obj.to_xml_string(encoding="utf8") # xml_string is an XML string
print(xml_string)

