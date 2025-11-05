import itertools, random
import copy
from math import lcm
from collections import Counter

random.seed(42)
N_VALUES = [0, 1, 2, 3, 4] #N: number of pictures shown each frame
N_RATIOS = {1: 12, 2: 6, 3: 4, 4: 3} #the ratio of N values in all trials
PRESENTATION_TIMES = [240, 400, 720]

### Get
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

### BUILD
def find_valid_trials():
    all_possible = itertools.product(N_VALUES, repeat=6)#create all possible combinations of N_values
    valid_trials = [trial for trial in all_possible if sum(trial) == 8]#951 trials in total,filter combinations whose sum is 8
    unique_valid_trials = set(tuple(sorted(trial)) for trial in valid_trials)#13 trials after removing duplicated combination
    return unique_valid_trials

def calculate_min_balance_blocks(TRIAL_SIZE,PICTURES_PER_RSVP, N_RATIOS):
    total_pictures_ratio_need = sum(n * N_RATIOS[n] for n in N_RATIOS) 

    min_trials = lcm(total_pictures_ratio_need, PICTURES_PER_RSVP) / PICTURES_PER_RSVP 
    min_ratios = lcm(total_pictures_ratio_need, PICTURES_PER_RSVP) / total_pictures_ratio_need
    
    min_frames = int(min_trials) * TRIAL_SIZE

    n_ratios_per_block = {k:int(v * min_ratios) for k, v in N_RATIOS.items()}
    total_positive_frames = sum(n_ratios_per_block.values())
    
    n_ratios_per_block[0] = int(min_frames - total_positive_frames)
    
    return int(min_trials), int(min_frames), n_ratios_per_block

def generate_quadrant_pools(N_VALUES, n_ratios_per_block):
    possible_N = {n: list(itertools.combinations([1, 2, 3, 4], n)) for n in N_VALUES}
    experiment_pools = {}

    for n in N_VALUES:
        n_frames_per_block = n_ratios_per_block.get(n, 0)
        
        if n_frames_per_block == 0:
            experiment_pools[n] = []
            continue

        base_pool_size = len(possible_N[n]) 
        num_repetitions = n_frames_per_block // base_pool_size 
        
        total_pool = possible_N[n] * num_repetitions
        experiment_pools[n] = total_pool
        
    return experiment_pools

def generate_one_block(block_prototype, experiment_pools):
    local_pools = {n: list(pool) for n, pool in experiment_pools.items()}
    final_block_sequence = []
    
    block_trials = list(block_prototype)
    random.shuffle(block_trials) 
    
    for trial_prototype in block_trials:
        n_values_list = list(trial_prototype)
        random.shuffle(n_values_list) 
        
        final_trial_frames = []
        for n in n_values_list:
            
            if local_pools[n]:
                quad_assignment = random.choice(local_pools[n]) 
                local_pools[n].remove(quad_assignment)
                final_trial_frames.append(quad_assignment)
            else:
                final_trial_frames.append(tuple()) 
                
        final_block_sequence.append(tuple(final_trial_frames))
        
    return final_block_sequence
    
def get_rsvps(N_BLOCKS, TRIAL_SIZE, PICTURES_PER_RSVP):
    
    min_trials, min_frames, n_ratios_per_block = calculate_min_balance_blocks(
        TRIAL_SIZE, PICTURES_PER_RSVP, N_RATIOS
    )
    unique_valid_trials = find_valid_trials()

    search_space = itertools.combinations_with_replacement(list(unique_valid_trials), min_trials)
    found_target_block = []
    for combo in search_space:
        all_n_values_in_combo = itertools.chain.from_iterable(combo)
        combo_counts = Counter(all_n_values_in_combo)
        if combo_counts == n_ratios_per_block:
            found_target_block.append(combo)
            
    block_prototype = random.choice(found_target_block) # randomly choose one block prototype

    # Generate pools and the full N/Quadrant sequence
    pools_for_single_block = generate_quadrant_pools(N_VALUES, n_ratios_per_block)
    
    full_rsvp_sequence = []
    for _ in range(N_BLOCKS):
        pools_copy = copy.deepcopy(pools_for_single_block)
        
        block_sequence = generate_one_block(
            block_prototype, 
            pools_copy
        )
        full_rsvp_sequence.extend(block_sequence)

    # Bind Duration (Time Cross-Balance)
    
    n_rsvp_sequences = len(full_rsvp_sequence)
    n_durations = len(PRESENTATION_TIMES)
    n_trials_total = int(lcm(n_rsvp_sequences, n_durations)) 
    
    duration_sequence = get_pres_times(n_trials_total)
    rsvp_multiplier = int(n_trials_total / n_rsvp_sequences)
    extended_rsvp_sequences = full_rsvp_sequence * rsvp_multiplier
    
    combined_trials_list = []
    for i in range(n_trials_total):
        combined_trials_list.append({
            'rsvp_seq': extended_rsvp_sequences[i],
            'dur': duration_sequence[i]
        })
    
    random.shuffle(combined_trials_list) 
    
    # Return the combined, balanced sequence and the total trial count
    return combined_trials_list, n_trials_total