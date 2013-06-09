#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rdio, json, sys, base64, codecs

if __name__ == '__main__':
    foo = map(base64.decodestring, ["cmQ0MmU0ZHVubWF2bjl0Y2FrOW5hem5w", "bndiYkhNQ2ZTYw=="])
    rdio_manager = rdio.Api(*foo)

    user_email = sys.argv[1]
    token_file = base64.encodestring(user_email).rstrip().rstrip('=')

    def get_tokens():
        try:
            with open(token_file, 'r') as fd:
                return json.load(fd)
        except IOError:
            return None

    def request_tokens():
        user = rdio_manager.find_user(user_email)
        print '%s %s''s key is: %s.' % (user.first_name, user.last_name, user.key)

        # Set authorization: get authorization URL, then pass back the PIN.
        token_dict = rdio_manager.get_token_and_login_url()
        print 'Authorize this application at: %s?oauth_token=%s' % (
            token_dict['login_url'], token_dict['oauth_token'])

        token_secret = token_dict['oauth_token_secret']
        oauth_verifier = raw_input('Enter the PIN / oAuth verifier: ').strip()
        token = raw_input('Enter oauth_token parameter from URL: ').strip()
        request_token = {"oauth_token":token, "oauth_token_secret":token_secret}
        authorization_dict = rdio_manager.authorize_with_verifier(oauth_verifier, request_token)

        # Get back key and secret. rdio_manager is now authorized
        # on the user's behalf.
        print 'Access token key: %s' % authorization_dict['oauth_token']
        print 'Access token secret: %s' % authorization_dict['oauth_token_secret']

        tokens = authorization_dict['oauth_token'], authorization_dict['oauth_token_secret']
        with open(token_file, 'w') as fd:
            json.dump(tokens, fd)
        return tokens

    tokens = get_tokens()
    if tokens is None:
        tokens = request_tokens()
    rdio_manager = rdio.Api(*(foo + tokens))

    playlists = rdio_manager.get_playlists().owned_playlists
    playlist = [t for t in playlists if t.name == sys.argv[2]][0]

    no_matches = []
    no_albums = []

    def add_artist_albums(artist):
        search_object = rdio_manager.search(
                query=artist,
                types=['Artists',],
                extras=['trackKeys',])
        if len(search_object.results) == 0:
            print "%s: No matches" % (artist)
            return
        best = None
        for result in search_object.results:
            if result.name.encode('utf-8').lower() == artist.lower():
                best = result
                break
        if best is None:
            print "No exact match for %s; possible matches:" % repr(artist)
            for result in search_object.results:
                print "  %s" % (repr(result.name))
            no_matches.append(artist)
            return
        add_keys = set()
        for album in rdio_manager.get_albums_for_artist(best.key) or []:
            print " + %s" % (album.name)
            add_keys = add_keys.union(set(album.track_keys))
        if len(add_keys) > 0:
            rdio_manager.add_to_playlist(playlist.key, list(sorted(add_keys)))
        else:
            no_albums.append(artist)

    with codecs.open(sys.argv[3], 'r', 'utf-8') as fd:
        artists = []
        for artist in (t.strip() for t in fd):
            if artist.startswith('#'):
                continue
            artists.append(artist)
        for idx, artist in enumerate(artists):
            print "(%d/%d) %s" % (idx+1, len(artists), artist)
            add_artist_albums(artist.encode('utf-8'))
    print "These queries failed:"
    for missed in no_matches:
        print "   %s" % missed
    print "No albums found for:"
    for missed in no_albums:
        print "   %s" % missed
