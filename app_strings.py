class General:
    spec_name_id = "You must specify NAME or ID"
    num_plist_found = "{} playlist(s) found matching name {}"
    plist_DNE = "Playlist {} appears to not exist!"
    op_canceled = "Operation cancelled"
    not_found = "Could not find {} in user's playlists."


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
    id_help = "Use id to specify playlist"
    followed = "Followed playlist with name: {}, id: {}"


class Unfollow:
    id_help = "Use id to specify playlist"
    no_prompt_help = (
        "Do not prompt user to confirm unfollow. Will be ignored if NAME "
        + "is supplied and multiple playlists exist with the same name.\n"
        + "See '--all' for deleting multiple lists that share the same name."
    )
    all_help = (
        "If multiple lists are found that share the same name, unfollow all. "
        + "Only has effect if used with --no-prompt."
    )

    dupes_found = (
        "Multiple playlists were found with name: {}."
        + "\nPlease use '--no-prompt' with '--all' to "
        + "unfollow all, or specify with '--id' which playlist to unfollow."
    )

    confirm = "Are you sure you want to unfollow the playlist {}?"

    unfollowed_all = "unfollowed all playlists associated with name: {}"
    unfollowed_plist = "unfollowed playlist: {}, ID: {}"


class Search:
    public_help = "Search public playlists instead of user's followed and created playlists"
    limit_help = (
        "The number of items to return (min = 1, default = 10, max = 50)"
    )
    market_help = "An ISO 3166-1 alpha-2 country code or the string"

    list_all = (
        "No name provided, listing all playlists (user created and followed)..."
    )
    plist_DNE = "Could not find {} in user's playlists."
    show_info = "{}, ID: {}\nDescription:\n{}"

    search_pub = "Searching public playlists..."
    num_public = "Found {} playlists matching the search query: '{}'"
