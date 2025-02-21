from ro_functions.roblox_api_searches import get_ro_username, search_badges, create_output_file, replace_env, get_badge_name
from dotenv import load_dotenv
from os import environ, path
import io
import requests

'''
Finds and does some ugly procedures to strip the "'s" from the end of the user whose friends list is being checked for alts
@param mode: Decides how the function treats the input data. changes how it handles the line based off which mode the program is run in
@param main_user_line: Takes the line (using .readline) that the main username is on
@return: Returns the string of the main user's username.
'''
def strip_main_username(mode, main_user_line):

    if mode == "badge":
        return main_user_line.split()[2]
    else:
        main_username = main_user_line.split()[0].split("'") # Takes the given line, splits it, takes the first word, then splits that word with ' as the delimiter, essentially separating the main username from the s at the end.
        return main_username[0]

'''
Checks whether a username only includes I's and L's (barcode name).
@param username: The username to be checked.
@return: Returns a boolean representing whether the name only contains I's and L's. True if it only contains I's and L's, False if not.
'''
def check_barcode(username):
    
    char_list = ["a", "b", "c", "d", "e", "f", "g", "h", "j", "k", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]

    for char in char_list:
        
        if char in username:
            return False
    
    return True

'''
Runs a few checks on a given user, comparing them to the 'main account'.
@param mode: Takes the mode the user selected and doesn't check some criteria if it is the 'badge' mode
@param main_user: The 'main account' mentioned above. This is always the person whose friends list was checked using friend_check.py
@param compared_user_id: Takes the user_id of the secondary user so as to reduce the amount of calls made to the Roblox api. The ID is needed to get the badge count.
@return: Returns a tuple of the status and exit messages. The status represents if the user is a suspected alt. The exit messages describe why they're suspected as an alt (one or more of the above reasons)
'''
def compare_username(mode, main_user, compared_user_id):
    
    # Initializes a few useful variables
    status = False
    exit_messages = []
    compared_username = get_ro_username(compared_user_id).lower()

    # Counts the amount  of badges the given user has
    badge_req = requests.get(f"https://badges.roblox.com/v1/users/{compared_user_id}/badges", params={"limit": 100})
    badge_count = len(badge_req.json()["data"])

    # Checks a few criteria that could qualify them as an alt and flags them if they meet those criteria
    if main_user.strip("1234567890").lower() in compared_username and mode != "badge": # Doesn't check if the main username is the same as the compared username if using the badge mode. Doesn't make sense to use this criteria based off what the badge_checker does

        status = True
        exit_messages.append("Main username found in username.")

    if "alt" in compared_username: # Checks if the user has 'alt' in their username
        status = True
        exit_messages.append("'Alt' found in username.")
    
    if badge_count < 10: # Checks the user's badge count and flags them if its low
        status = True
        exit_messages.append("User does not have many badges.")

    if compared_username.isdigit(): # Check if the user has only numbers in their username
        status = True
        exit_messages.append("User's username is only numbers.")

    if check_barcode(compared_username): # Checks if the user has a barcode username (only I's and L's) These are used to make it harder to find / ban alt accounts as capital I's and lowercase l's are hard to distinguish
        status = True
        exit_messages.append("Barcode username (only I's and L's).")

    return status, exit_messages

'''
The main work of the program. Checks the friend_search_result.txt file for potential alts, using common alt terms (alt, *name*2, etc)
@param mode: FINISH ME
@param badge_id: Takes the ID of the badge that is being searched for. Retrieved from the .env file.
@return: Returns none as its output is printed to a file that is created in the function
'''
def alt_detector(mode, requested_badge_id):
    

    out_file = create_output_file("alt_name_detection_result.txt") # Setup the output file

    # Sets vital info based off what mode was selected
    if mode == "friend":
        file_to_search = "friend_search_result.txt"
        id_location, name_location = 1, 0

    else:
        file_to_search = "badge_results.txt"
        id_location, name_location = 0, 1


    try: # Handles any errors arising from the file not existing or being misplaced (user moved the file or renamed it)
        friend_list = open(f"{path.dirname(__file__)}/output_files/{file_to_search}", "r")

    except FileNotFoundError:
        print("File does not exist or is misplaced. Please generate the selected file before using this program.")


    friend_list.readline() # Skips a line to get to the main user line in the file
    main_user = strip_main_username(mode, friend_list.readline()) # Reads in and gets the username of the user whose friends list is being checked

    out_file.write(f"\nMain Account: {main_user}\n\n") # Writes some extra info for logging and aesthetic purposes
    out_file.write("Potential alts:\n")

    for line in friend_list:

        if line[0] == "\n": # If the line is a new-line character, it can be skipped safely
            continue
        
        elif line[0] == "U" and mode == "badge": # Skips the line if the selected mode is badge and the first character is U, this skips all lines that state whether a user has a badge or not which are exclusively found in the badge_results.txt file
            continue

        else: # Splits the line into a list of words in the line and compares the username on the line to the main friend's username

            line_words = line.split()

            alt_status, reason_list = compare_username(mode, main_user, line_words[id_location].strip("()")) # Compares the two usernames (main account + account from friends list)
            
            if alt_status: # Prints the reasons that the friend account was detected as an alt

                out_file.write(f"\n{line_words[name_location].strip("()")} ({line_words[id_location].strip("()")}) is potentially an alt.")                
                out_file.write(" \nReason(s):\n")
                reason_count = 1
                
                for reason in reason_list: #Iterates through the reasons and prints them with appropriate numbering

                    out_file.write(f"{reason_count}.) {reason}\n")
                    reason_count += 1
                
                if search_badges(line_words[id_location].strip("()") ,requested_badge_id): # Checks if the user has the requested badge (this info is recorded in the separate files but for ease of use, its recorded here too.)
                    out_file.write(f"* User has the {get_badge_name(requested_badge_id)} badge.\n")

                else:
                    out_file.write(f"* User does not have the {get_badge_name(requested_badge_id)} badge.\n")
    

    print("Done!") # Wrap up the function
    out_file.close()
    return None


def main():
    
    #Sets up some valuable variables
    load_dotenv()
    valid_selected_mode = False
    selected_mode = ""

    while not valid_selected_mode: # Loops execution until a valid mode is selected or execution is stopped.

        selected_mode = input("Please select which alt detection mode to use. \nEnter 'friend' to search the friend_search_result.txt file, or enter 'badge' to search the badge_results.txt file.\n\nEnter 'exit' to end the program. \n\n")
        selected_mode = selected_mode.lower()

        if selected_mode == "friend": # Selects 'friend' mode which checks the 'friend_search_result.txt' file for potential alts.
            valid_selected_mode = True

        elif selected_mode == "badge": # Selects 'badge' mode which checks the 'badge_results.txt' file for potential alts.
            valid_selected_mode = True

        elif selected_mode == "exit": # Stops execution.
            print("Closing...")
            return
        
        else:
            print(f"\nInvalid mode. Please try again. ({selected_mode} is not an available mode)\n")
    
    print("\nValid mode selected. Checking...\n")

    try:
        alt_detector(selected_mode, environ["BADGE_ID"])

    except KeyError:
        replace_env()

    except Exception as e: # Prints errors. More than likely won't happen but its there for safety
        print(f"Error: {e}.")

    return

if __name__ == "__main__":
    main()
