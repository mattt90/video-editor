import episode_processor
import youtube_api
import sys

upload_file = 'upload.json'
if (len(sys.argv) > 1):
    upload_file = sys.argv[1]

options = episode_processor.get_options(upload_file)
#episode_processor.process_episode(options)

video_output_format = options["output_format"]
video_output_path = video_output_format.format(**options)
# upload video
video_options = {
    'keywords': options['keywords'],
    'title': options['episode_title'],
    'description': options['episode_description'],
    'category': options['category'],
    'privacyStatus': options['privacyStatus'],
    'publishAt': options['publishAt'],
    'file': video_output_path
}
print (video_options)
video = youtube_api.upload_video(video_options)
print(video)

thumbnail_output_format = options["thumbnailOutputFormat"]
thumbnail_output = thumbnail_output_format.format(**options)
# upload thumbnail
thumbnail_options = {
    'videoId': video.id,
    'file': thumbnail_output
}
youtube_api.upload_thumbnail(thumbnail_options)

# get playlists
playlist_options = {}
playlists = youtube_api.get_playlists(playlist_options)
print(playlists)

# filter playlist to playlist to upload video to
my_playlist_id = 0
for playlist in playlists.items:
    if (playlist.title == options["playlist"]):
        my_playlist_id = playlist.id
        break

# add video to playlist
youtube_api.insert_playlist_item({
    'video_id': video.id,
    'playlist_id': my_playlist_id
})
