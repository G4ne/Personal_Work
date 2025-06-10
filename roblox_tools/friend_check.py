
from ro_functions.roblox_api_searches import create_output_file, get_ro_username, search_others, check_env, search_badges, get_badge_name
from dotenv import load_dotenv
from os import environ
import requests


'''
Takes searches a given user's friends list and outputs whether each friend has the given badge
@arg badge_id: The ID of the badge to be checked for in the friends list
@return: Returns None as the main output of the function is output to a file
'''
def process_user_friends(badge_id):
    
    print("Please enter the ID of the user whose friends you'd like to check.\n")
    valid_u_id = False

    while not valid_u_id: # Makes sure the entered user ID is valid, looping until a valid UID is entered.

        user_id = input()

        try:

            check_uid_request = requests.get(f"https://users.roblox.com/v1/users/{user_id}")

            if check_uid_request.status_code == 200:
                valid_u_id = True
            else:
                raise Exception("Invalid user ID, please enter a valid user ID.")

        except Exception as user_excep:
            print(f"Error: {user_excep}")

    friends_list = search_others(user_id, "friend") # Gets the user's friends list from the search_others function

    print(f"\nChecking {len(friends_list)} friends.\n")

    try:
        badge_name = get_badge_name(badge_id) #gets badge name for logging purposes
    
    except:
        print("Please edit the .env file and enter a valid badge ID or delete the .env file, run the program again, and enter a valid badge ID.")

    output_file = create_output_file("friend_search_result.txt") # Creates the output file in its correct location

    output_file.write(f"\n{get_ro_username(user_id)}'s friends\n") # Prints the user whose friends list is being checked to the top of the file for documentation

    for friend in friends_list: # Iterate through the given user's friends list and prints the appropriate statement to output

        friend_username = get_ro_username(friend)

        if friend_username == "Invalid user id.": # Checks if the friend being checked still has a valid account. This prunes off accounts that have been deactivated / deleted / banned.
            print("User no longer exists.")
            continue
        
        print(f"Checking: {friend_username}")
        has_badge = search_badges(friend, badge_id)

        if has_badge:
            output_file.write(f"\n{get_ro_username(friend)} ({friend}) has the {badge_name} badge.\n")

        elif not has_badge:
            output_file.write(f"\n{get_ro_username(friend)} ({friend}) does not have the {badge_name} badge.\n")

        elif has_badge == None:
            output_file.write(f"\n{get_ro_username(friend)} does not exist / is invalid.\n")


    print("\nDone!")
    output_file.close()
    return None

def main():

    check_env() # Ensures the .env file exists before it is loaded in

    load_dotenv() # Loads .env variables into environ

    try: # Main work

        process_user_friends(int(environ["BADGE_ID"]))

    except Exception as ex: # Prints any exceptions that might happen

        print(f"Error: {ex}")

    return


if __name__ == "__main__":
    main()