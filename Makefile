.SILENT:
.ONESHELL:
.PHONY: help setup setup_train setup_cad setup_lychee render_parts \
        lint lint_links type_check test test_rerun validate quick_validate \
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

setup_cad: ## Install CAD dependencies (cadquery, requires Python 3.10-3.12)
	uv sync --group cad

render_parts: ## Generate STL + SVG from CadQuery scripts (requires setup_cad)
	@for f in hardware/cad/*.py; do echo "Rendering $$f..."; uv run --group cad python "$$f"; done

setup_rtk: ## Install RTK CLI for token-optimized LLM output
	@if command -v rtk > /dev/null 2>&1; then echo "rtk already installed: $$(rtk --version)"; \
	else curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh; fi
	rtk init -g

# MARK: dev
lint: ## Format and lint with ruff
	uv run ruff format . && uv run ruff check . --fix

lint_links: ## Check links with lychee
	@if command -v lychee > /dev/null 2>&1; then lychee --config .lychee.toml .; \
	else echo "lychee not installed — run: make setup_lychee"; fi

setup_lychee: ## Install lychee link checker
	@if command -v lychee > /dev/null 2>&1; then echo "lychee already installed: $$(lychee --version)"; \
	else curl -sSfL https://github.com/lycheeverse/lychee/releases/latest/download/lychee-x86_64-unknown-linux-gnu.tar.gz | tar xz -C /usr/local/bin 2>/dev/null \
	|| echo "Install failed — download manually from https://github.com/lycheeverse/lychee/releases"; fi

type_check: ## Run pyright type checking
	uv run pyright src

test: ## Run all tests with pytest
	uv run pytest

test_rerun: ## Rerun last failed tests only
	uv run pytest --lf -x

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
