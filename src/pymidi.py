# coding: UTF-8
#ラズパイマウスで演奏(MIDI)
#Sean D. Spencerさんのmidiparser.pyを使用

import sys
import midiparser
import math

#コマンドラインから引数を取得
args = sys.argv

midifile = args[1]
mode = int(args[5])

#書き出し先のファイル名
outfile = "pimidi.sh"

# インポートするチャンネル設定
imported_channels=[int(args[2]),int(args[3])]

def main(argv):

    #ファイル書き出し
    FILE = open(outfile,"w")

    #MIDIファイルの読み込み
    midi = midiparser.File(midifile)

    noteEventList=[]

    #MIDIファイルの情報を表示
    print "FileName：" + args[1]
    print "トラック数：%d" % midi.num_tracks
    print "フォーマット形式：%d" % midi.format
    print "４分音符基準の分解能：%d" % midi.division
    print "===================================="
    #分解能に合わせてBPMの係数を計算
    division_level = float(midi.division)/480

    #トラックの読み込み
    for track in midi.tracks:

        #イベントの読み込み
        for event in track.events:

            #イベントタイプがテンポ情報の場合
            if event.type == midiparser.meta.SetTempo:

                #MIDIのテンポ情報を取得
                tempo=event.detail.tempo
                #print "4分音符の長さ(µs): " + str(event.detail.tempo)

                #BPMの計算(BPM＝60÷音符の長さ(ms)×定数A×1000)
                midi_bpm = float(60)/(division_level*tempo*0.001*0.001)
                #print "BPM：%d" % midi_bpm
                #print "===================================="


            #イベントタイプがノートオンの場合(音を鳴らす)
            if ((event.type == midiparser.voice.NoteOn) and (event.channel in imported_channels)):
                if event.detail.velocity > 0:
                    noteEventList.append([event.absolute, 1, event.detail.note_no, event.detail.velocity])
                else:
                    noteEventList.append([event.absolute, 0, event.detail.note_no, event.detail.velocity])

            #イベントタイプがノートオフの場合(音を止める)
            if (event.type == midiparser.voice.NoteOff) and (event.channel in imported_channels):
                noteEventList.append([event.absolute, 0, event.detail.note_no, event.detail.velocity])


    noteEventList.sort()
    nowtimecount = 0
    print "イベントの長さ:%d" % len(noteEventList)
    print "===================================="
    last_time=-0
    active_notes={}
    for note in noteEventList:
        if last_time < note[0]:
            freq_xyz=[0,0,0]
            for i in range(0, min(len(active_notes.values()), 2)): # number of axes for which to build notes
                nownote=sorted(active_notes.values(), reverse=True)[i]
                freq_xyz[i] = pow(2.0, (nownote-69)/12.0)*440.0
                #print "チャンネル:%d  ノート:%d  周波数:%f  %d" % (i,nownote,freq_xyz[i],note[0]-last_time)

            if mode == 1:
                ###ラズパイマウスで動かす用
                #モータの電源ON
                FILE.write ("echo 1 > /dev/rtmotoren0\n")
                #演出用に距離センサを動かす
                FILE.write ("cat < /dev/rtlightsensor0\n")
                #モータへの指令
                FILE.write ("echo %d %d %d > /dev/rtmotor0 && " % (freq_xyz[0]*int(args[4]),freq_xyz[1]*int(args[4]),((float(note[0] - last_time)/midi.division)*tempo*0.001)))
                #モータの電源OFF
                FILE.write ("echo 0 > /dev/rtmotoren0\n")

                #別方式
                #FILE.write ("echo %d > /dev/rtmotor_raw_l0 && echo %d > /dev/rtmotor_raw_r0\n" % (freq_xyz[0],freq_xyz[1]))
                #FILE.write ("sleep %f\n" % ((float(note[0] - last_time)/midi.division)*tempo*0.001*0.001))


            elif mode == 2:
                ###画面に周波数やウェイト時間を表示させる(デバッグ用)
                nowtimecount += ((float(note[0] - last_time)/midi.division)*tempo*0.001*0.001)
                FILE.write ("echo -------------------------------\n")
                FILE.write ("echo MusicTime[s]:%f\n" % nowtimecount)
                FILE.write ("echo LeftMotor[Hz]:%d\n" % freq_xyz[0]*int(args[4]))
                FILE.write ("echo RightMotor[Hz]:%d\n" % freq_xyz[1]*int(args[4]))
                FILE.write ("echo DeltaTime[s]:%f\n" % ((float(note[0] - last_time)/midi.division)*tempo*0.001*0.001))
                #FILE.write ("echo left:%7dRight:%-5d\tTime:%0.6f\n" % (freq_xyz[0]*int(args[4]),freq_xyz[1]*int(args[4]),((float(note[0] - last_time)/midi.division)*tempo*0.001*0.001)))
                #ウェイト
                FILE.write ("sleep %f\n" % ((float(note[0] - last_time)/midi.division)*tempo*0.001*0.001))

            #print freq_xyz[1],freq_xyz[0]
            #print "経過時間:%d  周波数:%d  時間差：%d" % (last_time,freq_xyz[0],(note[0] - last_time))

            last_time = note[0]
        if note[1]==1: # Note on
            if active_notes.has_key(note[2]):
                pass
                #print "Warning: tried to turn on note already on!"
            else:
                active_notes[note[2]]=note[2] # key and value are the same, but we don't really care.
        elif note[1]==0: # Note off
            if(active_notes.has_key(note[2])):
                active_notes.pop(note[2])
            else:
                pass
                #print "Warning: tried to turn off note that wasn't on!"
    print ("書き出し完了")
    #FILE.write ("wait")
if __name__ == "__main__":
    main(sys.argv)
