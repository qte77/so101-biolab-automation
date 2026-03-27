#!/bin/bash

input=$(cat)

# Single jq call extracts all fields (tab-delimited)
read -r cwd agent model version cost duration lines_added lines_removed \
    tokens_in tokens_out remaining_pct exc_context <<< "$(echo "$input" | jq -r '[
    .workspace.current_dir,
    (.agent.type // "main"),
    .model.id,
    (.version // ""),
    (if .cost.total_cost_usd then (.cost.total_cost_usd * 100 | round / 100 | tostring) + "$" else "" end),
    (((.cost.total_api_duration_ms // 0) / 1000 / 60 | round | tostring) + "m"),
    (.cost.total_lines_added // 0 | tostring),
    (.cost.total_lines_removed // 0 | tostring),
    (((.context_window.total_input_tokens // 0) / 1000 | floor | tostring) + "k"),
    (((.context_window.total_output_tokens // 0) / 1000 | floor | tostring) + "k"),
    (if .context_window.current_usage.input_tokens then
        (.context_window.context_window_size // 200000) as $win |
        (.context_window.current_usage.input_tokens // 0) as $in |
        (.context_window.current_usage.cache_creation_input_tokens // 0) as $cc |
        (.context_window.current_usage.cache_read_input_tokens // 0) as $cr |
        (($in + $cc + $cr) / $win * 100) as $used |
        (100 - $used) | round
    else
        .context_window.remaining_percentage // 100
    end | tostring),
    (.exceeds_200k_tokens // false | tostring)
] | join("\t")')"

lines_changed="+${lines_added}/-${lines_removed}"
tokens="${tokens_in}/${tokens_out}"

# Subtract autocompact buffer to get TRUE usable space
if [ -n "$CLAUDE_AUTOCOMPACT_PCT_OVERRIDE" ]; then
    AUTOCOMPACT_BUFFER_PCT=$(awk "BEGIN {print 100 - $CLAUDE_AUTOCOMPACT_PCT_OVERRIDE}")
else
    AUTOCOMPACT_BUFFER_PCT=16.5
fi

true_free_pct=$(awk "BEGIN {print $remaining_pct - $AUTOCOMPACT_BUFFER_PCT}")
remaining=$(echo "$true_free_pct" | awk '{printf "%.2f", $1/100}' | sed 's/^0\./\./')

# Color remaining based on TRUE free space threshold
if [ $(awk "BEGIN {print ($true_free_pct <= 10)}") -eq 1 ]; then
    ctx_color="\033[93;41m"  # Bright yellow fg, red bg - CRITICAL
elif [ $(awk "BEGIN {print ($true_free_pct <= 20)}") -eq 1 ]; then
    ctx_color="\033[91;48;5;237m"  # Bright red fg, dark gray bg - WARNING
elif [ $(awk "BEGIN {print ($true_free_pct <= 35)}") -eq 1 ]; then
    ctx_color="\033[93m"  # Yellow fg - CAUTION
else
    ctx_color="\033[0;32m"   # Normal green fg - OK
fi

user=$(whoami)
time=$(date +%H:%M:%S)

if git rev-parse --git-dir >/dev/null 2>&1; then
    branch=$(git symbolic-ref --short HEAD 2>/dev/null || git rev-parse --short HEAD 2>/dev/null)
else
    branch=""
fi

printf "\033[0;31magent:%s \033[0;33mmodel:%s \033[2mver:%s \033[0;34mcost:%s \033[0;36mdur:%s\n\033[0;32mlines:%s \033[2mtokens(i/o):%s ${ctx_color}ctx(free):%s\033[0m \033[0;31m>200k:%s\033[0m\n\033[2mdir:%s \033[0;36mbranch:%s \033[0;32muser:%s \033[0;35mtime:%s\033[0m" "$agent" "$model" "$version" "$cost" "$duration" "$lines_changed" "$tokens" "$remaining" "$exc_context" "$(basename "$cwd")" "$branch" "$user" "$time"
