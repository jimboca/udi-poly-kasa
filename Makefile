
XML_FILES = profile/*/*.xml 

# sudo apt-get install libxml2-utils libxml2-dev
check:
	echo ${XML_FILES}
	xmllint --noout ${XML_FILES}


