from tika import parser

parsed = parser.from_file('RobertResumeFall.pdf')

print(parsed['content'])    # the extracted plain text (what the ATS sees)
print(parsed['metadata'])   # author, page count, fonts, encoding, etc.