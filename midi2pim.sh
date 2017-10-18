#!/bin/sh

if [ $# -ne 5 ]; then
  echo "引数が不足しています。" 1>&2
  echo "[midiファイル] [右車輪用チャンネル] [左車輪用チャンネル] [オクターブ設定] [モード]" 1>&2
  exit 1
fi
python src/pymidi.py $1 $2 $3 $4 $5
echo ====================================
echo スクリプトを実行します。
echo MIDIのファイル名：$1
echo ====================================
bash pimidi.sh
