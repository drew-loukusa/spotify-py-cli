class General:
    num_playlists_found = "{} playlist(s) found matching name {}"
    playlist_DNE = "Playlist {} appears to not exist!"
    operation_canceled = "Operation cancelled"
    not_found = "Could not find {} in user's playlists."


class Create:
    # Help strings for options
    force_help = "Create the playlist, even if one already exists with name NAME"
    collab_help = "Is the created playlist collaborative"
    desc_help = "Playlist description."
    public_help = "Is the created playlist public"

    # Command completion info
    playlist_created = "Playlist created."
    duplicate_created = "Playlist with duplicate name created."
    dupe_exists_no_force = (
        "A playlist with that name already exists.\n"
        + "Choose a diffrent name or use '--force'"
        + "to create a playlist with the same name "
        + "as the existing playlist."
    )

    # Info about created playlist
    pub_status = "Public: {}"
    collab_status = "Collaborative: {}"
    desc_status = "Description: {}"


class Delete:
    id_help = "Use id to specify playlist"
    no_prompt_help = (
        "Do not prompt user to confirm deletion. Will be ignored if NAME "
        + "is supplied and multiple playlists exist with the same name.\n"
        + "See '--all' for deleting multiple lists that share the same name."
    )
    all_help = (
        "If multiple lists are found that share the same name, delete all. "
        + "Only has effect if used with --no-prompt."
    )

    specify_name_or_id = "You must specify NAME or ID"
    duplicates_found = (
        "Multiple playlists were found with name: {}."
        + "\nPlease use '--no-prompt' with '--all' to "
        + "delete all, or specify with '--id' which playlist to delete."
    )

    confirm_delete = "Are you sure you want to delete the playlist {}?"

    deleted_all = "Deleted all playlists associated with name: {}"
    deleted_playlist = "Deleted playlist: {}, ID: {}"


class Search:
    listing_all = "No name provided, listing all playlists..."
