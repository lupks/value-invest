import os
import random
from pathlib import Path
from os import walk
from moviepy.editor import *
from nltk import tokenize


def concat_vid(text, keywords, save_dir):
    fnames = next(walk(save_dir), (None, None, []))[2]
    mov_paths = [os.path.join(save_dir, x) for x in fnames if '.DS_Store' not in x]
    dur_per_clip = 7
    height = 540

    def clip_vid(path):
        return VideoFileClip(path).subclip(0, dur_per_clip).resize(height=height)

    def clip_full(full, len_clips):
        full.set_duration(full.duration)

        def clip_into_clips(clip, start, end):
            return clip.subclip(start, end)

        times = [x for x in range(0, dur_per_clip * len_clips + dur_per_clip, dur_per_clip)]
        ret_clips = []
        for idx, start in enumerate(times[:-1]):
            full = full.set_duration(full.duration)
            new_clip = clip_into_clips(full, start, times[idx + 1])
            ret_clips.append(new_clip)

        return ret_clips

    def add_text(clip, text):

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i:i + n]

        text_split = text.split(' ')
        if len(text_split) > 5:
            text_len = len(text.split(' '))

            split_1 = ' '.join(text_split[:text_len // 2])
            split_2 = ' '.join(text_split[text_len // 2:])
            split_3 = None

            if len(text_split[:text_len // 2]) > 15:
                chunks = list(chunks(text_split, text_len // 3))
                split_1 = ' '.join(chunks[0])
                split_2 = ' '.join(chunks[1])
                split_3 = ' '.join(chunks[2] + chunks[3])

            fontsize = 18
            opacity = 0.9
            w, h = clip.size
            txt_clip = TextClip(split_1, fontsize=fontsize, font="Helvetica-Bold", color='white')
            txt_col = txt_clip.on_color(size=(clip.w + txt_clip.w, txt_clip.h + 10), color=(0, 102, 255),
                                        pos=(6, 'center'), col_opacity=opacity)
            txt_clip = txt_col.set_pos([30, h - 90]).set_duration(dur_per_clip)

            txt_clip2 = TextClip(split_2, fontsize=fontsize, font="Helvetica-Bold", color='white')
            txt_col2 = txt_clip2.on_color(size=(clip.w + txt_clip2.w, txt_clip2.h + 10), color=(204, 0, 255),
                                          pos=(6, 'center'), col_opacity=opacity)
            txt_clip2 = txt_col2.set_pos([50, h - 60]).set_duration(dur_per_clip)

            if split_3 is not None:
                txt_clip3 = TextClip(split_3, fontsize=fontsize, font="Helvetica-Bold", color='white')
                txt_col3 = txt_clip3.on_color(size=(clip.w + txt_clip3.w, txt_clip3.h + 10), color=(255, 255, 102),
                                              pos=(6, 'center'), col_opacity=opacity)
                txt_clip3 = txt_col3.set_pos([70, h - 30]).set_duration(dur_per_clip)

                return CompositeVideoClip([clip, txt_clip, txt_clip2, txt_clip3])

            return CompositeVideoClip([clip, txt_clip, txt_clip2])



        else:
            txt_clip = TextClip(text, size=([1700, 0]), font="Helvetica-Bold", color='white')
            txt_clip = txt_clip.set_pos([]).set_duration(dur_per_clip)
            im_width, im_height = txt_clip.size

            color_clip = ColorClip(size=(int(im_width * 1.1), int(im_height * 1.4)),
                                   color=(0, 255, 255))
            color_clip = color_clip.set_opacity(.6).set_duration(dur_per_clip).set_pos('center')

            return CompositeVideoClip([clip, color_clip, txt_clip])

    def get_vids_per_sentence(text, keywords):
        sentences = tokenize.sent_tokenize(text)
        m_paths = []
        for sent in sentences:
            if len(sent) > 1:
                def words_in_string(word_list, a_string):
                    return list(set(word_list).intersection(a_string.split()))

                vid_key = words_in_string(keywords, sent)

                m_keys = []
                for m in mov_paths:
                    if any(word in m for word in vid_key):
                        m_keys.append(m)

                try:
                    m_paths.append(random.sample(m_keys, 1))
                except ValueError:
                    pass
        else:
            pass

        return m_paths, sentences

    mov_paths_on_key, texts = get_vids_per_sentence(text, keywords)
    mov_paths_on_key = [item for sublist in mov_paths_on_key for item in sublist]

    clips = [clip_vid(path) for path in mov_paths_on_key]
    len_clips = len(clips)
    sub_final = concatenate_videoclips(clips, method='compose')

    clips_reso = clip_full(sub_final, len_clips)
    clips_add_text = [add_text(clip, texts[idx]) for idx, clip in enumerate(clips_reso)]
    final = concatenate_videoclips(clips_add_text)

    final.write_videofile(os.path.join(save_dir, 'gen_file', 'output.mp4'))
