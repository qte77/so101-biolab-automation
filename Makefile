.SILENT:
.ONESHELL:
.PHONY: help setup setup_train lint type_check test validate quick_validate \
        calibrate teleop record train eval serve demo

# MARK: config
LEADER_PORT ?= /dev/ttyACM0
FOLLOWER_A_PORT ?= /dev/ttyACM1
FOLLOWER_B_PORT ?= /dev/ttyACM2
HF_USER ?= $(shell hf auth whoami 2>/dev/null | head -n 1)
DATASET ?= $(HF_USER)/so101-biolab-pipetting
TASK ?= "Pick up pipette tip and aspirate from well A1"
NUM_EPISODES ?= 10
POLICY ?= act

# MARK: setup
help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage: make <target>\n\n"} \
		/^[a-zA-Z_-]+:.*##/ {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Install dev + test dependencies
	uv sync

setup_train: ## Install training dependencies (torch, wandb)
	uv sync --group train


# MARK: dev
lint: ## Format and lint with ruff
	uv run ruff format . && uv run ruff check . --fix

type_check: ## Run pyright type checking
	uv run pyright src

test: ## Run all tests with pytest
	uv run pytest

quick_validate: lint type_check ## Fast validation (lint + type check)

validate: lint type_check test ## Full validation (lint + type check + test)

# MARK: hardware
calibrate: ## Calibrate all arms
	lerobot-calibrate --robot.type=so101_follower --robot.port=$(FOLLOWER_A_PORT) --robot.id=arm_a
	lerobot-calibrate --robot.type=so101_follower --robot.port=$(FOLLOWER_B_PORT) --robot.id=arm_b
	lerobot-calibrate --teleop.type=so101_leader --teleop.port=$(LEADER_PORT) --teleop.id=leader

teleop: ## Start teleoperation (leader → follower)
	lerobot-teleoperate \
		--robot.type=so101_follower \
		--robot.port=$(FOLLOWER_A_PORT) \
		--robot.id=arm_a \
		--robot.cameras="{ overhead: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
		--teleop.type=so101_leader \
		--teleop.port=$(LEADER_PORT) \
		--teleop.id=leader \
		--display_data=true

record: ## Record teleoperation episodes
	lerobot-record \
		--robot.type=so101_follower \
		--robot.port=$(FOLLOWER_A_PORT) \
		--robot.id=arm_a \
		--robot.cameras="{ overhead: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
		--teleop.type=so101_leader \
		--teleop.port=$(LEADER_PORT) \
		--teleop.id=leader \
		--dataset.repo_id=$(DATASET) \
		--dataset.num_episodes=$(NUM_EPISODES) \
		--dataset.single_task=$(TASK) \
		--dataset.streaming_encoding=true \
		--display_data=true

train: ## Train policy on recorded data
	lerobot-train \
		--dataset.repo_id=$(DATASET) \
		--policy.type=$(POLICY) \
		--output_dir=outputs/train/$(POLICY)_biolab \
		--job_name=$(POLICY)_biolab \
		--policy.device=cuda \
		--wandb.enable=true

# MARK: app
eval: ## Evaluate trained policy
	python scripts/run_demo.py --mode=eval --arm-port=$(FOLLOWER_A_PORT)

serve: ## Start remote dashboard
	uvicorn src.dashboard.server:app --host 0.0.0.0 --port 8080 --reload

demo: ## Run full demo pipeline
	python scripts/run_demo.py --mode=full
