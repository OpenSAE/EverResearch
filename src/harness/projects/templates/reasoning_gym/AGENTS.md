<!-- everresearch:search -->
## Locate projects and files

Start with known registrations and explicit paths when locating a project, command, or configuration. When you need a broader search, list the immediate directories first and pick specific paths. Limit routine recursive searches to active source material. Search local workspace output, historical snapshots, experiment results, or caches by explicitly naming the required files or directories and limiting the output.
<!-- /everresearch:search -->

<!-- everresearch:mode -->
## Choose the maintenance mode

### Purpose and main functions

Use the project setting to select its maintenance guide and structure checker.

### Scope

Use this section for project maintenance, checking the online connection, or running an offline structure check.

Start by reading `.everresearch/mode.toml`. Its `enabled` setting selects this project's maintenance mode. Follow the user's choice and obtain authorization before changing it.

- **`enabled = false` selects offline maintenance.** Use the project's [offline operations guide](.everresearch/offline/operations.md). It explains how to plan, carry out, and finish maintenance using the project's files, commands, tests, and data.
- **`enabled = true` selects online maintenance.** Run `python -IS .everresearch/maintain.py status` first. When it prints `online`, read the central guide at the reported path. Follow that guide to the operations manual, shared skills, and central checks in the EverResearch repository. If the status command fails, report the cause and pause work that requires central maintenance until the user restores the connection or selects offline mode.
- **A missing or invalid setting blocks maintenance.** Report the problem and continue once the setting has been corrected or the user has chosen a mode.

When a structure check is authorized, run `python -IS .everresearch/maintain.py check` from the project root. The command runs the checker for the selected mode. Follow the project README for installation, training, prechecks, and reading results.
<!-- /everresearch:mode -->

## Original project and template layout

- **Original project** [Reasoning Gym](https://github.com/open-thought/reasoning-gym)
- **Source revision** [`5aea50d292a6`](https://github.com/open-thought/reasoning-gym/tree/5aea50d292a6427f12c63c77873ec8ae945cd2c0)
- **Paper** [Reasoning Gym: Reasoning Environments for Reinforcement Learning with Verifiable Rewards](https://proceedings.neurips.cc/paper_files/paper/2025/hash/528d56195a2c77c808494c86fa7c77ad-Abstract-Datasets_and_Benchmarks_Track.html) · NeurIPS 2025 Spotlight (Datasets and Benchmarks Track)
- **Authors** Zafir Stojanovski, Oliver Stanley, Joe Sharratt, Richard Jones, Abdulhakeem Adefioye, Jean Kaddour, Andreas Köpf
- **Original source archive** [reasoning_gym.zip](third_party/upstream/reasoning_gym.zip)
- **Archive SHA-256** `d05197b8d5bb040712aae92d603ad5672731c0550fb86bfd69da8468a1321f30`

### Before organization

```text
reasoning-gym/
├── .gitattributes
├── .github/
│   └── workflows/
├── .gitignore
├── .pre-commit-config.yaml
├── CONTRIBUTING.md
├── GALLERY.md
├── LICENSE
├── NOTICE.txt
├── README.md
├── assets/
│   ├── examples.png
│   └── icon.png
├── eval/
│   ├── .gitignore
│   ├── README.md
│   ├── dry_run.py
│   ├── eval.py
│   ├── eval_config.py
│   ├── example_config.json
│   ├── example_config.yaml
│   ├── generate_config.py
│   ├── requirements-eval.txt
│   ├── visualize_results.py
│   └── yaml/
├── examples/
│   ├── trl/
│   ├── unsloth/
│   ├── veRL/
│   └── verifiers/
├── notebooks/
│   ├── check-collisions-in-reasoning-gym-dataset.ipynb
│   ├── codeio/
│   ├── codeio.ipynb
│   ├── collisions/
│   ├── generate_anagrams.ipynb
│   ├── gsm-symbolic-cot.txt
│   ├── gsm_symbolic.ipynb
│   ├── plot_curriculum.ipynb
│   ├── test_generator_files.py
│   └── verify_gsm_symbolic.ipynb
├── pyproject.toml
├── reasoning_gym/
│   ├── __init__.py
│   ├── algebra/
│   ├── algorithmic/
│   ├── arc/
│   ├── arithmetic/
│   ├── coaching/
│   ├── code/
│   ├── cognition/
│   ├── composite.py
│   ├── data/
│   ├── dataset.py
│   ├── factory.py
│   ├── games/
│   ├── geometry/
│   ├── graphs/
│   ├── induction/
│   ├── logic/
│   ├── probability/
│   ├── scoring.py
│   ├── utils.py
│   └── version_manager.py
├── requirements-dev.txt
├── scripts/
│   ├── debug_curricula.py
│   ├── generate_gallery.py
│   └── hf_dataset/
├── tests/
│   ├── __init__.py
│   ├── coaching/
│   ├── test_ab.py
│   ├── test_acre.py
│   ├── test_advanced_geometry.py
│   ├── test_aiw.py
│   ├── test_arc_1d.py
│   ├── test_arc_1d_tasks.py
│   ├── test_arc_agi.py
│   ├── test_base_conversion.py
│   ├── test_basic_arithmetic.py
│   ├── test_bf.py
│   ├── test_binary_alternation.py
│   ├── test_binary_matrix.py
│   ├── test_bitwise_arithmetic.py
│   ├── test_boxnet.py
│   ├── test_caesar_cipher.py
│   ├── test_calendar_arithmetic.py
│   ├── test_chain_sum.py
│   ├── test_circuit_logic.py
│   ├── test_codeio.py
│   ├── test_coin_flip.py
│   ├── test_color_cube_rotation.py
│   ├── test_complex_arithmetic.py
│   ├── test_composite.py
│   ├── test_count_bits.py
│   ├── test_count_primes.py
│   ├── test_countdown.py
│   ├── test_course_schedule.py
│   ├── test_cryptarithm.py
│   ├── test_dataset.py
│   ├── test_dataset_common.py
│   ├── test_decimal_arithmetic.py
│   ├── test_decimal_chain_sum.py
│   ├── test_dice.py
│   ├── test_emoji_mystery.py
│   ├── test_family_relationships.py
│   ├── test_figlet_fonts.py
│   ├── test_fraction_simplification.py
│   ├── test_futoshiki.py
│   ├── test_game_of_life.py
│   ├── test_game_of_life_halting.py
│   ├── test_gcd.py
│   ├── test_get_score_answer_fn.py
│   ├── test_graph_color.py
│   ├── test_group_anagrams.py
│   ├── test_gsm_symbolic.py
│   ├── test_intermediate_integration.py
│   ├── test_isomorphic_strings.py
│   ├── test_jugs.py
│   ├── test_kakurasu.py
│   ├── test_knight_swap.py
│   ├── test_knights_knaves.py
│   ├── test_largest_island.py
│   ├── test_lcm.py
│   ├── test_leg_counting.py
│   ├── test_letter_counting.py
│   ├── test_letter_jumble.py
│   ├── test_list_functions.py
│   ├── test_mahjong_puzzle.py
│   ├── test_manipulate_matrix.py
│   ├── test_maze.py
│   ├── test_mini_sudoku.py
│   ├── test_modulo_grid.py
│   ├── test_n_queens.py
│   ├── test_needle_haystack.py
│   ├── test_number_filtering.py
│   ├── test_number_format.py
│   ├── test_number_sequences.py
│   ├── test_number_sorting.py
│   ├── test_palindrome.py
│   ├── test_palindrome_partitioning.py
│   ├── test_path_star.py
│   ├── test_polynomial_equations.py
│   ├── test_polynomial_multiplication.py
│   ├── test_pool_matrix.py
│   ├── test_power_function.py
│   ├── test_prime_factorization.py
│   ├── test_products.py
│   ├── test_propositional_logic.py
│   ├── test_puzzle24.py
│   ├── test_quantum_lock.py
│   ├── test_ransom_note.py
│   ├── test_rearc.py
│   ├── test_rectangle_count.py
│   ├── test_rotate_matrix.py
│   ├── test_rotten_oranges.py
│   ├── test_rubiks_cube.py
│   ├── test_rush_hour.py
│   ├── test_score_board.py
│   ├── test_scoring.py
│   ├── test_self_reference.py
│   ├── test_sentence_reordering.py
│   ├── test_shortest_path.py
│   ├── test_simple_equations.py
│   ├── test_simple_geometry.py
│   ├── test_simple_integration.py
│   ├── test_sokoban.py
│   ├── test_spell_backward.py
│   ├── test_spiral_matrix.py
│   ├── test_string_insertion.py
│   ├── test_string_manipulation.py
│   ├── test_string_splitting.py
│   ├── test_string_synthesis.py
│   ├── test_sudoku.py
│   ├── test_survo.py
│   ├── test_syllogisms.py
│   ├── test_time_intervals.py
│   ├── test_tower_of_hanoi.py
│   ├── test_tsumego.py
│   ├── test_utils.py
│   ├── test_word_ladder.py
│   ├── test_word_sequence_reversal.py
│   ├── test_word_sorting.py
│   └── test_zebra.py
├── tools/
│   ├── README.md
│   ├── cli/
│   └── server/
└── training/
    ├── README.md
    ├── configs/
    ├── evaluations/
    ├── rewards/
    ├── train_grpo.py
    ├── trainers/
    └── utils/
```

### After organization

```text
reasoning_gym/
├── .everresearch/
│   ├── maintain.py
│   ├── mode.toml
│   └── offline/
├── .gitattributes
├── .gitignore
├── .pre-commit-config.yaml
├── AGENTS.md
├── CONTRIBUTING.md
├── LICENSE
├── NOTICE.txt
├── README.md
├── assets/
│   ├── images/
│   ├── prepared_data/
│   ├── recipes/
│   └── reports/
├── base/
│   ├── reasoning_gym/
│   └── tools/
├── conf/
│   ├── config.yaml
│   └── tasks/
├── datasets/
│   ├── algebra/
│   ├── algorithmic/
│   ├── arc/
│   ├── arithmetic/
│   ├── code/
│   ├── cognition/
│   ├── data/
│   ├── games/
│   ├── geometry/
│   ├── graphs/
│   ├── induction/
│   ├── logic/
│   ├── probability/
│   ├── procedural/
│   └── training_rows/
├── doc/
│   ├── README.md
│   ├── code/
│   ├── environment/
│   ├── experiment.md
│   ├── knowledge/
│   └── maintenance.md
├── main.py
├── models/
│   ├── local_inference/
│   ├── remote_api/
│   └── training_checkpoint/
├── pyproject.toml
├── requirements_dev.txt
├── requirements_evaluation.txt
├── requirements_unsloth.txt
├── requirements_verifiers.txt
├── scripts/
│   ├── checkpoints/
│   ├── debug_curricula.py
│   ├── evaluation/
│   ├── examples/
│   ├── generate_gallery.py
│   ├── hf_dataset/
│   └── notebooks/
├── tasks/
│   ├── evaluation/
│   ├── local_evaluation/
│   ├── precheck/
│   └── training/
├── tests/
│   ├── __init__.py
│   ├── integration/
│   ├── product/
│   └── test_gsm_symbolic.py
└── third_party/
    ├── README.md
    ├── bfit/
    ├── logic_puzzle/
    ├── rearc_generators/
    ├── sokoban/
    └── upstream/
        └── reasoning_gym.zip
```
