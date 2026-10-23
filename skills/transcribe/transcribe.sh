#!/usr/bin/env bash
# Transcribe one recording with whisper.cpp to <knowledge base>/scratch/transcripts/<name>.txt, skipping one already transcribed
# Env: WHISPER_MODEL the ggml model, WHISPER_LANG the spoken language, TRANSCRIPTS_DIR the output folder, WHISPER_FLAGS more whisper.cpp flags
set -euo pipefail

[[ $# -eq 1 ]] || { echo "Usage: $(basename "$0") <audio-file>" >&2; exit 1; }
IN="$1"
[[ -f "$IN" ]] || { echo "File not found: $IN" >&2; exit 2; }

# The knowledge base root, alike through core/skills/ or a skills link
KB="$(cd "$(dirname "$0")/../../.." && pwd)"

# Homebrew's whisper.cpp ships its CLI under either name
BIN="$(command -v whisper-cli || command -v whisper-cpp || true)"
[[ -n "$BIN" ]] || { echo "whisper.cpp not found: brew install whisper-cpp" >&2; exit 3; }
MODEL="${WHISPER_MODEL:-$HOME/.whisper/models/ggml-large-v3.bin}"
[[ -f "$MODEL" ]] || { echo "No model at $MODEL: download ggml-large-v3.bin from huggingface.co/ggerganov/whisper.cpp to it, or set WHISPER_MODEL" >&2; exit 4; }
command -v ffmpeg >/dev/null || { echo "ffmpeg not found: brew install ffmpeg" >&2; exit 5; }

OUTDIR="${TRANSCRIPTS_DIR:-$KB/scratch/transcripts}"
# Keyed by file name alone, so recordings of one name in two folders share a transcript
STEM="$(basename "${IN%.*}")"
OUTTXT="$OUTDIR/$STEM.txt"
# Freshness is modification time alone: a newer transcript of a same-named recording passes as this one's
if [[ "$OUTTXT" -nt "$IN" ]]; then
  echo "Skipping (already transcribed): $OUTTXT"
  exit 0
fi
mkdir -p "$OUTDIR"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
# whisper.cpp reads 16 kHz mono WAV, whatever the recording's format
ffmpeg -hide_banner -loglevel error -i "$IN" -ac 1 -ar 16000 -c:a pcm_s16le -f wav "$TMP/in.wav"

args=(-m "$MODEL" -f "$TMP/in.wav")
# whisper.cpp assumes English unless -l says otherwise
args+=(-l "${WHISPER_LANG:-auto}")
# No carried context, so one misheard phrase cannot repeat into every later segment
args+=(--max-context 0)
# whisper.cpp appends .txt to -of
args+=(-of "$OUTDIR/$STEM" -otxt)
# Unquoted, so several flags split apart
"$BIN" "${args[@]}" ${WHISPER_FLAGS:-}

echo "Transcript → $OUTTXT"
