
from time import sleep
import requests
import os

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

def main():
    first_half = os.path.split(os.getcwd())[0]
    file_loc = first_half + "/roblox_api_searches.py"
    print(file_loc)

if __name__ == "__main__":
    main()