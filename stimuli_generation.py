from expyriment import stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK
import random, os

def load(stims):
    for stim in stims:
        stim.preload()

def get_rsvp(fixation, rsvp_files, mask_files, frame_list, source_folder, quad_map):
    lookup_conds = {}
    frames = [[fixation] + [
        stimuli.Picture(random.choice(mask_files), position=quad_map[quadrant])
        for quadrant in quad_map.keys()
    ]]

    for frame in frame_list:
        stims = [fixation]
        for quadrant in frame:
            picture_file = rsvp_files.pop()
            stims.append(stimuli.Picture(os.path.join(source_folder, picture_file), 
                                  position=quad_map[quadrant]))
            lookup_conds[picture_file] = {'quad': quadrant, 'total_stims': len(frame)}
        # Masks
        for quadrant in quad_map.keys():
            if quadrant not in frame:
                stims.append(stimuli.Picture(random.choice(mask_files), 
                                            position=quad_map[quadrant]))
        frames.append(stims)
    
    frames.append([fixation] + [
        stimuli.Picture(random.choice(mask_files), position=quad_map[quadrant])
        for quadrant in quad_map.keys()
    ])
    
    return frames, lookup_conds

def get_test(test_files, distractor_files, source_folder, lookup_conds):
    frames = {}
    all_files = test_files + distractor_files
    random.shuffle(all_files)
    for file in all_files:
        frames[stimuli.Picture(os.path.join(source_folder, file),(0,0))] = {'file': file,
                                                                            'test': True if file in test_files else False,
                                                                            'quad': lookup_conds[file]['quad'] if file in test_files else 'NA',
                                                                            'total_stims': lookup_conds[file]['total_stims'] if file in test_files else 'NA'}
    return frames

def generate_stims(trial_settings, pictures_list, mask_files, source_folder, quad_map, fixation):
    rsvp_files = [pictures_list[id] for id in trial_settings['rsvp_pics']]
    random.shuffle(rsvp_files)
    test_files = [pictures_list[id] for id in trial_settings['test_pics']]
    random.shuffle(test_files)
    distractors = [pictures_list[id] for id in trial_settings['distractors']]
    random.shuffle(distractors)
   
    rsvp_frames, lookup_conds = get_rsvp(fixation, rsvp_files, mask_files, trial_settings['rsvp'], source_folder, quad_map)
    test_frames = get_test(test_files, distractors, source_folder, lookup_conds)

    load([e for frame in rsvp_frames for e in frame] + list(test_frames.keys()))
    
    return rsvp_frames, test_frames