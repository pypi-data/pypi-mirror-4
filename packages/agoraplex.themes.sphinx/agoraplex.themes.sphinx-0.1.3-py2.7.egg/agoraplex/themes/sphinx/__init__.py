import os

def get_html_theme_path ():
    """
    Return a list of HTML theme paths
    """
    return [os.path.abspath(os.path.dirname(__file__))]
