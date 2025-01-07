import os
import random
from moviepy.editor import AudioFileClip, CompositeAudioClip, concatenate_videoclips, concatenate_audioclips, afx, vfx, VideoFileClip

def process_intro(intro_video, intro_audio, video, fade_seconds = 3):
    main_vid_0 = video.subclip(0, fade_seconds)
    main_vid_1 = video.subclip(fade_seconds)
    first_intro = intro_video.set_audio(intro_audio.subclip(0, intro_video.duration).volumex(0.8))
    intro_fade_audio = CompositeAudioClip([intro_audio.subclip(intro_video.duration, intro_video.duration + fade_seconds).fx(afx.audio_fadeout, fade_seconds), main_vid_0.audio])
    intro_fade = main_vid_0.set_audio(intro_fade_audio)
    full_intro = concatenate_videoclips([first_intro, intro_fade, main_vid_1])
    return full_intro

def process_outro(outro_video, outro_audio, video, fade_seconds = 3):
    main_vid_1 = video.subclip(fade_seconds, video.duration - fade_seconds)
    main_vid_2 = video.subclip(video.duration - fade_seconds, video.duration)
    outro_fade_audio = CompositeAudioClip([main_vid_2.audio, outro_audio.subclip(0, fade_seconds).fx(afx.audio_fadein, fade_seconds)])
    outro_fade = main_vid_2.set_audio(outro_fade_audio)
    outro_last = outro_video.set_audio(outro_audio.subclip(fade_seconds, outro_video.duration + fade_seconds).volumex(0.8))
    full_outro = concatenate_videoclips([main_vid_1, outro_fade, outro_last])
    return full_outro

def process_video(episode_number, fade_seconds = 3):
    intro_video = VideoFileClip('assets/VH_intro720.mp4').without_audio().fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
    main_video = VideoFileClip(f'ep_{episode_number}.mkv')
    main_vid_0 = main_video.subclip(0, fade_seconds)
    main_vid_1 = main_video.subclip(fade_seconds, main_video.duration - fade_seconds)
    main_vid_2 = main_video.subclip(main_video.duration - fade_seconds, main_video.duration)
    outro_video = VideoFileClip('assets/Outro720.mp4').without_audio().fx(vfx.fadein, 1).fx(vfx.fadeout, 1)


    intro_audio = AudioFileClip('assets/Ringside - Dyalla.mp3')#.subclip(0, intro_video.duration + fade_seconds).volumex(0.8)
    outro_audio = AudioFileClip('assets/Inspired (Instrumental) - NEFFEX.mp3')#.subclip(0, outro_video.duration + fade_seconds).volumex(0.8)


    first_intro = intro_video.set_audio(intro_audio.subclip(0, intro_video.duration).volumex(0.8))
    intro_fade_audio = CompositeAudioClip([intro_audio.subclip(intro_video.duration, intro_video.duration + fade_seconds).fx(afx.audio_fadeout, fade_seconds), main_vid_0.audio])
    #intro_fade_audio.write_audiofile('test_intro.mp3')
    intro_fade = main_vid_0.set_audio(intro_fade_audio)
    full_intro = concatenate_videoclips([first_intro, intro_fade])

    outro_fade_audio = CompositeAudioClip([main_vid_2.audio, outro_audio.subclip(0, fade_seconds).fx(afx.audio_fadein, fade_seconds)])
    outro_fade = main_vid_2.set_audio(outro_fade_audio)
    outro_last = outro_video.set_audio(outro_audio.subclip(fade_seconds, outro_video.duration + fade_seconds).volumex(0.8))
    full_outro = concatenate_videoclips([outro_fade, outro_last])

    #later_video = concatenate_videoclips([main_vid_2, outro_video])
    #later_video = later_video.set_audio(outro_audio)

    full_video = concatenate_videoclips([full_intro, main_vid_1, full_outro])
    #full_video = concatenate_videoclips([intro_video, main_vid_1, later_video])
    #full_video = full_video.set_audio(intro_audio)
    full_video.write_videofile(f'final_ep_{episode_number}.mp4')

def process_clip(clip_process_options, video_options):
    clips_to_return = []
    clip_to_process = VideoFileClip(clip_process_options.clip_path)

    if (clip_process_options.include_intro):
        #intro_video = VideoFileClip('assets/VH_intro720.mp4').without_audio().fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        intro_video = VideoFileClip(video_options.intro_video_path)
        intro_audio = AudioFileClip(video_options.intro_audio_path)
        if (not video_options.include_intro_video_audio):
            # todo: video audio is overwritten here; fix it
            intro_video = intro_video.without_audio()
        intro_video = intro_video.fx(vfx.fadein, 1).fx(vfx.fadeout, 1)
        if (video_options.include_intro_video_audio):
            intro_video = intro_video.set_audio(intro_audio.subclip(0, intro_video.duration).volumex(0.8))
        clips_to_return.append(intro_video)

    return clips_to_return

def process_montage_video(video, montage_speed, fade = 1, volume = 0.8):
    montage = video.without_audio().set_fps(video.fps * montage_speed).fx(vfx.speedx, montage_speed)
    audio = process_montage_audio(montage.duration, fade).volumex(volume)
    final_montage_clip = montage.set_audio(audio)
    return final_montage_clip

def process_montage(video_path, montage_speed, fade = 1):
    video = VideoFileClip(video_path, montage_speed)
    return process_montage_video(video, montage_speed, fade)

def process_montage_audio(video_length, fade):
    video_duration = video_length
    continue_loop = True
    montage_asset_directory = 'assets/montage'
    audio_asset_list = os.listdir(montage_asset_directory)
    return_list = []
    
    while continue_loop:
        audio_name = random.choice(audio_asset_list)
        audio = AudioFileClip(f'{montage_asset_directory}/{audio_name}')
        if (video_duration > audio.duration):
            return_list.append(audio.fx(afx.audio_fadein, fade).fx(afx.audio_fadeout, fade))
            video_duration = video_duration - audio.duration
        elif (video_duration < audio.duration):
            return_list.append(audio.subclip(0, video_duration).fx(afx.audio_fadein, fade).fx(afx.audio_fadeout, fade))
            continue_loop = False
        else:
            return_list.append(audio.fx(afx.audio_fadein, fade).fx(afx.audio_fadeout, fade))
            continue_loop = False
    return concatenate_audioclips(return_list)

