
from time import sleep, strptime, time, mktime
import requests
import io
from os import path, makedirs
from dotenv import dotenv_values
from math import ceil

from rich.console import Console

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
Searches and lists all of a user's friends or followers
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

    if response.status_code == 200: # OK status code
        sleep(0.1) # Very short delay to avoid overloading API
        return response.json()["name"]
    else:
        return response.status_code
    
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
Does some math to calculate a user's account age
@param info_response: The raw response data which has the desired user's account creation date
@return: Returns an int of the user's account age in days
'''
def get_acc_age(info_response):

    date_gotten = info_response.json()["created"] # Grabs the 'created' section of the user info
    
    badge_date = strptime(f"{int(date_gotten[0:4])} {int(date_gotten[5:7])} {int(date_gotten[8:10])} {int(date_gotten[11:13])} {int(date_gotten[14:16])} {int(date_gotten[17:19])}", "%Y %m %d %H %M %S") # Converts the creation date of the account into a time struct

    days_old = ceil((time() - mktime(badge_date)) / 86400) # Does some math based off the current time, calculating the time in seconds that the account has existed and then converting that to days

    return days_old

'''
Compares two user's groups
@param user_one: The first user of whose groups are being compared
@param user_two: The second user of whose groups are being compared
@return: The number of groups the two users have in common.
'''
def group_comparison(user_one, user_two):

    if user_one == None: # If user_one is None, that means two users are not being compared and this function should be skipped
        return 0
    
    # Initialize useful variables
    user_one_groups = requests.get(f"https://groups.roblox.com/v1/users/{user_one}/groups/roles").json()["data"]
    id_comparison_list = []
    user_two_groups = requests.get(f"https://groups.roblox.com/v1/users/{user_two}/groups/roles").json()["data"]
    groups_in_common = 0

    for group in user_one_groups: # Iterate through the first user's groups and add all the groups' ids to a list
        id_comparison_list.append(group["group"]["id"])
    
    for group in user_two_groups: # Check each group's id against the ids in the list, incrementing the counter if a match is found

        if group["group"]["id"] in id_comparison_list:
            groups_in_common += 1

    return groups_in_common

'''
Compare's two user's friends
@param user_one: The first user of whose friends are being compared
@param user_two: The second user of whose friends are being compared
@return: The number of friends the two users have in common.
'''
def friend_comparison(user_one, user_two):
    
    if user_one == None: # If user_one is None, that means two users are not being compared and this function should be skipped
        return 0
    
    # Initialize useful variables
    user_one_friends = requests.get(f"https://friends.roblox.com/v1/users/{user_one}/friends").json()["data"]
    user_two_friends = requests.get(f"https://friends.roblox.com/v1/users/{user_two}/friends").json()["data"]
    friends_in_common = 0

    for user in user_two_friends: # Iterates through every friend in the second user's friends list, comparing them to the first user's friends list and incrementing the counter if a commonality is found

        if user in user_one_friends:
            friends_in_common += 1
        
    return friends_in_common

'''
Compares a user's avatar against the basic bacon avatars
@param user_id: The ID of the user being checked
@return: Returns true or false depending on if the user is a possible alt or not, with None as a return option if the input ID was bad
'''
def avatar_check(user_id):
    
    alt_id_lists = [ # A list of common accessory set ups for alts. Can be expanded if necessary.
        [63690008, 86498048, 86500008, 86500036, 86500054, 86500064, 86500078, 144075659, 144076358, 144076760], 
        [144075659, 382537569, 1772336109, 4047884939, 4637119437, 4637120072, 4637120775, 4637122096, 4637151279], 
        [62724852, 382537806, 382538059],
        [144076436, 144076512, 376526888]
        ]
    possible_alt = False
    
    avatar_request = requests.get(f"https://avatar.roblox.com/v1/users/{user_id}/currently-wearing") # Gets the user's currently worn accessories

    if avatar_request.status_code == 429: # If we get rate limited, do this

        while avatar_request.status_code == 429: # Loop until we don't get rate limited

            sleep(10)
            avatar_request = requests.get(f"https://avatar.roblox.com/v1/users/{user_id}/currently-wearing")
    
    elif avatar_request.status_code == 404: # If a bad ID was input, return None
        return None

    user_avatar = avatar_request.json()["assetIds"] # Gets the list of asset IDs

    for avatar in alt_id_lists: # Loops through the above list of common accessory set ups and checks our current user against those.
        
        if user_avatar == avatar:
            possible_alt = True
    
    return possible_alt

'''
Runs a few checks on a given user, comparing them to the 'main account'.
@param mode: Takes the mode the user selected and doesn't check some criteria if it is the 'badge' mode
@param main_user: The 'main account' mentioned above. This is always the person whose friends list was checked
@param compared_user_id: Takes the user_id of the secondary user so as to reduce the amount of calls made to the Roblox api. The ID is needed to get the badge count.
@return: Returns a tuple of the status and exit messages. The status represents if the user is a suspected alt. The exit messages describe why they're suspected as an alt (one or more of the criteria).
'''
def compare_username(mode, main_user, compared_user_id):
    
    # Initializes a few useful variables
    status = False
    exit_messages = []
    compared_username = get_ro_username(compared_user_id).lower()
    main_username = get_ro_username(main_user)
    alt_info = requests.get(f"https://users.roblox.com/v1/users/{compared_user_id}") # Gets the user's account info from the API
    env_badge = dotenv_values(f"{path.dirname(path.dirname(__file__))}/.env")["BADGE_ID"] # This is the ID of the badge held in the .env file, used to rule out some false positives
    fav_game_count = len(requests.get(f"https://games.roblox.com/v2/users/{compared_user_id}/favorite/games").json())

    # The following 3 lines calculates the amount of days since the user acquired the badge
    days_old = get_badge_date(compared_user_id, env_badge)
    badge_date = strptime(f"{days_old[0]} {days_old[1]} {days_old[2]} {days_old[3][0:2]} {days_old[3][3:]}", "%Y %m %d %H %M")
    badge_time = int(ceil((time() - mktime(badge_date)) / 86400))

    friend_num = requests.get(f"https://friends.roblox.com/v1/users/{compared_user_id}/friends/count") # Gets the number of friends a user has

    friends_in_common = friend_comparison(main_user, compared_user_id) # Counts how many friends the two accounts have in common

    # The following 3 lines gets the number of groups a user is in
    group_req = requests.get(f"https://groups.roblox.com/v1/users/{compared_user_id}/groups/roles").json()
    group_num = 0
    for group in group_req["data"]: group_num += 1

    groups_in_common = group_comparison(main_user, compared_user_id) # Count how many groups the accounts are both in

    # Counts the amount  of badges the given user has
    badge_req = requests.get(f"https://badges.roblox.com/v1/users/{compared_user_id}/badges", params={"limit": 100})

    if badge_req.status_code == 404: # If the request errors, returns a tuple of Nones. Request usually errors because an account no longer exists.
        return None, None
    
    else:
        badge_count = len(badge_req.json()["data"])

    # Checks a few criteria that could qualify them as an alt and flags them if they meet those criteria
    if main_username.strip("1234567890").lower() in compared_username and mode != "badge" and mode != "user": # Doesn't check if the main username is the same as the compared username if using the badge mode. Doesn't make sense to use this criteria based off what the badge_checker does

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
            exit_messages.append("Account does not have many badges. (Be aware, this can be a false positive due to privacy settings.)")

    if compared_username.isdigit(): # Check if the user has only numbers in their username
        status = True
        exit_messages.append("Account's username is only numbers.")

    if check_barcode(compared_username): # Checks if the user has a barcode username (only I's and L's) These are used to make it harder to find / ban alt accounts as capital I's and lowercase l's are hard to distinguish
        status = True
        exit_messages.append("Barcode username (only I's and L's).")

    if get_acc_age(alt_info) < 50: # Checks if the user's account is new
        status = True
        exit_messages.append("Account is new. (<50 days old)")

    if badge_time < 7: # If they recently got the chosen badge, its possible they've joined to troll / are an alt
        status = True
        exit_messages.append("Account has recently acquired the badge.")

    if alt_info["description"] == '': # Checks if the account has a description. Low effort alts often don't.
        status = True
        exit_messages.append("Account has no description.")

    if friends_in_common > 15 and mode != "badge" and mode != "user": # Checks how many friends the two accounts share. Higher number = more likely to be an alt but this is very weak evidence
        status = True
        exit_messages.append("Accounts share >15 friends.")

    if friend_num < 5: # Checks if the user has friends. If they have little to no friends, they're either sad or an alt. More often than not, its the latter
        status = True
        exit_messages.append("Account has little to no friends.")

    if groups_in_common > 5 and mode != "badge" and mode != "user": # Checks how many groups the two compared accounts have in common. If two accounts have many groups in common, one is possibly an alt but this is fairly weak
        status = True
        exit_messages.append("Accounts share >5 groups in common.")

    if group_num == 0: # Checks if the user is in any groups
        status = True
        exit_messages.append("Account is in no groups.")

    if fav_game_count == 0: # Checks if the user has any games favorited. Can be an indicator that its an alt and not an account frequently played on.
        status = True
        exit_messages.append("Account has no favorite games.")

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