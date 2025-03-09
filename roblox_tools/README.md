# Roblox API Scripts

Made these scripts to interact with the Roblox API in various ways. The ro_functions directory is required for any of these to function.

Badge_checker.py - Searches Roblox for users given a keyword from input and tells you if the discovered users have a certain badge. You need the badge ID of the badge you're looking for and it should be placed in the .env file (just run the script if there is no .env file).

Friend_check - Takes a Roblox user ID from input and searches the given user's friends list, outputting if each of the given user's friends has a specified badge. Again, you need the badge ID of the badge you're looking for and the ID should be placed in the .env file. (Run the script if there is no .env file, one will automatically be made)

Alt_check - Checks the output of the previous two programs and flags accounts that have common alt account attributes. (Barcode username, containing the main accounts name in the alt's, alt in the username, etc).

All scripts in this folder REQUIRE the ro_functions directory to exist in the same directory as the script.

All output is placed inside a folder named "output_files" which is created when you first run any of these scripts. You probably shouldn't move this folder or change its contents as some scripts rely on one or more output files to function.