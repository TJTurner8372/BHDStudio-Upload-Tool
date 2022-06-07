# Show Streams Inside Audio Settings Window -----------------------------------------------------------------------
import pathlib
from pymediainfo import MediaInfo


def stream_menu(x):
    build_list = []
    media_info = MediaInfo.parse(pathlib.Path(x))  # Uses pymediainfo to get information for track selection
    for track in media_info.tracks:  # For loop to loop through mediainfo tracks
        # Formatting --------------------------------------------------------------------------------------------------
        if track.track_type == 'Audio':  # Only grab audio track information

            if str(track.compression_mode) != 'None':
                audio_track_compression = f"{str(track.compression_mode)}  |  "
            else:
                audio_track_compression = ''

            if str(track.format) != 'None':  # Gets format string of tracks (aac, ac3 etc...)
                audio_format = f"{str(track.commercial_name)} - ({str(track.format).lower()})  |  "
            else:
                audio_format = ''
            if str(track.channel_s) != 'None':  # Gets audio channels of input tracks
                if str(track.channel_s) == '8':
                    show_channels = '7.1'
                elif str(track.channel_s) == '6':
                    show_channels = '5.1'
                elif str(track.channel_s) == '3':
                    show_channels = '2.1'
                else:
                    show_channels = str(track.channel_s)
                audio_channels = f"Chnl: {show_channels}  |  "
            else:
                audio_channels = ''
            if str(track.bit_rate_mode) != 'None':  # Gets audio bit rate mode
                if str(track.other_bit_rate_mode) != 'None':  # Get secondary string of audio bit rate mode
                    audio_bitrate_mode = f"{str(track.bit_rate_mode)}  |  "
            else:
                audio_bitrate_mode = ''
            if str(track.other_bit_rate) != 'None':  # Gets audio bit rate of input tracks
                audio_bitrate = f"{str(track.other_bit_rate[0])}  |  "
            else:
                audio_bitrate = ''
            if str(track.other_language) != 'None':  # Gets audio language of input tracks
                audio_language = f"{str(track.other_language[0])}  |  "
            else:
                audio_language = ''
            if str(track.title) != 'None':  # Gets audio title of input tracks
                if len(str(track.title)) > 40:  # Counts title character length
                    audio_title = f"{str(track.title)[:20]}...  |  "  # If title > 40 characters
                else:
                    audio_title = f"{str(track.title)}  |  "  # If title is < 40 characters
            else:
                audio_title = ''
            if str(track.other_sampling_rate) != 'None':  # Gets audio sampling rate of input tracks
                audio_sampling_rate = f"{str(track.other_sampling_rate[0])}  |  "
            else:
                audio_sampling_rate = ''
            if str(track.other_duration) != 'None':  # Gets audio duration of input tracks
                audio_duration = f"{str(track.other_duration[0])}  |  "
            else:
                audio_duration = ''
            if str(track.delay) != 'None':  # Gets audio delay of input tracks
                if str(track.delay) == '0':
                    audio_delay = ''
                else:
                    audio_delay = f'{str(track.delay)}ms  |  '
            else:
                audio_delay = ''
            if str(track.other_stream_size) != 'None':  # Get tracks stream size
                audio_track_stream_size = f"{str(track.other_stream_size[4])}  |  "
            else:
                audio_track_stream_size = ''
            if str(track.other_bit_depth) != 'None':  # Get tracks bit-depth
                audio_track_bit_depth = f"{(track.other_bit_depth[0])}-bit  |  "
            else:
                audio_track_bit_depth = ''
            # ---------------------------------------------------------------------------------------------- Formatting
            audio_track_info = str(audio_track_compression + audio_format + audio_channels + audio_bitrate_mode +
                                   audio_bitrate + audio_sampling_rate + audio_delay + audio_duration +
                                   audio_language + audio_title + audio_track_stream_size +
                                   audio_track_bit_depth).strip()
            # Formatting
            build_list.append(audio_track_info)
    return build_list
# ---------------------------------------------------------------------------------------------------- Show Streams
