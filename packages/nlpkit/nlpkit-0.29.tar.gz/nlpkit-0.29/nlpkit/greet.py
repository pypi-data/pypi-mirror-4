def hello(first="Dave", second=""):
    """Returns personalized greeting with specified first and second
    names.
    
    Named Arguments:
    first -- First name (default="Dave")
    second -- Second name (defualt="")

    Return: Personalized greeting
    """
    return ("Hello, " + first + " " + second).strip() + "."

def goodbye():
    """Returns goodbye message.

    Named Arguments: None
    Return: Goodbye message.
    """
    return "Goodbye."
