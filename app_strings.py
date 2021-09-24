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
    force_help = (
        "Create the playlist, even if one already exists with name NAME"
    )
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
