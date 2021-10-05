class General:
    # def num_found(self, num_items: int, item_name: str):
    #     """{num_items} {item_type}(s) found matching name {item_name}"""
    #     return self.num_found.__doc__.format(
    #         num_items=num_items, item_type=self.type, item_name=item_name
    #     )
    num_items_found = "{} item(s) found matching name {}"
    item_DNE = "{} with {}: '{}' appears to not exist!"
    op_canceled = "Operation cancelled"
    not_found = "Could not find {} in user's followed items."


class Create:
    # Help strings for options
    force_help = "Create the playlist, even if you already own or follow a playlist with name NAME"
    collab_help = "Is the created playlist collaborative"
    desc_help = "Playlist description."
    public_help = "Is the created playlist public"

    # Command completion info
    plist_created = "Playlist created."
    dupe_created = "Playlist with duplicate name created."
    dupe_exist_no_f = (
        "A playlist with that name already exists.\n"
        + "Choose a diffrent name or use '--force'"
        + "to create a playlist with the same name "
        + "as the existing playlist."
    )

    # Info about created playlist
    pub_status = "Public: {}"
    collab_status = "Collaborative: {}"
    desc_status = "Description: {}"


class Follow:
    id_help = "Use id to specify item to follow"
    followed = "Followed {} with name: {}, id: {}"


class Save:
    id_help = "Use id to specify item to save"
    saved = "Saved {} with name: {}, id: {}"


class Unsave:
    id_help = "Use id to specify item to unsave"
    unsaved = "Unsaved {} with name: {}, id: {}"


class Unfollow:
    id_help = "Use id to specify item to unfollow"
    # no_prompt_help = (
    #     "Do not prompt user to confirm unfollow. Will be ignored if NAME "
    #     + "is supplied and multiple items exist with the same name.\n"
    # )

    no_prompt_help = "Do not prompt user to confirm unfollow."

    dupes_found = (
        "Multiple items were found with name: {}."
        + "Please specify with '--id' which item to unfollow."
    )

    item_DNE = "No playlist exists with id: {}"
    confirm = "Are you sure you want to unfollow the {} '{}', id: {}?"
    unfollowed_item = "unfollowed item: {}, ID: {}"


class Search:
    user_help = "Limit search to just a user's followed items"
    limit_help = (
        "The number of items to return (min = 1, default = 10, max = 50)"
    )
    market_help = "An ISO 3166-1 alpha-2 country code or the string"

    list_all = (
        "No name provided, listing all items (user created and followed)..."
    )
    item_DNE = "Could not find {} in user's followed items."
    show_info = "{}, ID: {}\nDescription:\n{}"

    search_pub = "Searching public items..."
    num_items_found = "Found {} items matching the search query: '{}'"


class Listing:
    listing = "Listing your saved/followed {}s:"
    params = "Limit: {}, Offset: {}"
    ret_all = "Retrieving all items..."


class Edit:
    help = "Edit a playlist you own, or are a collaborator on"

    class Details:
        name_help = "Change the name of the playlist"
        public_help = "Change the public/private status of the playlist"
        collab_help = "Change whether the playlist is collaborative or not"
        desc_help = "Change the description of the playlist"

    class Add:
        track_ids_help = "Track ID, or list of space seperated track IDs to add to the playlist"
        unique_help = "Only add track if it NOT already in the list (default behavior is FALSE; always add track)"
        insert_at_help = """Insert before track before INDEX.
Default is to add to the BACK/END of the playlist, specify 0 to add to the front.
For multiple tracks, takes a list of semi-colon and comma seperated values.
See help text for '--specific' option on the remove command for list syntax."""
        not_unique = "Track not added as it already exists in the playlist and option '--add-if-unique' was used."

    class Remove:
        track_ids_help = "Track ID, or list of space seperated track IDs to add to the playlist"
        all_help = """Remove all occurances of the track from the playlist. NOTE: This option will override '--count' and '--specfic'"""
        specific_help = """Remove specific occurances of the track,
argument to option should be comma seperated list of positions as a str"
For multiple tracks, seperate track position lists with ';'
Example: For tracks: TR1 TR2 TR3
        A list like: "0,2; 3,4; 5,6" would match up TR1 to 0,2, TR2 to 3,4 ...

NOTE:
Command will left align the positions list to the track ids.
Any track that doesn't get a position list, will fall back to
simple removal of the first occurance.
Example: track ids: TR1 TR2 TR3, position list: "0,2; 5,6"
In this case, TR3 will fall back to simple first occurance removal.
To skip an item in the track ids, use an ellipse. Example: \"0,2; ... ; 5,6\"

NOTE: If you specify a count with '--count', any tracks that have position lists will ignore said count.
"""
        offset_help = """For walking, start at the first INT, end at the second INT.
Providing -1 as the second int tells it to walk to the end of the list.
By default it walks from the start (0) to the end (-1)
        """
        count_help = "How many occurances of track to remove from the playlist. Can be overridden by '--specific' or '--all'"
