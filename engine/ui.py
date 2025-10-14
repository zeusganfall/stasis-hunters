def show_toast(message, protected=False):
    """
    Displays a toast message to the user.

    Args:
        message (str): The message to display.
        protected (bool): If True, the message will indicate that the item
                          is protected in the Chronicle.
    """
    if protected:
        print(f"\n[PROTECTED IN CHRONICLE] {message}\n")
    else:
        print(f"\n[INFO] {message}\n")