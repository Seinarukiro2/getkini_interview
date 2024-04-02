from telethon import Button
import os


async def create_email_message(event, message, view) -> None:
    """
    Create a message with inline buttons for viewing email files.

    Args:
        event: The event triggering the message creation.

    Returns:
        None
    """
    # Constructing the message
    eml_extension = "post_eml"
    if view:
        eml_extension = "view_eml"

    # Get absolute path to the 'data' directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))
    data_dir = os.path.join(parent_dir, "data")

    # Get list of eml files in the 'data' directory
    eml_files = [f for f in os.listdir(data_dir) if f.endswith(".eml")]

    # Check if there are any eml files
    if eml_files:
        # Generating inline buttons for each eml file
        buttons = []
        for eml_file in eml_files:
            # Use file name as part of the callback data
            callback_data = (
                f"{eml_extension}_{eml_file}"  # For example: 'view_eml_file1.eml'
            )
            button = Button.inline(
                eml_file[:-4], data=callback_data
            )  # Remove '.eml' extension
            buttons.append(button)

        # Create a single inline keyboard row with all buttons
        keyboard = [buttons[i : i + 1] for i in range(0, len(buttons), 1)]

        # Send the message with inline keyboard
        await event.respond(message, buttons=keyboard)
    else:
        await event.respond("No emails available.")
