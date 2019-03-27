

import re

# Removes invalid charaters for ISY Node description
def get_valid_node_name(name,max_length=14):
    offset = max_length * -1
    # Only allow utf-8 characters
    #  https://stackoverflow.com/questions/26541968/delete-every-non-utf-8-symbols-froms-string
    name = bytes(name, 'utf-8').decode('utf-8','ignore')
    # Remove <>`~!@#$%^&*(){}[]?/\;:"'` characters from name
    sname = re.sub(r"[<>`~!@#$%^&*(){}[\]?/\\;:\"']+", "", name)
    # And return last part of name of over max_length
    return sname[offset:].lower()
