import itertools
import random
from math import lcm
from collections import Counter
N_BLOCKS = 15  #total_trials = N_BLOCKS * 5 |USE THIS TO CONTROL NUMBER OF TRIALS|
N_values = [0, 1, 2, 3, 4] #N: number of pictures shown each frame
ratio_N = {1:4, 2:3, 3:2, 4:1} #the ratio of N values in all trials
trial_size = 6 #each trial has 6 frames
picture_per_trial = 8
quadrants = [1, 2, 3, 4]

#list all possible trial type
all_possible = itertools.product(N_values, repeat=trial_size)#creat all possible combinations of N_values
valid_trials = [trial for trial in all_possible if sum(trial) == picture_per_trial]#951 trials in total,filter combinations whose sum is 8
unique_valid_trials = set(tuple(sorted(trial)) for trial in valid_trials)#13 trials after removing duplicated combination

print(unique_valid_trials)
print(f"Total valid trials: {len(unique_valid_trials)}")


###Define the minimum trials assignment unit we need(except quarderants)
# Calculate how many trials we need to meet the ratio requirement 
total_ratio = sum(ratio_N.values()) #10
total_pictures_ratio_need = sum(n * ratio_N[n] for n in ratio_N) #20
num_trial_we_need = lcm(total_pictures_ratio_need, picture_per_trial)/picture_per_trial #40/8 = 5!
num_ratio_we_need = lcm(total_pictures_ratio_need, picture_per_trial)/total_pictures_ratio_need #40/20 = 2
print("num_ratio_we_need:", num_ratio_we_need,"num_trial_we_need:",num_trial_we_need) 
num_frames_we_need = num_trial_we_need * trial_size #5*6=30

N_should_use = {k:int(v * num_ratio_we_need) for k, v in ratio_N.items()}
total_positive_frames = sum(N_should_use.values())
N_should_use[0] = int(num_frames_we_need - total_positive_frames)
target_counter = Counter(N_should_use)

search_space = itertools.combinations_with_replacement(list(unique_valid_trials), int(num_trial_we_need))
found_target_block = []
total_combination_checked = 0
print(f"--- start searching ---")
for combo in search_space:
    total_combination_checked += 1
    all_n_values_in_combo = itertools.chain.from_iterable(combo)
    combo_counts = Counter(all_n_values_in_combo)
    if combo_counts == N_should_use:
        found_target_block.append(combo)
print(f"\n--- finish searching ---")

print("found_target_block:", len(found_target_block)) #61 types of blocks found

block = found_target_block[0]
print("Selected Block:",block)    

### Consider quadrants, same logic, lcm them assign
#Possible assignments of quadrants for each N
possible_N = {n: list(itertools.combinations(quadrants, n)) for n in range(0,5)}
experiment_pools = {}
for n in N_values:
    num_combinaions = len(possible_N[n])
    repeats_per_block = target_counter[n] // num_combinaions
    base_pool = possible_N[n] * repeats_per_block

    total_pool = base_pool * N_BLOCKS
    random.shuffle(total_pool)
    experiment_pools[n] = total_pool

block_prototype_pool = list(block) * N_BLOCKS
random.shuffle(block_prototype_pool)

final_experiment_sequence = []
# This loop runs 15 times (5 trials/block * 3 blocks)
for block_prototype in block_prototype_pool:
     n_values_list = list(block_prototype)
     random.shuffle(n_values_list)

     final_trial_frames = [
         experiment_pools[n].pop() for n in n_values_list
     ]
     final_experiment_sequence.append(tuple(final_trial_frames))

print("\nFinal Experiment Sequence:")
# This loop correctly prints only the first 5 trials
for i, trial in enumerate(final_experiment_sequence[:18]):
    print(f"Trial {i+1}: {trial}")
    for frame_num, quadrants in enumerate(trial):
        print(f"  Frame {frame_num+1}: N={len(quadrants)}, Quadrants={quadrants}")

# --- THIS BLOCK IS NOW UN-INDENTED ---
# This validation check now runs ONCE, after all trials are generated
print("\n--- Final Validation ---")
if all(len(pool)==0 for pool in experiment_pools.values()):
    print("Success: All experiment pools are empty as expected.")
else:
    print("Error: Some experiment pools are not empty, check the logic.")