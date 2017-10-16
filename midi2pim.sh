#!/bin/sh

if [ $# -ne 4 ]; then
  echo "引数が不足しています。" 1>&2
  echo "[midiファイル] [右車輪用チャンネル] [左車輪用チャンネル] [オクターブ設定]" 1>&2
  exit 1
fi
python src/pymidi.py $1 $2 $3 $4
echo ====================================
echo スクリプトを実行します。
echo ファイル名：$1
echo ====================================
bash src/pimidi.sh
