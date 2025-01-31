
from time import sleep
import requests
import io
from os import path, makedirs

'''
Searches for users on Roblox using the supplied keyword
@arg username_keyword: The keyword to be used to search for users
@arg id_list: Takes a list to which the function will add the IDs it receieves from the API
@arg name_list: Takes a list to which the function will append the names it recieves from the API
@arg next_page_cursor: If supplied, this will change the page that the API supplies when requested. should never be used but is there for extremely large searches
@return: Returns None as the main work the function is doing is adding IDs and names to the given lists '''
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
Searches and lists all of a user's friends
@arg username_keyword: The id of the user whose friends list is being checked
@return: Returns a list which contains the IDs of all the requested user's friends '''
def search_friends(user_id):

    response = requests.get(f"https://friends.roblox.com/v1/users/{user_id}/friends")

    user_id_list = []

    if response.status_code == 200: #OK status code, allows us to move forward

        friends_list = response.json()["data"]

        for friend in friends_list: #iterate through all the friends, adding the ID to the ID list

                user_id_list.append(friend["id"])

    else:
        print("Requested user does not exist.")

    return user_id_list

'''
Gets and returns the Roblox username of a user given their user ID. Mostly used to convert user IDs into more readable usernames
@arg user_id: The user ID of the account to get the name of
@return: Returns a string of the user's username
'''
def get_ro_username(user_id):
    
    response = requests.get(f"https://users.roblox.com/v1/users/{user_id}")

    if response.status_code == 200: #OK status code
        return response.json()["name"]
    else:
        return "Invalid user id."

'''
Creates an output file in the output_files directory
@arg file_name: A string of the name of the file to create
@return: returns a file object that can be written to
'''
def create_output_file(file_name):
   
    if path.dirname(__file__) == "ro_functions/": #Checks the current directory and sets the correct name
        dir_name = path.dirname(path.dirname(__file__))
    else:
        dir_name = path.dirname(__file__)

    makedirs(f"{path.dirname(path.dirname(__file__))}/output_files", exist_ok=True) #Creates the output_files directory if it doesn't exist
    file_loc = f"{path.dirname(path.dirname(__file__))}/output_files/{file_name}" #Sets the file location as output files with the file name at the end

    return open(file_loc, "w")