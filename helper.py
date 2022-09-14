###############################################################################
# Functions
###############################################################################
def replace_address(str_src, l_address_replace):
    for address_replace in l_address_replace:
        str_src = str_src.replace(address_replace[0], address_replace[1])
    return str_src

def delete_clinic(str_src, l_clin_delete):
    for clin_delete in l_clin_delete:
        str_src = str_src.replace(clin_delete, '')
    return str_src