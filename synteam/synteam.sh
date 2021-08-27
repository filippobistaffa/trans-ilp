#!/bin/bash

pool="instances_journal_final/synteam_210_true.json"
task="instances_journal_final/task_english"
instances=20

./syn_team_journal -i_all_stud $pool -i_task $task -n_agents $1 -teamsize $2 -n_subsets $instances
