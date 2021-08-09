
# Overview
## Document Purpose
The purpose of this document is to list out the requirements for this project (SpotifyPlaylistEditor). 

Having a spec allows me to write tests before writing code as I am using TDD for this project.

## High Level Requirements

* Users should be able to login/verify their identity
* Users should be able to list/show their existing playlists
* Users should be able to search their existing playlists
* Users should be able to create new playlists
* Users should be able to delete created/existing playlists 
* Users should be able to edit created/existing playlists 

## Mid Level Requirements

* Each high level feature should have associated command
    * To do anything with this CLI app, you have to use one of the 'commands'. These are not flags, (optional) because if you don't provide one, you get the help dialog text. So, no dashes and I'm calling these commands
* The CREATE, DELETE, EDIT, and SEARCH commands must be provided a name 
    * If the name provided does not match any exisiting playlists, the app should attempt to find playlists with similar names
        * This behavior should be toggleable with a sub flag (I.E. do not search for similarly named lists if provided name does not match any existing lists)
        * How many lists are returned after searching can be changed as well with a flag 
            > Return N lists (use flag with number)

            > Return ALL user playlists (use flag with no number)
    * If the name provided does not match any existing playlists and...
        * No similar lists exist
        * Similar lists _may_ exist but the "DO NOT SEARCH FOR SIMILAR LISTS" flag has been used
        > Return an error to the user 

* CREATE command:
    * If create new command is provided a name that already exists, should return an error to the user 
        * This behavior can be overidden with a flag: I.E. force create the list. This  flag should cause the app to delete the existing list with said name, and then create a new playlist

    * If playlist creation is successful, nothing should printed to the screen (in typical CLI app fashion)

* DELETE command:
    * Should prompt user before deleting ("are you sure you want to delete list X?")
        * This behavior can be overidden with a flag: Force delete with out prompting user 
            * Should display nothing if delete was successful
            * Should display an error if delete was unsuccessful

* LIST/SEARCH command:
    * Has two names (LIST and SEARCH) ?
    * If provided NO NAME, should list all playlists of the user 
    * (?) Should allow with subflags, various ways of filtering the provided lists
    * (?) Should paginate results if number of existing lists is large 
        * (?) Number of results per page can be set with flag 
    * EXPAND LATER

* (?) Some commands will send output to screen if errors occur, it should be possible to suppress these errors with a flag (--silent , or something like that)


## Notes on Handeling Login/Verification

At least to start out with, this application will require each user to create their own secret + client_ID through spotify. The secrets can go into a file which is then read by the app.

This is simpler than the alternative, which is to split the app into a local CLI app which talks to a server. This method would allow a single secret to be used (for the server) and the local cli that each user downloads simply talks to the server. 

This method is obviously more work, and would require me to code two applications. Maybe once I'm done with the first prototype, maybe.
