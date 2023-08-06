from logilab.common.textutils import unormalize

def normalize_name(name):
    """
    Return the string in parameter:
       - in lower-case
       - replace diacritical characters with their corresponding ascii characters
       - remove leading and trailing whitespaces
       - replace other withespaces with underscores.
    """
    return unormalize(name.lower().strip()).replace(' ', '_')
