#!/bin/sh
ID=taku
IP=35.231.58.73
PORT=8022
PASSPHRASE=t.matsumura
KEYFILE=~/.ssh/id_rsa_matsu
SENDFILE=wsgi.py
REMOTE_DIR=/home/taku/kimonoSearch_www/

# expect コマンド実行
expect -c "
  # タイムアウト値設定
  set rimeout 30
  #spawnで実行
  spawn sftp -P $PORT -i $KEYFILE $ID@$IP

  # パスフレーズ入力の「:」の出力を待つ
  expect ":"

  # : が出たらパスフレーズを送信
  send \"$PASSPHRASE\n\"

  # コマンド入力の「>」の出力を待つ
  expect ">"

  # >が出たらファイルをput

  send \"put $SENDFILE $REMOTEDIR\$SENDFILE\"

  # コマンド入力の「>」の出力を待つ
  expect ">"

  # >が出たらquit
  send \"quit\"

  # spawnの出力先を画面にする
  interact
  "
