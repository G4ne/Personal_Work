
from os import environ, path, makedirs
from dotenv import load_dotenv
import requests
import io
from ro_functions.roblox_api_searches import search_badges, search_user, create_output_file

'''
Processes a list of user IDs and prints whether each user has a certain badge to the console
@arg requested_badge_id: The ID of the badge that each user is being checked for
@return: Returns nothing. Prints output to file '''
def process_user_ids(requested_badge_id):
    
    print("Enter the keyword you'd like to search for usernames with.\n")
    user_keyword = input()

    user_ids = [] #makes lists for the user ids and names to be stored in after being found with the keyword
    user_names = []

    search_user(user_keyword, user_ids, user_names) #searches, using the keyword, for users and adds their id and name to the list

    badge_name_request = requests.get(f"https://badges.roblox.com/v1/badges/{requested_badge_id}") #gets the name of the badge to be logged in output
    badge_name = badge_name_request.json()["name"]

    output = create_output_file("badge_results.txt")

    output.write("\n") #gives whitespace at the top for ease of reading

    for i in range(len(user_ids)): #iterates through all user ids that were found matching the keyword and checks if they have the given badge, writing the result to an output file

        if search_badges(user_ids[i], requested_badge_id):

            output.write(f"{user_ids[i]} ({user_names[i]})\n")
            output.write(f"User has the {badge_name} badge\n\n")

        else:

            output.write(f"{user_ids[i]} ({user_names[i]})\n")
            output.write(f"User does not have the {badge_name} badge\n\n")

    output.close()
    
    print(f"\nDone!")
    return None
    

def main():

    load_dotenv() #Adds .env file to environ

    try: #error handling

        process_user_ids(environ["BADGE_ID"])

    except KeyError: #makes a .env file to be filled with the desired badge ID

        print(".env file not detected. Replacement file created. Please enter the ID of the badge you wish to search for and run the script again.")

        with open(".env", "w") as replacement:

            replacement.write("# Fill in badge ID below.\n")
            replacement.write("BADGE_ID=")
            print("\nPlease enter the ID of the badge you'd like to search users for.")
            replacement.write(input())
            replacement.close()

    except Exception as error_code:
        print(f"Error: {error_code}")

    return


if __name__ == "__main__":
    main()
