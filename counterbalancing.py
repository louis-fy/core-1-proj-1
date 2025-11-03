import itertools, random
from math import lcm
from collections import Counter

N_VALUES = [0, 1, 2, 3, 4] #N: number of pictures shown each frame
N_RATIOS = {1:4, 2:3, 3:2, 4:1} #the ratio of N values in all trials
PRESENTATION_TIMES = [240, 400, 720]

def get_pres_times(n_trials):
    trials = []
    for _ in range(int(n_trials / len(PRESENTATION_TIMES))):
        trials += random.sample(PRESENTATION_TIMES, len(PRESENTATION_TIMES))
    return trials

def get_perm(trials):
    latin_sq = list(itertools.permutations([0,1,2]))
    for n, trial in trials.items():
        trials[n] = [trial[i] for i in latin_sq[(n - 1) % len(latin_sq)]]
    return trials

def get_pictures(n_pictures, pictures_per_trial, n_trials, subject_id):
    cat_length = pictures_per_trial // 3
    total_pictures_multiplier = lcm(n_pictures, pictures_per_trial) / n_pictures
    picture_ids = list(range(n_pictures)) * int(total_pictures_multiplier)
    temp_trials = []
    for start in range(0, len(picture_ids), pictures_per_trial):
        temp_trials.append([picture_ids[start:start+cat_length],
                            picture_ids[start+cat_length:start+(cat_length*2)],
                            picture_ids[start+(cat_length*2):start+pictures_per_trial]])

    total_trials_multiplier = lcm(n_trials, len(temp_trials)) / len(temp_trials)
    all_trials = temp_trials * int(total_trials_multiplier)
    trials_by_subject = {}
    n = 0
    for start in range(0, len(all_trials), n_trials):
        trials_by_subject[n] = {i:trial for i, trial in enumerate(all_trials[start:start+n_trials], 1)}
        n += 1
    
    cur_trials = get_perm(trials_by_subject[(subject_id-1) % len(trials_by_subject)])

    return cur_trials

def get_rsvps(N_BLOCKS, TRIAL_SIZE, PICTURES_PER_RSVP):
    #list all possible trial type
    all_possible = itertools.product(N_VALUES, repeat=TRIAL_SIZE)#create all possible combinations of N_values
    valid_trials = [trial for trial in all_possible if sum(trial) == PICTURES_PER_RSVP]#951 trials in total,filter combinations whose sum is 8
    unique_valid_trials = set(tuple(sorted(trial)) for trial in valid_trials)#13 trials after removing duplicated combination
    #print(unique_valid_trials)


    ###Define the minimum trials assignment unit we need(except quarderants)
    # Calculate how many trials we need to meet the ratio requirement
    total_pictures_ratio_need = sum(n * N_RATIOS[n] for n in N_RATIOS) #20
    min_trials = lcm(total_pictures_ratio_need, PICTURES_PER_RSVP)/PICTURES_PER_RSVP #40/8 = 5!
    min_ratios = lcm(total_pictures_ratio_need, PICTURES_PER_RSVP)/total_pictures_ratio_need #40/20 = 2
    min_frames = min_trials * TRIAL_SIZE #5*6=30

    n_ratios_per_block = {k:int(v * min_ratios) for k, v in N_RATIOS.items()}
    total_positive_frames = sum(n_ratios_per_block.values()) #20
    n_ratios_per_block[0] = int(min_frames - total_positive_frames) #Adding 0:10

    search_space = itertools.combinations_with_replacement(list(unique_valid_trials), int(min_trials))
    found_target_block = []
    for combo in search_space:
        all_n_values_in_combo = itertools.chain.from_iterable(combo)
        combo_counts = Counter(all_n_values_in_combo)
        if combo_counts == n_ratios_per_block:
            found_target_block.append(combo)

    block = found_target_block[0] # First of 61 types of blocks found

    ### Consider quadrants, same logic, lcm them assign
    #Possible assignments of quadrants for each N
    possible_N = {n: list(itertools.combinations([1, 2, 3, 4], n)) for n in N_VALUES}
    experiment_pools = {}
    for n in N_VALUES:
        base_pool = possible_N[n] * (n_ratios_per_block[n] // len(possible_N[n]))
        total_pool = base_pool * N_BLOCKS
        random.shuffle(total_pool)
        experiment_pools[n] = total_pool
    block_prototype_pool = list(block) * N_BLOCKS
    random.shuffle(block_prototype_pool)

    final_experiment_sequence = []
    for block_prototype in block_prototype_pool:
        n_values_list = list(block_prototype)
        random.shuffle(n_values_list)
        final_trial_frames = [experiment_pools[n].pop() for n in n_values_list]
        final_experiment_sequence.append(tuple(final_trial_frames))
    
    return final_experiment_sequence