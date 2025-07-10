
from time import sleep
import requests
import io
from os import path, makedirs
from dotenv import dotenv_values

'''
Searches for users on Roblox using the supplied keyword
@arg username_keyword: The keyword to be used to search for users
@arg id_list: Takes a list to which the function will add the IDs it receieves from the API
@arg next_page_cursor: If supplied, this will change the page that the API supplies when requested. should never be used but is there for extremely large searches
@return: Returns None as the main work the function is doing is adding IDs and names to the given lists '''
def search_user(username_keyword, id_list, next_page_cursor=""):
    
    parameters = {"keyword": username_keyword, "cursor": next_page_cursor, "limit": 100}
    response = requests.get("https://users.roblox.com/v1/users/search", params=parameters)


    if response.status_code == 429: # Checks if we recieved the too many requests error and enters a loop to retry data acquisition if we did

        while response.status_code == 429:

            print("Too many requests, waiting and trying again.")
            sleep(10.0)
            response = requests.get("https://users.roblox.com/v1/users/search", params=parameters)

    if response.status_code == 200: # Good status code, if we recieve a 200 then we can begin collecting IDs

        user_list = response.json()["data"]

        for user in user_list: # Appends the id and name of the user given by the API
            id_list.append(user["id"])

    else: # Shouldn't happen but catches either of the two other error codes we can get
        print(f"Error: {response.status_code}")
        return None
    
    if response.json()["nextPageCursor"] != None: # Checks to see if there are more pages of results and recursively checks the pages if they exist
        search_user(username_keyword, id_list, response.json()["nextPageCursor"])

    return None


'''
Recursively searches a given user's badge list for the given badge using their ids
@arg user_id: The ID of the user is being checked
@arg badge_id: The ID of the badge the user is being checked for
@return: Returns a bool representative of if the user has the badge, returns None if there was an error '''
def search_badges(user_id, badge_id):

    sleep(0.5) # Delay used to not overload the Roblox API
    
    response = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges/{badge_id}/awarded-date")

    if response.status_code == 200: # Positive response code
        return True

    elif response.status_code == 204: # Negative response code
        return False

    elif response.status_code == 429: # Too many requests response code, can be ignored as it has no effect for us
        pass

    elif response.status_code == 404: # Bad user ID response code
        print("Invalid user / User does not exist.")
        return False

'''
Searches and lists all of a user's friends
@arg username_keyword: The id of the user whose friends list is being checked
@arg mode: Sets the mode of what is being searched, friends or followers (and maybe following in the future)
@arg next_page: Defaults to none but if supplied, means the next page of results should be accessed (if the user is following a lot of people)
@arg user_id_list: Takes a list of user_ids (usually from previous iterations of the function) for the cases of recursion. If there is no previous iteration of the function, a new list is made.
@return: Returns a list which contains the IDs of all the requested user's friends '''
def search_others(user_id, mode, next_page=None, user_id_list=None):

    recurse = False # Set up a variable for later

    # Determines what call is made to the API based off what option the user selected when calling the function
    if mode == "friend": # Calls Roblox's friends API call
        response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends")
    
    elif mode == "follower": # Calls Roblox's followers API call
        response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/followers", params={"limit": 25, "cursor": next_page})

        if response.json()["nextPageCursor"] != None: # If there are more than one page of followers, sets the function up for recursion
            next_page_value = response.json()["nextPageCursor"]
            recurse = True

    if user_id_list == None: # If there is no supplied list for IDs to be added to, makes a new empty list. Primarily useful for recursion
        user_id_list = []

    if response.status_code == 200: # OK status code, allows us to move forward

        others_list = response.json()["data"]

        for user in others_list: # Iterate through all the friends, adding the ID to the ID list

                user_id_list.append(user["id"])

    else:
        print("Requested user does not exist.")

    if recurse: # If there are more pages to check (in the case of searching followers), recursively checks all pages
        search_others(user_id, mode, next_page_value, user_id_list)

    return user_id_list

'''
Gets and returns the Roblox username of a user given their user ID. Mostly used to convert user IDs into more readable usernames
@arg user_id: The user ID of the account to get the name of
@return: Returns a string of the user's username or None if there was an error
'''
def get_ro_username(user_id):
    
    response = requests.get(f"https://users.roblox.com/v1/users/{user_id}")

    if response.status_code == 200: #OK status code
        return response.json()["name"]
    else:
        return None
    
'''
Gets and returns the name of a given Roblox badge.
@param badge_id: The ID of the desired badge.
@return: Returns a string of the badge's ID.
'''
def get_badge_name(badge_id):

    badge_name_request = requests.get(f"https://badges.roblox.com/v1/badges/{badge_id}") # Gets the name of the badge to be logged in output

    if badge_name_request.status_code == 404:
        print("Invalid badge ID entered.")
        raise Exception("InvalidID")
    
    else:
        return badge_name_request.json()["name"]
    
'''
Gets and returns the date a given badge was acquired
@param user_id: The ID of the user whose badge data is being acquired
@param badge_id: ID of the desired badge
@return: Returns a list consisting of the year, month, day, and time the badge was earned
'''
def get_badge_date(user_id, badge_id):
    
    badge_request = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges/{badge_id}/awarded-date").json()["awardedDate"]

    time_list = badge_request[0:10].split("-")

    time_list.append(badge_request[11:16])

    return time_list

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
@return: Returns a tuple of the status and exit messages. The status represents if the user is a suspected alt. The exit messages describe why they're suspected as an alt (one or more of the above reasons).
'''
def compare_username(mode, main_user, compared_user_id):
    
    # Initializes a few useful variables
    status = False
    exit_messages = []
    compared_username = get_ro_username(compared_user_id).lower()
    main_username = get_ro_username(main_user)
    env_badge = dotenv_values(f"{path.dirname(path.dirname(__file__))}/.env")["BADGE_ID"] # This is the ID of the badge held in the .env file, used to rule out some false positives

    # Counts the amount  of badges the given user has
    badge_req = requests.get(f"https://badges.roblox.com/v1/users/{compared_user_id}/badges", params={"limit": 100})

    if badge_req.status_code == 404: # If the request errors, returns a tuple of Nones. Request usually errors because an account no longer exists.
        return None, None
    
    else:
        badge_count = len(badge_req.json()["data"])

    # Checks a few criteria that could qualify them as an alt and flags them if they meet those criteria
    if main_username.strip("1234567890").lower() in compared_username and mode != "badge": # Doesn't check if the main username is the same as the compared username if using the badge mode. Doesn't make sense to use this criteria based off what the badge_checker does

        status = True
        exit_messages.append("Main username found in username.")

    if "alt" in compared_username: # Checks if the user has 'alt' in their username
        status = True
        exit_messages.append("'Alt' found in username.")
    
    if badge_count < 10: # Checks the user's badge count and flags them if its low
        if badge_count == 0 and search_badges(main_user, env_badge): # Rules out fairly common false positives since the Roblox API won't give someone's badge list if they have certain privacy settings
            pass

        else:
            status = True
            exit_messages.append("User does not have many badges. (Be aware, this can be a false positive due to privacy settings.)")

    if compared_username.isdigit(): # Check if the user has only numbers in their username
        status = True
        exit_messages.append("User's username is only numbers.")

    if check_barcode(compared_username): # Checks if the user has a barcode username (only I's and L's) These are used to make it harder to find / ban alt accounts as capital I's and lowercase l's are hard to distinguish
        status = True
        exit_messages.append("Barcode username (only I's and L's).")

    return status, exit_messages

'''
Creates an output file in the output_files directory
@arg file_name: A string of the name of the file to create
@return: returns a file object that can be written to
'''
def create_output_file(file_name):
   
    if path.basename(path.dirname(__file__)) == "ro_functions": # Checks the current directory and sets the correct name
        dir_name = path.dirname(path.dirname(__file__))
    else:
        dir_name = path.dirname(__file__)

    makedirs(f"{dir_name}/output_files", exist_ok=True) # Creates the output_files directory if it doesn't exist
    file_loc = f"{dir_name}/output_files/{file_name}" # Sets the file location as output files with the file name at the end

    return open(file_loc, "w")

'''
Creates and fills a new .env file
@return: Returns none as its main work is creating a filling a file
'''
def replace_env():

    print(".env file not detected. Replacement file created. Please enter the ID of the badge you wish to search for.")

    with open(f"{path.dirname(path.dirname(__file__))}/.env", "w") as replacement:

        replacement.write("# Fill in badge ID below.\n")
        replacement.write("BADGE_ID=")
        print("\nPlease enter the ID of the badge you'd like to search users for.")

        new_id = input()

        while not validate_badge(new_id):

            print("\nInvalid badge ID input. Please input a valid badge ID.")
            new_id = input()

        replacement.write(new_id)
        print() # Whitespace
        replacement.close()

    return None

'''
Checks if the .env file exists and replaces it if it does not exist
@return: Returns none as its main work is checking and potentially replacing the .env file
'''
def check_env():
    
    if not path.isfile(f"{path.dirname(path.dirname(__file__))}/.env"):
        replace_env()

    return None

'''
Takes a int representing a new badge ID and overwrites the old badge ID held in the .env file
@param new_id: The new badge ID to be placed into the .env file
@return: Returns None as its work is modifying a file
'''
def modify_env(new_id):

    with open(f"{path.dirname(path.dirname(__file__))}/.env", "w") as env:

        env.write("# Fill in badge ID below.\n")
        env.write(f"BADGE_ID={new_id}")
        env.close()
    
    return None

'''
Ensures that an entered badge is a valid badge
@param badge: The ID of the badge to be validated
@return: Returns a bool representing if the badge is a valid badge or not
'''
def validate_badge(badge):

    badge_request = requests.get(f"https://badges.roblox.com/v1/badges/{badge}")

    if badge_request.status_code == 404:
        return False
    
    else:
        return True