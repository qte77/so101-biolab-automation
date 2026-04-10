# Requires GNU Make >= 3.82 for .ONESHELL
# macOS ships 3.81 as of Sequoia 15.4 (2025-03, Apple avoids GPLv3).
# Ref: https://opensource.apple.com/releases/ (validated 2026-04-10)
# Fix: brew install make → use gmake (not make)
ifeq ($(filter oneshell,$(.FEATURES)),)
$(error GNU Make >= 3.82 required. macOS: brew install make, then use gmake)
endif

.SILENT:
.ONESHELL:
.PHONY: \
	setup_uv setup_dev setup_all setup_train setup_cad setup_scad setup_slicer setup_rtk setup_lychee \
	render_wireframe render_solid check_prints render_all \
	lint_code check_links check_types run_tests rerun_tests quick_validate validate \
	calibrate_arms start_teleop record_episodes train_policy \
	eval_policy serve_dashboard run_demo \
	help
.DEFAULT_GOAL := help


# -- config --
VERBOSE ?= 0
ifeq ($(VERBOSE),0)
RUFF_QUIET := --quiet
PYTEST_QUIET := -q --tb=short --no-header
PYRIGHT_QUIET := > /dev/null
else
RUFF_QUIET :=
PYTEST_QUIET :=
PYRIGHT_QUIET :=
endif

LEADER_PORT ?= /dev/ttyACM0
FOLLOWER_A_PORT ?= /dev/ttyACM1
FOLLOWER_B_PORT ?= /dev/ttyACM2
HF_USER ?= $(shell hf auth whoami 2>/dev/null | head -n 1)
DATASET ?= $(HF_USER)/so101-biolab-pipetting
TASK ?= "Pick up pipette tip and aspirate from well A1"
NUM_EPISODES ?= 10
POLICY ?= act


# MARK: SETUP


setup_uv: ## Install uv package manager (if missing)
	if command -v uv > /dev/null 2>&1; then
		echo "uv already installed: $$(uv --version)"
	else
		echo "Installing uv ..."
		curl -LsSf https://astral.sh/uv/install.sh | sh
		echo ""
		echo "NOTE: restart your shell or run 'source $$HOME/.local/bin/env' to add uv to PATH"
	fi

setup_dev: setup_uv ## Install dev + test dependencies
	uv sync

setup_all: setup_dev setup_cad ## Install all dependencies + tools
	-$(MAKE) setup_slicer
	-$(MAKE) setup_lychee

## setup_train: setup_uv  # Uncomment when GPU available
##	uv sync --group train

setup_cad: setup_uv ## Install build123d for BREP CAD generation
	uv sync --group cad

setup_scad: ## Install OpenSCAD for parametric STL generation
	if command -v openscad > /dev/null 2>&1; then
		echo "openscad already installed: $$(openscad --version 2>&1 | head -1)"
	else
		echo "Installing OpenSCAD ..."
		if command -v apt-get > /dev/null 2>&1; then
			sudo apt-get update -qq && sudo apt-get install -y -qq openscad
		elif command -v brew > /dev/null 2>&1; then
			brew install openscad
		elif command -v snap > /dev/null 2>&1; then
			sudo snap install openscad
		else
			echo "ERROR: No supported package manager found. Install manually: https://openscad.org/downloads"
			exit 1
		fi
	fi

setup_slicer: ## Install CuraEngine (preferred) or PrusaSlicer (fallback) for printability validation
	if command -v CuraEngine > /dev/null 2>&1; then
		echo "CuraEngine already installed: $$(CuraEngine --version 2>&1 | head -1)"
	elif command -v prusa-slicer > /dev/null 2>&1; then
		echo "PrusaSlicer already installed: $$(prusa-slicer --version 2>&1 | head -1)"
	else
		echo "Installing CuraEngine (headless slicer) ..."
		if command -v dnf > /dev/null 2>&1; then
			sudo dnf install -y curaengine \
				|| { echo "CuraEngine unavailable, trying PrusaSlicer ..."; sudo dnf install -y prusa-slicer; }
		elif command -v apt-get > /dev/null 2>&1; then
			sudo apt-get update -qq && sudo apt-get install -y -qq curaengine \
				|| { echo "CuraEngine unavailable, trying PrusaSlicer ..."; sudo apt-get install -y -qq prusa-slicer; }
		elif command -v brew > /dev/null 2>&1; then
			brew install --cask prusaslicer
		else
			echo "WARN: Install manually — https://github.com/Ultimaker/CuraEngine or https://github.com/prusa3d/PrusaSlicer/releases"
		fi
	fi

setup_rtk: ## Install RTK CLI for token-optimized LLM output
	if command -v rtk > /dev/null 2>&1; then
		echo "rtk already installed: $$(rtk --version)"
	else
		curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
	fi
	rtk init -g

setup_lychee: ## Install lychee link checker
	if command -v lychee > /dev/null 2>&1; then
		echo "lychee already installed: $$(lychee --version)"
	else
		curl -sSfL https://github.com/lycheeverse/lychee/releases/latest/download/lychee-x86_64-unknown-linux-gnu.tar.gz \
			| tar xz -C /usr/local/bin 2>/dev/null \
			|| echo "Install failed — download manually from https://github.com/lycheeverse/lychee/releases"
	fi


# MARK: HARDWARE


render_wireframe: ## Generate STL + wireframe SVG from parts.json
	uv run --group cad python hardware/render.py

render_solid: ## Generate STL + solid-filled SVG from parts.json
	uv run --group cad python hardware/render.py --solid

check_prints: ## Run slicer printability checks on STLs (CuraEngine or PrusaSlicer)
	uv run python hardware/slicer/validate.py --all

render_all: render_wireframe check_prints ## Generate parts + validate printability

calibrate_arms: ## Calibrate all arms (leader + followers)
	lerobot-calibrate --robot.type=so101_follower --robot.port=$(FOLLOWER_A_PORT) --robot.id=arm_a
	lerobot-calibrate --robot.type=so101_follower --robot.port=$(FOLLOWER_B_PORT) --robot.id=arm_b
	lerobot-calibrate --teleop.type=so101_leader --teleop.port=$(LEADER_PORT) --teleop.id=leader

start_teleop: ## Start teleoperation (leader → follower)
	lerobot-teleoperate \
		--robot.type=so101_follower \
		--robot.port=$(FOLLOWER_A_PORT) \
		--robot.id=arm_a \
		--robot.cameras="{ overhead: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30}, wrist: {type: opencv, index_or_path: 2, width: 640, height: 480, fps: 30}}" \
		--teleop.type=so101_leader \
		--teleop.port=$(LEADER_PORT) \
		--teleop.id=leader \
		--display_data=true

record_episodes: ## Record teleoperation episodes
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

train_policy: ## Train policy on recorded data
	lerobot-train \
		--dataset.repo_id=$(DATASET) \
		--policy.type=$(POLICY) \
		--output_dir=outputs/train/$(POLICY)_biolab \
		--job_name=$(POLICY)_biolab \
		--policy.device=cuda \
		--wandb.enable=true


# MARK: DEV


lint_code: ## Format and lint with ruff
	uv run ruff format . $(RUFF_QUIET) && uv run ruff check . --fix $(RUFF_QUIET)

check_links: ## Check links with lychee
	if command -v lychee > /dev/null 2>&1; then
		lychee --config .lychee.toml .
	else
		echo "lychee not installed — run: make setup_lychee"
	fi

check_types: ## Run pyright type checking
	uv run pyright src $(PYRIGHT_QUIET)

run_tests: ## Run all tests with pytest
	uv run pytest $(PYTEST_QUIET)

rerun_tests: ## Rerun last failed tests only
	uv run pytest --lf -x

quick_validate: lint_code check_types ## Fast validation (lint + type check)

validate: lint_code check_types run_tests ## Full validation (lint + type check + test)


# MARK: APP


eval_policy: ## Evaluate trained policy
	uv run python scripts/run_demo.py --mode=eval --arm-port=$(FOLLOWER_A_PORT)

serve_dashboard: ## Start remote dashboard
	uv run uvicorn src.dashboard.server:app --host 0.0.0.0 --port 8080 --reload

run_demo: ## Run full demo pipeline
	uv run python scripts/run_demo.py --mode=full


# MARK: HELP


help: ## Show available recipes grouped by section
	echo "Usage: make [recipe]"
	echo ""
	awk '/^# MARK:/ { \
		section = substr($$0, index($$0, ":")+2); \
		printf "\n\033[1m%s\033[0m\n", section \
	} \
	/^[a-zA-Z0-9_-]+:.*?##/ { \
		helpMessage = match($$0, /## (.*)/); \
		if (helpMessage) { \
			recipe = $$1; \
			sub(/:/, "", recipe); \
			printf "  \033[36m%-22s\033[0m %s\n", recipe, substr($$0, RSTART + 3, RLENGTH) \
		} \
	}' $(MAKEFILE_LIST)
