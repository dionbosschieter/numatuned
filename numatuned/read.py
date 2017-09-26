def read(path_to_file):
    """
    Open the file, read it, and close the file.
    """
    with open(path_to_file, mode='r') as f:
        return f.read()
