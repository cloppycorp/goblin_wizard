import sys
import os
import ctypes
import resources_rc
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QTableWidget, QApplication, QDialog, QApplication, QTableWidget
from goblin_wizard_ui import Ui_Dialog  # Import the generated UI class

# Ensure DPI awareness for Windows systems
ctypes.windll.shcore.SetProcessDpiAwareness(1)  # For DPI awareness


class MyWindow(QtWidgets.QDialog):
    def __init__(self):
        super(MyWindow, self).__init__()
        # Ensure the window has the system menu and maximize button
        #self.setWindowFlags(Qt.Window | Qt.WindowSystemMenuHint | Qt.WindowMinMaxButtonsHint)
        self.setGeometry(100, 100, 788, 631)  # Example: width=800px, height=600px
        self.ui = Ui_Dialog()  # Create an instance of the UI class
        self.ui.setupUi(self)  # Set up the UI
        self.setWindowTitle("MIDI Goblin Wizard")
        
        # Connect the save button to the save function
        self.ui.save_button.clicked.connect(self.save_goblinwizard_file)

        # Initialize the device name variable
        self.device_name = ""
        # Initialiie the remove button as disabled
        self.ui.remove_button.setEnabled(False)
        # Initialize an empty list to store the parameters
        self.parameter_list = []
        self.index_counter = 0  # This will keep track of the index number
        # Disable the create_button on startup
        self.ui.create_button.setEnabled(False)
        # Add an error label programmatically
        self.ui.error_label = QtWidgets.QLabel(self)
        # Get the geometry of the create_button (Create Folders and Files button)
        create_button_geometry = self.ui.create_button.geometry()

        # Calculate the new X position: the right edge of the button + 5 pixels
        new_x_position = create_button_geometry.x() + create_button_geometry.width() + 5

        # Use the same Y position as the create_button
        new_y_position = create_button_geometry.y()

        # Now, set the geometry of the error label based on these calculated positions
        self.ui.error_label.setGeometry(new_x_position, new_y_position, 400, 30)  # Adjust width and height as needed

        self.ui.error_label.setGeometry(330, 610, 400, 30)  # Adjust the position as needed
        self.ui.error_label.setStyleSheet("color: violet;")
        self.ui.error_label.setText("")  # Start with no error message
        # Connect the load button to the load function
        self.ui.load_button.clicked.connect(self.load_goblinwizard_file)
        # Disable all parameter-related inputs until synth_name is confirmed
        self.ui.param_type.setEnabled(False)
        self.ui.param_name.setEnabled(False)
        self.ui.param_cc_num.setEnabled(False)
        self.ui.param_msb.setEnabled(False)
        self.ui.param_lsb.setEnabled(False)
        self.ui.add_parameter.setEnabled(False)
        self.ui.parameter_table.setEnabled(False)
        self.ui.add_parameter.move(310, 290)
        # Ensure row selection instead of individual cell selection
        self.ui.parameter_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.ui.parameter_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)  # Disable editing in table
        # Disable move_up and move_down buttons initially
        self.ui.move_up_button.setEnabled(False)
        self.ui.move_down_button.setEnabled(False)

        self.ui.undo_button.setVisible(False)  # Hide the undo button
        self.ui.undo_button.setEnabled(False)  # Disable the undo button
        self.ui.undo_button.clicked.connect(self.undo_synth_name_change)  # Make sure undo is connected
        self.ui.reset_button.setEnabled(False)  # Disable the undo button
        self.ui.create_button.setEnabled(False)  # Disable the undo button

        # Populate the param_cc_num, param_msb, and param_lsb combo boxes with numbers from 0 to 127
        for i in range(128):
            self.ui.param_cc_num.addItem(str(i))
            self.ui.param_msb.addItem(str(i))
            self.ui.param_lsb.addItem(str(i))

        # Connect the text box to handle text changes (e.g., replace spaces with underscores)
        self.ui.param_name.textChanged.connect(self.handle_param_name_text_change)
        self.ui.synth_name.textChanged.connect(self.handle_synth_name_text_change)  # For synth_name

        # Connect the type drop down box
        self.ui.param_type.currentIndexChanged.connect(self.handle_param_type_change)

        # Connect the "CONFIRM" button to a function that confirms the synth_name
        self.ui.confirm_button.clicked.connect(self.confirm_synth_name)

        # Connect the "ADD" button to a function that will add the parameter to the list
        self.ui.add_parameter.clicked.connect(self.add_parameter_to_list)

        # Connect the "Remove" button to a function that removes the selected parameter
        self.ui.remove_button.clicked.connect(self.remove_parameter_from_list)

        # Connect the "Move Up" and "Move Down" buttons
        self.ui.move_up_button.clicked.connect(self.move_entry_up)
        self.ui.move_down_button.clicked.connect(self.move_entry_down)

        # Track table selection changes to enable/disable the move buttons
        self.ui.parameter_table.itemSelectionChanged.connect(self.update_move_buttons_state)

        # Track table selection changes to enable/disable the remove button
        self.ui.parameter_table.itemSelectionChanged.connect(self.update_remove_button_state)

        # Disable the remove button initially
        self.update_remove_button_state()

        # Hide param_msb and param_lsb by default (since CC is selected by default)
        self.ui.param_msb.setVisible(False)
        self.ui.param_lsb.setVisible(False)

        # Connect the reset button to this function in the __init__ method
        self.ui.reset_button.clicked.connect(self.reset_project)
        
        # Connect the create_button to this function in the __init__ method
        self.ui.create_button.clicked.connect(self.open_directory_dialog)
        # Ensure the create_button is disabled initially
        self.ui.create_button.setEnabled(False)

    # Override the resizeEvent to update the error label's position dynamically
    def resizeEvent(self, event):
        # Call the original resize event
        super().resizeEvent(event)
        
        # Get the geometry of the create_button (Create Folders and Files button)
        create_button_geometry = self.ui.create_button.geometry()

        # Calculate the new X position: right edge of the button + 5 pixels
        new_x_position = create_button_geometry.x() + create_button_geometry.width() + 5

        # Use the same Y position as the create_button
        new_y_position = create_button_geometry.y()

        # Now, set the geometry of the error label based on these calculated positions
        self.ui.error_label.setGeometry(new_x_position, new_y_position, 400, 30)  # Adjust width and height as needed

    def adjust_size_for_screen(self):
        screen = app.primaryScreen()
        dpi = screen.logicalDotsPerInch()
        
        # Adjust the size of the window based on the DPI scaling
        if dpi > 96:  # Assume 96 DPI is "normal"
            scale_factor = dpi / 96.0
            self.resize(int(self.width() * scale_factor), int(self.height() * scale_factor))

    def save_goblinwizard_file(self):
        # Open a file dialog to save the .goblinwizard file
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, 
                                               "Save .goblinwizard File",
                                               "",  # Initial directory
                                               "Goblin Wizard Files (*.goblinwizard);;All Files (*)",
                                               options=options)
        if file_path:
            # Ensure the file has the .goblinwizard extension
            if not file_path.endswith(".goblinwizard"):
                file_path += ".goblinwizard"

            # Start writing the file
            with open(file_path, 'w') as file:
                # Write the device name at the top
                file.write(f"device name: {self.device_name}\n")

                # Write the contents of the parameter list
                for row, entry in enumerate(self.parameter_list):
                    # Write the entry's index number first, followed by where it's displayed in the table (row)
                    file.write(f"{entry['index']} {row} {entry['type']} {entry['name']} {entry['cc']} {entry['msb']} {entry['lsb']}\n")

            print(f"File saved: {file_path}")

    def load_goblinwizard_file(self):
        # Check if a project is already in progress (device_name set and parameter list not empty)
        if self.device_name and len(self.parameter_list) > 0:
        # Show warning dialog
            confirm_load = QMessageBox(self)
            confirm_load.setWindowTitle("Warning")
            confirm_load.setText("Warning, loading project will erase all changes to current project. Are you sure you want to load a project?")
            confirm_load.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
            confirm_load.setDefaultButton(QMessageBox.Cancel)

            # If the user cancels, just close the dialog
            if confirm_load.exec_() == QMessageBox.Cancel:
                return

        # Open the file explorer for .goblinwizard files
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, 
                                                "Open .goblinwizard File",
                                                "",  # Initial directory
                                                "Goblin Wizard Files (*.goblinwizard);;All Files (*)",
                                                options=options)
        if file_path:
            # Clear the current device name and parameter list
            self.device_name = ""
            self.parameter_list.clear()
            self.ui.parameter_table.setRowCount(0)
            self.ui.synth_name.clear()

            # Parse the .goblinwizard file
            try:
                with open(file_path, 'r') as file:
                    lines = file.readlines()

                    # First line contains the device name
                    if lines and lines[0].startswith("device name:"):
                        self.device_name = lines[0].split(":")[1].strip()
                        self.ui.synth_name.setText(self.device_name)

                    # Remaining lines are the parameter entries
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) == 7:
                            # Extract values from the line (index, row order, type, name, cc, msb, lsb)
                            param_list_index = int(parts[0])
                            param_table_index = int(parts[1])
                            param_type_value = parts[2]
                            param_name_value = parts[3]
                            param_cc_value = int(parts[4])
                            param_msb_value = int(parts[5])
                            param_lsb_value = int(parts[6])

                            # Create an entry in the parameter list
                            parameter_entry = {
                                "index": param_list_index,
                                "type": param_type_value,
                                "name": param_name_value,
                                "cc": param_cc_value,
                                "msb": param_msb_value,
                                "lsb": param_lsb_value
                            }

                            # Insert the entry into the parameter list at the correct order
                            self.parameter_list.append(parameter_entry)
                            self.update_table()

            except Exception as e:
                print(f"Error loading file: {e}")
                QMessageBox.warning(self, "Error", "Failed to load the file.")
            self.ui.reset_button.setEnabled(True)  # Disable the undo button    
            self.ui.parameter_table.clearSelection()
            self.ui.create_button.setEnabled(True)
            self.ui.param_type.setEnabled(True)
            self.ui.param_name.setEnabled(True)
            self.ui.param_cc_num.setEnabled(True)
            self.ui.param_msb.setEnabled(True)
            self.ui.param_lsb.setEnabled(True)
            self.ui.add_parameter.setEnabled(True)
            self.ui.parameter_table.setEnabled(True)
            self.update_save_button()

    def update_create_button_state(self):
        # Check if the synth name is defined and there is at least one entry in the list
        if self.device_name and len(self.parameter_list) > 0:
            self.ui.create_button.setEnabled(True)
        else:
            self.ui.create_button.setEnabled(False)

    def open_directory_dialog(self):

        # Create a directory dialog that only allows selecting directories
        directory_dialog = QFileDialog(self, "Select Directory")
        directory_dialog.setFileMode(QFileDialog.Directory)
        directory_dialog.setOption(QFileDialog.ShowDirsOnly, True)

        # Hide the "New Folder" button by disabling the creation of directories
        directory_dialog.setOption(QFileDialog.DontUseNativeDialog, True)

        # Execute the dialog and get the selected directory (if "OKAY" is pressed)
        if directory_dialog.exec_() == QFileDialog.Accepted:
            selected_directory = directory_dialog.selectedFiles()[0]  # Get the selected directory
            print(f"Selected directory: {selected_directory}")

            # Get the synth name (device_name)
            synth_name = self.device_name

            if not synth_name:
                self.ui.error_label.setText("No synth name has been provided!")
                return  # Prevent folder creation without a synth name

            # Create the full path for the new folder
            new_folder_path = os.path.join(selected_directory, synth_name)

        try:
            # Create the main directory
            os.makedirs(new_folder_path)
            print(f"Folder '{synth_name}' created at: {new_folder_path}")

            # Create the subfolders
            patches_folder = os.path.join(new_folder_path, "PATCHES")
            remaps_folder = os.path.join(new_folder_path, "REMAPS")
            config_folder = os.path.join(new_folder_path, "CONFIG")
            os.makedirs(patches_folder)
            os.makedirs(remaps_folder)
            os.makedirs(config_folder)

            print(f"Subfolders 'PATCHES', 'REMAPS', 'CONFIG' created.")

            # Create and open the MIDI_INFO.txt file in the PATCHES folder
            midi_info_path = os.path.join(config_folder, "MIDI_INFO.txt")
            with open(midi_info_path, "w") as midi_info_file:
                # Loop through the parameter list and print the values in the correct format
                for entry in self.parameter_list:
                    if entry["type"] == "CC":
                        # For CC entries, print "name cc_value"
                        midi_info_file.write(f"CC {entry['name']} {entry['cc']}\n")
                    elif entry["type"] == "NRPN":
                        # For NRPN entries, print "NRPN msb_value lsb_value"
                        midi_info_file.write(f"NRPN {entry['name']} {entry['msb']} {entry['lsb']}\n")

            print(f"MIDI_INFO.txt created at: {midi_info_path}")
            self.ui.error_label.setText(f"Folder structure and MIDI_INFO.txt created successfully.")
        except FileExistsError:
            # Handle the case where the folder already exists
            self.ui.error_label.setText(f"Folder '{synth_name}' already exists.")
        except Exception as e:
            # Handle any other errors
            self.ui.error_label.setText(f"Error: {str(e)}")

    def reset_project(self):
        # First confirmation dialog
        confirm_reset = QtWidgets.QMessageBox(self)
        confirm_reset.setWindowTitle("Confirm Reset")
        confirm_reset.setText("Do you want to reset this project? All of your entries and synth name will be erased!")
        confirm_reset.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        confirm_reset.setDefaultButton(QtWidgets.QMessageBox.No)

        # Check the response
        if confirm_reset.exec_() == QtWidgets.QMessageBox.Yes:
            # Second confirmation dialog
            second_confirm_reset = QtWidgets.QMessageBox(self)
            second_confirm_reset.setWindowTitle("Are you sure?")
            second_confirm_reset.setText("Are you sure?")
            second_confirm_reset.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            second_confirm_reset.setDefaultButton(QtWidgets.QMessageBox.No)

            # If the user confirms the second dialog
            if second_confirm_reset.exec_() == QtWidgets.QMessageBox.Yes:
                # Clear all entries in the list
                self.parameter_list.clear()
                self.update_table()

                # Clear the synth_name field
                self.ui.synth_name.clear()
                self.device_name = ""

                # Reset the dropdowns
                self.ui.param_type.setCurrentIndex(0)  # Set to 'CC'
                self.ui.param_cc_num.setCurrentIndex(0)  # Set to 0
                self.ui.param_msb.setCurrentIndex(0)  # Set to 0
                self.ui.param_lsb.setCurrentIndex(0)  # Set to 0

                # Reset UI elements back to initial state (disabled)
                self.ui.param_type.setEnabled(False)
                self.ui.param_name.setEnabled(False)
                self.ui.param_cc_num.setEnabled(False)
                self.ui.param_msb.setEnabled(False)
                self.ui.param_lsb.setEnabled(False)
                self.ui.add_parameter.setEnabled(False)
                self.ui.parameter_table.setEnabled(False)
                self.ui.reset_button.setEnabled(False)  # Disable the undo button
                self.ui.create_button.setEnabled(False)  # Disable the undo button
                # Reset the parameter name text box
                self.ui.param_name.setText("")  # Clear the parameter name input field
                self.ui.undo_button.setVisible(False)     # Hide the undo button
                self.ui.undo_button.setEnabled(False)     # Disable the undo button
                self.ui.confirm_button.setText("CONFIRM")  # Change the confirm button text to "Change"
                self.update_save_button()


    def handle_param_name_text_change(self, text):
        # Replace spaces with underscores
        updated_text = text.upper().replace(" ", "_")

        # Limit the text to 14 characters
        if len(updated_text) > 14:
            updated_text = updated_text[:14]

        # Only keep valid characters: letters, numbers, underscores, and dashes
        valid_text = ''.join(char for char in updated_text if char.isalnum() or char in "_-")

        # If there's a difference between the original and valid text, replace it in the text box
        if valid_text != updated_text:
            self.ui.param_name.setText(valid_text)
        
        # Clear any error message
        self.ui.error_label.setText("")

    def handle_synth_name_text_change(self, text):
        # Replace spaces with underscores
        updated_text = text.upper().replace(" ", "_")

        # Only keep valid characters: letters, numbers, underscores, and dashes
        valid_text = ''.join(char for char in updated_text if char.isalnum() or char in "_-")

        # Limit the valid text to 20 characters
        if len(valid_text) > 20:
            valid_text = valid_text[:20]

        # If there's a difference between the original and valid text, replace it in the text box
        if valid_text != self.ui.synth_name.text():
            self.ui.synth_name.setText(valid_text)
        
        # Clear any error message
        self.ui.error_label.setText("")

        # Check if the current synth name matches the confirmed device_name
        if self.device_name:  # Only perform change/undo behavior if device_name has already been confirmed
            if valid_text != self.device_name:
                # If the name has changed, disable the create button, change confirm button text, and show the undo button
                self.ui.create_button.setEnabled(False)
                self.ui.confirm_button.setText("Change")
                self.ui.undo_button.setVisible(True)
                self.ui.undo_button.setEnabled(True)
            else:
                # If the text matches the confirmed device_name, revert the buttons
                self.ui.confirm_button.setText("Confirm")
                self.ui.undo_button.setVisible(False)
                self.ui.undo_button.setEnabled(False)
                self.ui.create_button.setEnabled(True)

    def confirm_synth_name(self):
        # Get the value from synth_name and store it in device_name
        new_device_name = self.ui.synth_name.text()

        # Check if the device_name is valid (not empty and matches naming rules)
        if not new_device_name:
            self.ui.error_label.setText("Device name cannot be empty!")
            return

        # Update the device_name to the new value and store it
        self.device_name = new_device_name

        # If this is the first confirmation, keep the confirm button text as "Confirm"
        if self.ui.confirm_button.text() == "Confirm":
            self.original_device_name = self.device_name  # Store the confirmed name for potential undo later
        else:
            # If the confirm button was showing "Change", revert it to "Confirm"
            self.ui.confirm_button.setText("Confirm")

        # Hide and disable the undo button now that the changes are confirmed
        self.ui.undo_button.setVisible(False)
        self.ui.undo_button.setEnabled(False)

        # Enable all other inputs now that the device name is confirmed
        self.ui.param_type.setEnabled(True)
        self.ui.param_name.setEnabled(True)
        self.ui.param_cc_num.setEnabled(True)
        self.ui.param_msb.setEnabled(True)
        self.ui.param_lsb.setEnabled(True)
        self.ui.add_parameter.setEnabled(True)
        self.ui.parameter_table.setEnabled(True)

        # Clear any error message
        self.ui.error_label.setText("")

        # Re-enable the "Create Synth Folders and Files" button if the criteria are met
        self.update_create_button_state()
        self.ui.reset_button.setEnabled(True)  # Disable the undo button

    def undo_synth_name_change(self):
        # Revert the synth_name text to the previously confirmed device name
        self.ui.synth_name.setText(self.device_name)  # Use self.device_name, which stores the last confirmed value
        self.ui.undo_button.setVisible(False)  # Hide the undo button
        self.ui.confirm_button.setText("Confirm")  # Set the confirm button text back to "Confirm"
        self.ui.create_button.setEnabled(True)  # Enable the create button if there are parameters in the list
        self.update_create_button_state()

    def update_remove_button_state(self):
        # Enable the remove button only if an item is selected and there are rows in the table
        if self.ui.parameter_table.selectionModel().hasSelection() and len(self.parameter_list) > 0:
            self.ui.remove_button.setEnabled(True)
        else:
            self.ui.remove_button.setEnabled(False)

    def update_move_buttons_state(self):
        # Get the currently selected row
        selected_row = self.ui.parameter_table.currentRow()

        # If no row is selected, disable both buttons
        if selected_row == -1:
            self.ui.move_up_button.setEnabled(False)
            self.ui.move_down_button.setEnabled(False)
            return

        # If fewer than 2 entries exist, disable both buttons
        if len(self.parameter_list) < 2:
            self.ui.move_up_button.setEnabled(False)
            self.ui.move_down_button.setEnabled(False)
        else:
            # Enable/Disable the move up button (only enabled if not the first row)
            if selected_row > 0:
                self.ui.move_up_button.setEnabled(True)
            else:
                self.ui.move_up_button.setEnabled(False)

            # Enable/Disable the move down button (only enabled if not the last row)
            if selected_row < len(self.parameter_list) - 1:
                self.ui.move_down_button.setEnabled(True)
            else:
                self.ui.move_down_button.setEnabled(False)


    def handle_param_type_change(self):
        # Get the current value of the param_type combo box
        param_type_value = self.ui.param_type.currentText()

        if param_type_value == "CC":
            # Move the add button to (310, 70) if "CC" is selected
            self.ui.add_parameter.move(310, 290)

            # Show param_cc_num and hide param_msb and param_lsb
            self.ui.param_cc_num.setVisible(True)
            self.ui.param_msb.setVisible(False)
            self.ui.param_lsb.setVisible(False)

            # Reset param_msb and param_lsb to 0
            self.ui.param_msb.setCurrentIndex(0)
            self.ui.param_lsb.setCurrentIndex(0)

        elif param_type_value == "NRPN":
            # Move the add button to (400, 70) if "NRPN" is selected
            self.ui.add_parameter.move(400, 290)

            # Show param_msb and param_lsb, hide param_cc_num
            self.ui.param_cc_num.setVisible(False)
            self.ui.param_msb.setVisible(True)
            self.ui.param_lsb.setVisible(True)

            # Reset param_cc_num to 0
            self.ui.param_cc_num.setCurrentIndex(0)

    def add_parameter_to_list(self):
        # Clear any previous error messages
        self.ui.error_label.setText("")
        
        # Get the current values from the form
        param_type_value = self.ui.param_type.currentText()
        param_name_value = self.ui.param_name.text()
        param_cc_value = int(self.ui.param_cc_num.currentText()) if param_type_value == "CC" else 255
        param_msb_value = int(self.ui.param_msb.currentText()) if param_type_value == "NRPN" else 255
        param_lsb_value = int(self.ui.param_lsb.currentText()) if param_type_value == "NRPN" else 255

        #Rule 1: check to make sure theyve entered a name
        if not param_name_value:
            self.ui.error_label.setText("Parameter name cannot be empty!")
            return
        # Rule 2: Check if the parameter name already exists in the list
        if any(entry["name"] == param_name_value for entry in self.parameter_list):
            self.ui.error_label.setText("name already being used!")
            return  # Prevent adding the entry

        # Rule 3: Check if the CC number is already being used (for CC only)
        if param_type_value == "CC" and any(entry["cc"] == param_cc_value for entry in self.parameter_list):
            self.ui.error_label.setText("CC number already being used!")
            return  # Prevent adding the entry

        # Rule 4: Check if the MSB and LSB combination already exists (for NRPN only)
        if param_type_value == "NRPN" and any(entry["msb"] == param_msb_value and entry["lsb"] == param_lsb_value for entry in self.parameter_list):
            self.ui.error_label.setText(f"msb: {param_msb_value} and lsb: {param_lsb_value} already being used!")
            return  # Prevent adding the entry

        # If all validation passes, add the entry to the list
        parameter_entry = {
            "index": self.index_counter,
            "type": param_type_value,
            "name": param_name_value,
            "cc": param_cc_value,
            "msb": param_msb_value,
            "lsb": param_lsb_value
        }

        # Add the entry to the list
        self.parameter_list.append(parameter_entry)
        self.index_counter += 1  # Increment the index for the next entry

        # Reset the parameter name text box
        self.ui.param_name.setText("")  # Clear the parameter name input field

        # Update the table with the new entry
        self.update_table()
        self.update_save_button()
        # Update the state of the create button
        self.update_create_button_state()
        # Disable the create_button on startup
 

    def remove_parameter_from_list(self):
        # Get the selected row
        selected_row = self.ui.parameter_table.currentRow()

        if selected_row >= 0:  # If a valid row is selected
            # Remove the entry from the list
            del self.parameter_list[selected_row]

            # Update the table after removing the entry
            self.update_table()

            # Update the state of the create button
            self.update_create_button_state()
            self.update_save_button()
            self.ui.parameter_table.clearSelection()

    def update_save_button(self):
         # Check if a parameter has been successfully added to the list
        if self.device_name and len(self.parameter_list) > 0:
            self.ui.save_button.setEnabled(True)
        else:
            self.ui.save_button.setEnabled(False)       

    def move_entry_up(self):
        # Get the selected row
        selected_row = self.ui.parameter_table.currentRow()

        if selected_row > 0:
            # Swap the selected entry with the one above it
            self.parameter_list[selected_row], self.parameter_list[selected_row - 1] = (
                self.parameter_list[selected_row - 1],
                self.parameter_list[selected_row],
            )

            # Update the table
            self.update_table()

            # Select the moved entry
            self.ui.parameter_table.selectRow(selected_row - 1)

    def move_entry_down(self):
        # Get the selected row
        selected_row = self.ui.parameter_table.currentRow()

        if selected_row < len(self.parameter_list) - 1:
            # Swap the selected entry with the one below it
            self.parameter_list[selected_row], self.parameter_list[selected_row + 1] = (
                self.parameter_list[selected_row + 1],
                self.parameter_list[selected_row],
            )

            # Update the table
            self.update_table()

            # Select the moved entry
            self.ui.parameter_table.selectRow(selected_row + 1)

    def update_table(self):
        # Clear the table first
        self.ui.parameter_table.setRowCount(0)

        # Add each entry from parameter_list to the table
        for entry in self.parameter_list:
            row_position = self.ui.parameter_table.rowCount()
            self.ui.parameter_table.insertRow(row_position)

            self.ui.parameter_table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(entry["type"]))
            self.ui.parameter_table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(entry["name"]))
            self.ui.parameter_table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(entry["cc"]) if entry["cc"] != 255 else "--"))
            self.ui.parameter_table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(str(entry["msb"]) if entry["msb"] != 255 else "--"))
            self.ui.parameter_table.setItem(row_position, 4, QtWidgets.QTableWidgetItem(str(entry["lsb"]) if entry["lsb"] != 255 else "--"))

        # Update move and remove button state after updating the table
        self.update_remove_button_state()
        self.update_move_buttons_state()

# Run the application
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)  # Enable High DPI scaling
    # Enable high DPI scaling before QApplication is created
    QtWidgets.QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Now create the application
    app = QtWidgets.QApplication(sys.argv)

    # Create and show the main window
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
