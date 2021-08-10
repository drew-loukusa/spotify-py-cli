def create_playlist(sp, name) -> str:
    """ Attempts to create a playlist with the given name, returns the playlist id if successful"""
    user_id = sp.me()['id']
    result = sp.user_playlist_create(user_id, name=name, public=False)
    return result['id'] 
    
def list_playlists(sp):
    user_id = sp.me()['id']
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        print(playlist['name'])

def delete_playlist(sp, pl_id):
    """Attempts to delete the playlist with the id 'pl_id'"""
    sp.current_user_unfollow_playlist(playlist_id=pl_id)

# I'd assume there is a better way to do this.
# However, how many users are going to have > 100 playlists?
# Not many. And even the outliers probably have < 1000 playlists.
# Search in a linear fashion through < 1000 vaules is easy for a computer.
# Might improve this at some point, but for now it's fine.
def check_exists(sp, pl_id):
    user_id = sp.me()['id']
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        name, id = playlist['name'], playlist['id']
        if id == pl_id:
            return True
    return False

def get_playlist(sp, pl_name):
    user_id = sp.me()['id']
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        name, id = playlist['name'], playlist['id']
        if name == pl_name:
            return playlist 
    return None 

def get_pl_id_from_name(sp, pl_name):
    user_id = sp.me()['id']
    playlists = sp.user_playlists(user_id)
    for playlist in playlists['items']:
        name, id = playlist['name'], playlist['id']
        if name == pl_name:
            return id
    return ''