from expyriment import design, control, stimuli
from expyriment.misc.constants import C_WHITE, C_BLACK, K_j, K_f
import os
from counterbalancing import *
from stimuli_generation import *


""" Constants """
DEMO = True
KEYS = [K_f, K_j]
KEYS_TO_MAPPING = [{K_f:True, K_j:False}, {K_f:False, K_j:True}]
WD = os.path.dirname(os.path.abspath(__file__))
PICTURES_FOLDER = os.path.join(WD, 'stimuli')
MASKS_FOLDER = os.path.join(WD, 'masks')
PICTURES_LIST = [f for f in os.listdir(PICTURES_FOLDER) if f.endswith(('.jpg', '.jpeg'))]
MASK_LIST = [os.path.join(MASKS_FOLDER, f) for f in os.listdir(MASKS_FOLDER) if f.endswith(('.jpg', '.jpeg'))]
QUADRANT_MAPPING = {1:(-165, 115), 
                    2:(165, 115), 
                    3:(165, -115), 
                    4:(-165, -115)}
N_BLOCKS = 15
N_TRIALS = 5 * N_BLOCKS
N_PRACTICE_TRIALS = 3
TRIAL_SIZE = 6
PICTURES_PER_RSVP = 8
PICTURES_PER_TRIAL = 12

end_instructions = "Thank you for participating in our task!"

""" Helper functions """

def timed_draw(stims):
    t0 = exp.clock.time
    exp.screen.clear()
    for stim in stims:
        stim.present(clear=False, update=False)
    exp.screen.update()
    t1 = exp.clock.time
    return t1 - t0

def present_for(stims, t=1000):
    dt = timed_draw(stims)
    exp.clock.wait(t - dt)

def present_instructions(text):
    instructions = stimuli.TextScreen(text=text, text_justification=0, heading="Instructions")
    instructions.present()
    exp.keyboard.wait()

def get_trials(subject_id):
    pres_times = get_pres_times(N_TRIALS)
    pictures_ids = get_pictures(len(PICTURES_LIST),PICTURES_PER_TRIAL,N_TRIALS,subject_id)
    rsvp_orders = get_rsvps(N_BLOCKS,TRIAL_SIZE,PICTURES_PER_RSVP)
    trials = {}
    for i in range(N_TRIALS):
        trials[i+1] = {'dur': pres_times[i],
                       'rsvp_pics': pictures_ids[i+1][0] + pictures_ids[i+1][1],
                       'test_pics': pictures_ids[i+1][1],
                       'distractors': pictures_ids[i+1][2],
                       'rsvp': rsvp_orders[i]}
    return trials

def get_start_instructions(subject_key_map):
    start_instructions = f"""
    In this task, each trial will have the following structure:\n
    1. A white fixation cross will appear on the screen:\n
    Stare at it when it is present!\n
    2. A volley of eight windows with 0-4 pictures will appear in rapid succession\n
    3. After the volley, you will be tested on another eight pictures one by one:\n
    The test will begin without a warning. Your goal is to indicate whether each test picture was in the initial volley or not. Press 'F' if it was {'present' if subject_key_map[K_f] else 'absent'} and 'J' if it was {'present' if subject_key_map[K_j] else 'absent'}.\n
    There will be three practice trials at the very beginning. Press 'SPACE' when you are ready to begin.
    """
    return start_instructions

def get_mid_instructions(subject_key_map):
    mid_instructions = f"""
    Good job! The remaining trials will follow the exact same structure.\n
    Reminder:\n
    Press 'F' if you believe a test picture was {'present' if subject_key_map[K_f] else 'absent'} in the rapid volley preceding it or 'J' if you believe it was {'present' if subject_key_map[K_j] else 'absent'}.\n
    Press 'SPACE' when you are ready to begin.
    """
    return mid_instructions

""" Global settings """
exp = design.Experiment(name="RSVP Memory Test", background_colour=C_BLACK, foreground_colour=C_WHITE)
exp.add_data_variable_names(['subject_id','trial_n', 'trial_type', 'n_stims', 'stim_position', 'filename', 'pres_time', 'RT', 'correct'])

#control.set_develop_mode()
control.initialize(exp)

""" Stimulus Constants """
FIXATION = stimuli.FixCross(colour=C_WHITE)

""" Experiment """
def run_trial(trial_num, trial, subject_key_map):
    rsvp_frames, test_frames = generate_stims(trial, PICTURES_LIST, MASK_LIST, PICTURES_FOLDER, QUADRANT_MAPPING, FIXATION)
    present_for([FIXATION], 500)
    #RSVP
    for frame in rsvp_frames:
        present_for(frame, trial['dur'])
    exp.clock.wait(200)
    #Test
    for frame in test_frames.keys():
        present_for([frame], 400)
        exp.screen.clear()
        exp.screen.update()
        key, rt = exp.keyboard.wait(KEYS)
        correct = subject_key_map[key] == test_frames[frame]['test']
        exp.data.add([exp.subject, trial_num, test_frames[frame]['test'], test_frames[frame]['total_stims'], test_frames[frame]['quad'], test_frames[frame]['file'], trial['dur'], rt, correct])

control.start()

subject_key_map = KEYS_TO_MAPPING[(exp.subject-1) % 2]

present_instructions(get_start_instructions(subject_key_map))

for trial_num, trial in get_trials(exp.subject).items():
    if DEMO and trial_num > 4:
        break
    if trial_num == N_PRACTICE_TRIALS + 1:
        present_instructions(get_mid_instructions(subject_key_map))
    run_trial(trial_num, trial, subject_key_map)

present_instructions(end_instructions)

control.end()