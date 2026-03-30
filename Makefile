.SILENT:
.ONESHELL:
.PHONY: \
	setup setup_train setup_cad setup_scad setup_slicer setup_rtk setup_lychee \
	render_scad check_prints render_all \
	lint lint_links type_check test test_rerun validate quick_validate \
	calibrate teleop record train eval serve demo \
	help
.DEFAULT_GOAL := help


# -- config --
LEADER_PORT ?= /dev/ttyACM0
FOLLOWER_A_PORT ?= /dev/ttyACM1
FOLLOWER_B_PORT ?= /dev/ttyACM2
HF_USER ?= $(shell hf auth whoami 2>/dev/null | head -n 1)
DATASET ?= $(HF_USER)/so101-biolab-pipetting
TASK ?= "Pick up pipette tip and aspirate from well A1"
NUM_EPISODES ?= 10
POLICY ?= act


# MARK: SETUP


setup: ## Install dev + test dependencies
	uv sync

setup_train: ## Install training dependencies (torch, wandb)
	uv sync --group train

setup_cad: ## Install CadQuery for SVG wireframe generation (requires Python 3.10-3.12)
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

setup_slicer: ## Install PrusaSlicer for printability validation (optional)
	if command -v prusa-slicer > /dev/null 2>&1; then
		echo "PrusaSlicer already installed: $$(prusa-slicer --version 2>&1 | head -1)"
	else
		echo "Installing PrusaSlicer ..."
		if command -v apt-get > /dev/null 2>&1; then
			sudo apt-get update -qq && sudo apt-get install -y -qq prusa-slicer
		elif command -v brew > /dev/null 2>&1; then
			brew install --cask prusaslicer
		elif command -v flatpak > /dev/null 2>&1; then
			flatpak install -y flathub com.prusa3d.PrusaSlicer
		else
			echo "WARN: Install manually from https://github.com/prusa3d/PrusaSlicer/releases"
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


render_scad: ## Generate STL + SVG from OpenSCAD scripts (requires setup_scad)
	command -v openscad > /dev/null 2>&1 || { echo "ERROR: openscad not found — run: make setup_scad"; exit 1; }
	STL_DIR="$$(pwd)/hardware/stl"
	echo "--- STL generation"
	openscad -o hardware/stl/tip_rack_holder.stl hardware/scad/tip_rack_holder.scad 2>/dev/null
	openscad -o hardware/stl/gripper_tips_tpu.stl hardware/scad/gripper_tips.scad 2>/dev/null
	openscad -o hardware/stl/96well_plate_holder.stl hardware/scad/plate_holder.scad 2>/dev/null
	openscad -o hardware/stl/fridge_hook_tool.stl hardware/scad/fridge_hook.scad 2>/dev/null
	openscad -o hardware/stl/tool_dock_3station.stl hardware/scad/tool_dock.scad 2>/dev/null
	openscad -o hardware/stl/pipette_mount_so101.stl hardware/scad/pipette_mount.scad 2>/dev/null
	openscad -o hardware/stl/tool_cone_robot.stl -D 'PART="robot"' hardware/scad/tool_changer.scad 2>/dev/null
	openscad -o hardware/stl/tool_cone_pipette.stl -D 'PART="male"' hardware/scad/tool_changer.scad 2>/dev/null
	openscad -o hardware/stl/tool_cone_gripper.stl -D 'PART="male"' hardware/scad/tool_changer.scad 2>/dev/null
	openscad -o hardware/stl/tool_cone_hook.stl -D 'PART="male"' hardware/scad/tool_changer.scad 2>/dev/null
	echo "--- SVG wireframe from STLs (CadQuery)"
	uv run --group cad python3 hardware/cad/stl_to_svg.py --all
	python3 hardware/cad/theme_svgs.py
	echo "=== render_scad: done ==="

check_prints: ## Run PrusaSlicer printability checks on STLs (optional, requires setup_slicer)
	if command -v prusa-slicer > /dev/null 2>&1; then
		python hardware/slicer/validate.py --all
	else
		echo "SKIP: PrusaSlicer not installed — run 'make setup_slicer' to enable validation"
	fi

render_all: render_scad check_prints ## Generate parts (OpenSCAD) + validate printability

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


# MARK: DEV


lint: ## Format and lint with ruff
	uv run ruff format . && uv run ruff check . --fix

lint_links: ## Check links with lychee
	if command -v lychee > /dev/null 2>&1; then
		lychee --config .lychee.toml .
	else
		echo "lychee not installed — run: make setup_lychee"
	fi

type_check: ## Run pyright type checking
	uv run pyright src

test: ## Run all tests with pytest
	uv run pytest

test_rerun: ## Rerun last failed tests only
	uv run pytest --lf -x

quick_validate: lint type_check ## Fast validation (lint + type check)

validate: lint type_check test ## Full validation (lint + type check + test)


# MARK: APP


eval: ## Evaluate trained policy
	python scripts/run_demo.py --mode=eval --arm-port=$(FOLLOWER_A_PORT)

serve: ## Start remote dashboard
	uvicorn src.dashboard.server:app --host 0.0.0.0 --port 8080 --reload

demo: ## Run full demo pipeline
	python scripts/run_demo.py --mode=full


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
