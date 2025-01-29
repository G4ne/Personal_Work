
from os import environ
from dotenv import load_dotenv
import requests
from time import sleep
import io

'''
Searches for users on Roblox using the supplied keyword
@arg username_keyword: The keyword to be used to search for users
@arg id_list: Takes a list to which the function will add the IDs it receieves from the API
@arg name_list: Takes a list to which the function will append the names it recieves from the API
@arg next_page_cursor: If supplied, this will change the page that the API supplies when requested. should never be used but is there for extremely large searches
@return: Returns None as the main work the function is doing is adding things to the given lists '''
def search_user(username_keyword, id_list, name_list, next_page_cursor=""):
    
    parameters = {"keyword": username_keyword, "cursor": next_page_cursor, "limit": 100}
    response = requests.get("https://users.roblox.com/v1/users/search", params=parameters)


    if response.status_code == 429: #Checks if we recieved the too many requests error and enters a loop to retry data acquisition if we did

        while response.status_code == 429:

            print("Too many requests, waiting and trying again.")
            sleep(10.0)
            response = requests.get("https://users.roblox.com/v1/users/search", params=parameters)

    if response.status_code == 200: #Good status code, if we recieve a 200 then we can begin collecting IDs

        user_list = response.json()["data"]

        for user in user_list: #Appends the id and name of the user given by the API
            id_list.append(user["id"])
            name_list.append(user["name"])

    else: #Shouldn't happen but catches either of the two other error codes we can get
        print(f"Error: {response.status_code}")
        return None
    
    if response.json()["nextPageCursor"] != None: #Checks to see if there are more pages of results and recursively checks the pages if they exist
        search_user(username_keyword, id_list, name_list, response.json()["nextPageCursor"])

    return None


'''
Searches a given user's badge list for the given badge using their ids
@arg user_id: The ID of the user is being checked
@arg badge_id: The ID of the badge the user is being checked for
@arg cursor_loc: Similar to the above function's cursor argument, if this is supplied, it will change the page that the Roblox API supplies when queried 
@return: Returns a bool representative of if the user has the badge '''
def search_badges(user_id, badge_id, cursor_loc=""):
    
    response = requests.get(f"https://badges.roblox.com/v1/users/{user_id}/badges", params={"limit": 10,"cursor": cursor_loc})

    badges = response.json()["data"]

    for badge in badges: #Iterates through the badges provided by the API and checks their IDs against the badge ID we're looking for
        if badge["id"] == int(badge_id):
            return True
            
    if response.json()["nextPageCursor"] != None: #If there are more pages of badges, this recursively checks them.
        if search_badges(user_id, badge_id, response.json()["nextPageCursor"]):
            return True

    return False

    
'''
Processes a list of user IDs and prints whether each user has a certain badge to the console
@arg requested_badge_id: The ID of the badge that each user is being checked for
@return: Returns nothing. Prints output to console '''
def process_user_ids(requested_badge_id):
    
    print("Enter the keyword you'd like to search for usernames with.\n")
    user_keyword = input()

    user_ids = [] #makes lists for the user ids and names to be stored in after being found with the keyword
    user_names = []

    search_user(user_keyword, user_ids, user_names) #searches, using the keyword, for users and adds their id and name to the list

    badge_name_request = requests.get(f"https://badges.roblox.com/v1/badges/{requested_badge_id}") #gets the name of the badge to be logged
    badge_name = badge_name_request.json()["name"]

    with open("badge_results.txt", "w") as output:

        output.write("\n") #gives whitespace at the top for ease of reading

        for i in range(len(user_ids)): #iterates through all user ids that were found matching the keyword and checks if they have the given badge, writing the result to an output file
            if search_badges(user_ids[i], requested_badge_id):
                output.write(f"{user_ids[i]} ({user_names[i]})\n")
                output.write(f"User has the {badge_name} badge\n\n")
            else:
                output.write(f"{user_ids[i]} ({user_names[i]})\n")
                output.write(f"User does not have the {badge_name} badge\n\n")

    
    print(f"\nDone!")
    return None
    

def main():

    load_dotenv() #Adds .env file to environment

    try: #error handling
        process_user_ids(environ["BADGE_ID"])
    except KeyError: #makes a .env file to be filled with the desired badge ID
        print(".env file not detected. Replacement file created. Please enter the ID of the badge you wish to search for in the file.")
        with open(".env", "w") as replacement:
            replacement.write("# Fill in badge ID below.\n")
            replacement.write("BADGE_ID=")
            replacement.close()
    except Exception as error_code:
        print(f"Error: {error_code}")
    return


if __name__ == "__main__":
    main()
