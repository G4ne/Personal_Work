
from ro_functions.roblox_api_searches import create_output_file, get_ro_username, search_friends, replace_env, search_badges
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

    while not valid_u_id: #Makes sure the entered user ID is valid, looping until a valid UID is entered.

        user_id = input()

        try:

            check_uid_request = requests.get(f"https://users.roblox.com/v1/users/{user_id}")

            if check_uid_request.status_code == 200:
                valid_u_id = True
            else:
                raise Exception("Invalid user ID, please enter a valid user ID.")

        except Exception as user_excep:
            print(f"Error: {user_excep}")

    friends_list = search_friends(user_id) #Gets the user's friends list from the search_friends function

    badge_name_request = requests.get(f"https://badges.roblox.com/v1/badges/{badge_id}") #gets the name of the badge to be logged in output
    badge_name = badge_name_request.json()["name"]

    output_file = create_output_file("friend_search_result.txt") #Creates the output file in its correct location

    for friend in friends_list: #Iterate through the given user's friends list and prints the appropriate statement to output.
        
        has_badge = search_badges(friend, badge_id)

        if has_badge:
            output_file.write(f"\n{get_ro_username(friend)} ({friend}) has the {badge_name} badge.\n")

        elif not has_badge:
            output_file.write(f"\n{get_ro_username(friend)} ({friend}) does not have the {badge_name} badge.\n")

        elif has_badge == None:
            output_file.write(f"\n{get_ro_username(friend)} does not exist / is invalid.\n")


    print("\nDone!")
    return None

def main():

    load_dotenv() #Loads .env variables into environ

    try: #Main work

        process_user_friends(environ["BADGE_ID"])
    
    except KeyError: #Creates and fills new env file if none exist

        replace_env()
        print("\nPlease run the script again.")

    except Exception as ex: #Prints any other exception that might happen

        print(f"Error: {ex}")

    return


if __name__ == "__main__":
    main()