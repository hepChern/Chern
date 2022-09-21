

def output_file_exists(output_file):
    if (not csys.exists(output_file)):
        return False
    return True