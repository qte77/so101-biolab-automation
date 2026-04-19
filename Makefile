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
	setup_uv setup_dev setup_all setup_cad setup_scad setup_slicer setup_node setup_rtk setup_lychee setup_mdlint setup_diagramforge setup_hardware_deps setup_hardware \
	render_parts check_prints render_all \
	autofix lint check_links check_docs check_types check_complexity test test_cov retest quick_validate validate \
	calibrate_arms start_teleop start_foxglove fetch_urdf record_episodes train_policy \
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

NODE_VERSION ?= 22.11.0
NODE_DIR     := $(HOME)/.local/share/node
NODE_BIN     := $(NODE_DIR)/bin

LEADER_PORT ?= /dev/ttyACM0
FOLLOWER_A_PORT ?= /dev/ttyACM1
FOLLOWER_B_PORT ?= /dev/ttyACM2
HF_USER ?= $(shell hf auth whoami 2>/dev/null | head -n 1)
DATASET ?= $(HF_USER)/so101-biolab-pipetting
TASK ?= "Pick up pipette tip and aspirate from well A1"
NUM_EPISODES ?= 10
POLICY ?= act
WANDB ?= 0
WRIST_CAM ?= 2
ENV_CAM ?= 0

# Detect OS and package manager — use in recipes via $(DETECT_PKG_MGR)
# Sets: PKG_MGR (dnf|apt|pacman|brew), HOST_OS (linux|darwin), HOST_ARCH (x86_64|aarch64|arm64)
define DETECT_PKG_MGR
HOST_OS=$$(uname -s | tr '[:upper:]' '[:lower:]')
HOST_ARCH=$$(uname -m)
if command -v dnf > /dev/null 2>&1; then PKG_MGR=dnf
elif command -v apt-get > /dev/null 2>&1; then PKG_MGR=apt
elif command -v pacman > /dev/null 2>&1; then PKG_MGR=pacman
elif command -v brew > /dev/null 2>&1; then PKG_MGR=brew
else PKG_MGR=unknown
fi
endef


# MARK: SETUP


setup_uv: ## Install uv package manager (if missing)
	if command -v uv > /dev/null 2>&1; then
		echo "uv already installed: $$(uv --version)"
	else
		echo "Installing uv ..."
		curl --proto '=https' --tlsv1.2 -LsSf https://astral.sh/uv/install.sh | sh
		echo ""
		echo "NOTE: restart your shell or run 'source $$HOME/.local/bin/env' to add uv to PATH"
	fi

setup_dev: setup_uv ## Install dev + test dependencies
	uv sync

setup_all: setup_dev setup_cad ## Install all dependencies + tools
	-$(MAKE) setup_slicer
	-$(MAKE) setup_lychee
	-$(MAKE) setup_rtk
	-$(MAKE) setup_diagramforge

setup_cad: setup_uv ## Install build123d for BREP CAD generation
	uv sync --group cad

setup_scad: ## Install OpenSCAD for parametric STL generation
	if command -v openscad > /dev/null 2>&1; then
		echo "openscad already installed: $$(openscad --version 2>&1 | head -1)"
	else
		$(DETECT_PKG_MGR)
		echo "Installing OpenSCAD ..."
		case "$$PKG_MGR" in
			dnf) sudo dnf install -y openscad ;;
			apt) sudo apt-get update -qq && sudo apt-get install -y -qq openscad ;;
			pacman) sudo pacman -S --noconfirm openscad ;;
			brew) brew install openscad ;;
			*) echo "ERROR: Install manually: https://openscad.org/downloads"; exit 1 ;;
		esac
	fi

setup_slicer: ## Install CuraEngine (preferred) or PrusaSlicer (fallback) for printability validation
	if command -v CuraEngine > /dev/null 2>&1; then
		echo "CuraEngine already installed: $$(CuraEngine --version 2>&1 | head -1)"
	elif command -v prusa-slicer > /dev/null 2>&1; then
		echo "PrusaSlicer already installed: $$(prusa-slicer --version 2>&1 | head -1)"
	else
		$(DETECT_PKG_MGR)
		echo "Installing CuraEngine (headless slicer) ..."
		case "$$PKG_MGR" in
			dnf) sudo dnf install -y curaengine \
				|| { echo "CuraEngine unavailable, trying PrusaSlicer ..."; sudo dnf install -y prusa-slicer; } ;;
			apt) sudo apt-get update -qq && sudo apt-get install -y -qq curaengine \
				|| { echo "CuraEngine unavailable, trying PrusaSlicer ..."; sudo apt-get install -y -qq prusa-slicer; } ;;
			pacman) sudo pacman -S --noconfirm cura-engine \
				|| { echo "CuraEngine unavailable, trying PrusaSlicer ..."; sudo pacman -S --noconfirm prusa-slicer; } ;;
			brew) brew install --cask prusaslicer ;;
			*) echo "WARN: Install manually — https://github.com/Ultimaker/CuraEngine or https://github.com/prusa3d/PrusaSlicer/releases" ;;
		esac
	fi

setup_node: ## Install Node.js user-locally to ~/.local/share/node (no sudo)
	if [ -x "$(NODE_BIN)/node" ]; then
		echo "node already installed: $$($(NODE_BIN)/node --version) (at $(NODE_DIR))"
	elif command -v node > /dev/null 2>&1; then
		echo "node already installed on PATH: $$(node --version)"
	else
		$(DETECT_PKG_MGR)
		NODE_ARCH=$$HOST_ARCH
		case "$$NODE_ARCH" in x86_64) NODE_ARCH=x64 ;; aarch64|arm64) NODE_ARCH=arm64 ;; esac
		echo "Installing Node.js $(NODE_VERSION) ($$HOST_OS-$$NODE_ARCH) to $(NODE_DIR) ..."
		mkdir -p $(NODE_DIR)
		curl --proto '=https' --tlsv1.2 -sSfL \
			"https://nodejs.org/dist/v$(NODE_VERSION)/node-v$(NODE_VERSION)-$$HOST_OS-$$NODE_ARCH.tar.xz" \
			| tar -xJ --strip-components=1 -C $(NODE_DIR) \
			|| { echo "Install failed — download manually from https://nodejs.org/dist/v$(NODE_VERSION)/"; exit 1; }
	fi
	mkdir -p $(HOME)/.local/bin
	for bin in node npm npx; do \
		if [ -x "$(NODE_BIN)/$$bin" ] && [ ! -e "$(HOME)/.local/bin/$$bin" ]; then \
			ln -s "$(NODE_BIN)/$$bin" "$(HOME)/.local/bin/$$bin"; \
			echo "symlinked $$bin -> $(HOME)/.local/bin/$$bin"; \
		fi; \
	done

setup_rtk: ## Install RTK CLI for token-optimized LLM output
	if command -v rtk > /dev/null 2>&1; then
		echo "rtk already installed: $$(rtk --version)"
	else
		curl --proto '=https' --tlsv1.2 -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh
	fi
	rtk init -g

setup_lychee: ## Install lychee link checker user-locally to ~/.local/bin (no sudo)
	if command -v lychee > /dev/null 2>&1; then
		echo "lychee already installed: $$(lychee --version)"
	else
		$(DETECT_PKG_MGR)
		case "$$HOST_OS" in \
		linux) LYCHEE_TARGET="$$HOST_ARCH-unknown-linux-gnu" ;; \
		darwin) LYCHEE_TARGET="$$HOST_ARCH-apple-darwin" ;; \
		*) echo "ERROR: unsupported OS — download manually from https://github.com/lycheeverse/lychee/releases"; exit 1 ;; \
		esac
		mkdir -p ~/.local/bin
		curl --proto '=https' --tlsv1.2 -sSfL \
			"https://github.com/lycheeverse/lychee/releases/latest/download/lychee-$$LYCHEE_TARGET.tar.gz" \
			| tar xz -C ~/.local/bin \
			&& echo "lychee installed to ~/.local/bin — ensure it is on PATH" \
			|| echo "Install failed — download manually from https://github.com/lycheeverse/lychee/releases"
	fi

setup_mdlint: setup_node ## Install markdownlint-cli2 via user-local npm (no sudo)
	export PATH="$(NODE_BIN):$$PATH"
	if [ -x "$(NODE_BIN)/markdownlint-cli2" ]; then
		echo "markdownlint-cli2 already installed: $$(markdownlint-cli2 --version 2>&1 | head -1)"
	elif command -v markdownlint-cli2 > /dev/null 2>&1; then
		echo "markdownlint-cli2 already installed (system PATH): $$(markdownlint-cli2 --version 2>&1 | head -1)"
	else
		echo "Installing markdownlint-cli2 into $(NODE_DIR) ..."
		if [ -x "$(NODE_BIN)/npm" ] || command -v npm > /dev/null 2>&1; then
			npm install -g markdownlint-cli2
		else
			echo "ERROR: npm not found after setup_node — check Node install"
			exit 1
		fi
	fi

setup_diagramforge: ## Clone diagramforge from URL in .gitmodules if missing (not a tracked submodule)
	if [ -e diagramforge/.git ]; then
		echo "diagramforge already present"
	elif [ ! -f .gitmodules ]; then
		echo "WARN: .gitmodules missing — skipping"
	else
		url=$$(git config --file .gitmodules submodule.diagramforge.url 2>/dev/null)
		if [ -z "$$url" ]; then
			echo "WARN: submodule.diagramforge.url not set in .gitmodules — skipping"
		else
			echo "Cloning diagramforge from $$url ..."
			git clone "$$url" diagramforge
		fi
	fi

setup_hardware_deps: ## Install system deps for lerobot (kernel headers, cmake, libav)
	$(DETECT_PKG_MGR)
	echo "Installing lerobot build dependencies ($$PKG_MGR on $$HOST_OS) ..."
	case "$$PKG_MGR" in
		dnf) sudo dnf install -y kernel-devel cmake gcc g++ pkg-config \
			libavformat-free-devel libavcodec-free-devel libavdevice-free-devel \
			libavutil-free-devel libswscale-free-devel libswresample-free-devel \
			libavfilter-free-devel ;;
		apt) sudo apt-get update -qq && sudo apt-get install -y -qq \
			linux-headers-$$(uname -r) cmake build-essential pkg-config \
			libavformat-dev libavcodec-dev libavdevice-dev \
			libavutil-dev libswscale-dev libswresample-dev libavfilter-dev ;;
		pacman) sudo pacman -S --noconfirm linux-headers cmake base-devel ffmpeg ;;
		brew) echo "macOS: evdev not needed (pynput uses Quartz)" && \
			brew install cmake ffmpeg pkg-config ;;
		*) echo "ERROR: unsupported package manager — install kernel headers, cmake, and libav dev packages manually"; exit 1 ;;
	esac

setup_hardware: setup_uv setup_hardware_deps ## Install all hardware deps (LeRobot, Feetech, Foxglove, system libs)
	uv sync --group lerobot --group foxglove


# MARK: HARDWARE


render_parts: ## Generate STL + SVG from hardware/parts.json (build123d preferred, OpenSCAD fallback)
	uv run --group cad python src/hardware/render.py

check_prints: ## Run slicer printability checks on STLs (CuraEngine or PrusaSlicer)
	uv run python src/hardware/slicer/validate.py --all

render_all: render_parts check_prints ## Generate parts + validate printability

find_port: ## Identify serial port for a single board (unplug USB when prompted)
	lerobot-find-port

scan_servos: ## Scan a port for STS3215 servos (override: PORT=/dev/ttyACM1)
	uv run so101-scan-servos --port=$(or $(PORT),/dev/ttyACM0)

install_udev: ## Install udev rule for Waveshare boards (makes ttyACM* world-rw)
	echo 'SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", MODE="0666"' | \
		sudo tee /etc/udev/rules.d/99-waveshare.rules
	sudo udevadm control --reload-rules
	sudo udevadm trigger
	echo "udev rule installed. Replug the Waveshare board(s)."

bringup: patch_lerobot scan_servos ## Guided first-bringup: patch lerobot + scan servos
	echo ""
	echo "Next steps:"
	echo "  1. If scan shows mixed firmware, patches are already applied."
	echo "  2. Run 'make calibrate_arms' (or calibrate individually)."
	echo "  3. Run 'make start_teleop' to verify leader → follower."

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

fetch_urdf: ## Download SO-101 URDF + STL assets from foxglove-sdk
	if [ -d "SO101" ]; then
		echo "SO101/ already exists — skipping"
	else
		echo "Fetching SO-101 URDF + STL from foxglove-sdk..."
		git clone --depth 1 --filter=blob:none --sparse \
			https://github.com/foxglove/foxglove-sdk.git /tmp/foxglove-sdk-sparse
		cd /tmp/foxglove-sdk-sparse && \
			git sparse-checkout set python/foxglove-sdk-examples/so101-visualization/SO101
		cp -r /tmp/foxglove-sdk-sparse/python/foxglove-sdk-examples/so101-visualization/SO101 SO101
		rm -rf /tmp/foxglove-sdk-sparse
		echo "SO101/ URDF + STL assets ready"
	fi

start_foxglove: fetch_urdf ## Live 3D arm viz + cameras via Foxglove (ws://localhost:8765)
	@echo "Requires: uv sync --group foxglove --group lerobot"
	uv run --group foxglove --group lerobot so101-foxglove \
		--robot.port=$(FOLLOWER_A_PORT) \
		--robot.id=arm_a \
		--robot.wrist_cam_id=$(WRIST_CAM) \
		--robot.env_cam_id=$(ENV_CAM)

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

train_policy: ## Train policy on recorded data (WANDB=1 to enable wandb)
	lerobot-train \
		--dataset.repo_id=$(DATASET) \
		--policy.type=$(POLICY) \
		--output_dir=outputs/train/$(POLICY)_biolab \
		--job_name=$(POLICY)_biolab \
		--policy.device=cuda \
		--wandb.enable=$(if $(filter 1,$(WANDB)),true,false)


# MARK: DEV


autofix: ## Auto-format and fix lint issues (use before committing)
	uv run ruff format . $(RUFF_QUIET) && uv run ruff check . --fix $(RUFF_QUIET)
	export PATH="$(NODE_BIN):$$PATH"
	if command -v markdownlint-cli2 > /dev/null 2>&1; then
		markdownlint-cli2 --fix "README.md" "CHANGELOG.md" "CONTRIBUTING.md" "AGENTS.md" "docs/**/*.md"
	fi

lint: ## Check formatting + lint (fails on issues, does not fix)
	uv run ruff format --check . $(RUFF_QUIET) && uv run ruff check . $(RUFF_QUIET)

check_links: ## Check links with lychee
	if command -v lychee > /dev/null 2>&1; then
		lychee --config .lychee.toml .
	else
		echo "lychee not installed — run: make setup_lychee"
	fi

check_docs: ## Lint markdown files (reads .markdownlint.json)
	export PATH="$(NODE_BIN):$$PATH"
	if command -v markdownlint-cli2 > /dev/null 2>&1; then
		markdownlint-cli2 "README.md" "CHANGELOG.md" "CONTRIBUTING.md" "AGENTS.md" "docs/**/*.md"
	else
		echo "markdownlint-cli2 not installed — run: make setup_mdlint"
	fi

check_types: ## Run pyright type checking
	uv run pyright src $(PYRIGHT_QUIET)

test: ## Run all tests with pytest
	uv run pytest $(PYTEST_QUIET)

test_cov: ## Run tests with coverage report
	uv run pytest --cov=so101 --cov=dashboard --cov-fail-under=80 $(PYTEST_QUIET)

retest: ## Rerun last failed tests only
	uv run pytest --lf -x

check_complexity: ## Check cognitive complexity (max 15/function)
	uv run complexipy src/so101/ src/dashboard/ --max-complexity-allowed 15

quick_validate: lint check_types ## Fast gate (lint + type check)

validate: lint check_types test_cov check_complexity ## Full gate (lint + types + tests + coverage + complexity)


# MARK: APP


eval_policy: ## Evaluate trained policy
	uv run so101-demo --mode=eval --arm-port=$(FOLLOWER_A_PORT)

serve_dashboard: ## Start remote dashboard
	uv run uvicorn dashboard.server:app --host 0.0.0.0 --port 8080 --reload

run_demo: ## Run full demo pipeline
	uv run so101-demo --mode=full

patch_lerobot: ## Apply lerobot patches for mixed STS3215 firmware (prototyping only)
	uv run so101-patch-lerobot

patch_lerobot_revert: ## Revert lerobot patches
	uv run so101-patch-lerobot --revert


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
