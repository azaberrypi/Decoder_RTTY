import wave
import numpy as np
import translation_table
fname='rtty.wav'   # should specify the filename.
smp= 8000          # Sampling Rate [frequency/s]
baud = 45.45       # Baud rate [bit/s]
FQm= smp/915.0     # Mark Frequency : 915Hz
FQs= smp/1085.0    # Space Frequency : 1085Hz
wind= 32           # windows size Integer
waveFile = wave.open(fname, 'r')

current_bit=0
ex_bit=0
sum1=0
hogehoge = [0] * 2000
data_and_stop_bit = [0] * 6
databit_index = 0
smp_per_bit = int(smp / baud)       # frequency/bit

maybe_found_startbit_flag = 0
found_startbit_flag = 0
processing_databit_flag = 0
found_databit_flag = 0
finish_1bit_flag = 0
found_stopbit_flag = 0

num_smp = 0
START_BIT = 0
STOP_BIT = 1
judgement_smp = 0.25    # 1bit分のデータにおいて、どれだけの割合を超えた個所を読めばsmpが安定していると考えるか
mode = "11111"

mq=[];mi=[];sq=[];si=[]

for j in range(waveFile.getnframes()):
      buf = waveFile.readframes(1)    # 一つのオーディオフレームを読み込んで、bytesオブジェクトとして返す
      # q:実数, i:虚数
      mq.append((buf[0]-128)*np.sin(np.pi*2.0/FQm*j))       # unsigned 8bit(0-255で中心が128) → 中心を0
      mi.append((buf[0]-128)*np.cos(np.pi*2.0/FQm*j))
      sq.append((buf[0]-128)*np.sin(np.pi*2.0/FQs*j))
      si.append((buf[0]-128)*np.cos(np.pi*2.0/FQs*j))
      # 絶対値(強度)を導出
      mk = np.sqrt(sum(mq)**2 + sum(mi)**2)
      sp = np.sqrt(sum(sq)**2 + sum(si)**2)
      #print(mk,sp,int(mk>sp),sep=",")
      if j>wind:
            mq.pop(0);mi.pop(0);sq.pop(0);si.pop(0)
      current_bit = int(mk>sp)


      # ストップビット→スタートビットを探す
      if maybe_found_startbit_flag == 0 and current_bit == START_BIT and ex_bit == STOP_BIT:
            maybe_found_startbit_flag = 1


      # ストップビットの処理
      if databit_index == 5 and finish_1bit_flag == 1:
            processing_databit_flag = 0
            num_smp += 1
            # ストップビットではなかった時
            if num_smp == int(smp_per_bit * judgement_smp) and current_bit != STOP_BIT :
                  databit_index = 0
                  num_smp = 0
                  finish_1bit_flag = 0
                  maybe_found_startbit_flag = 0
            # nビット分の長さが終了
            elif current_bit != ex_bit and maybe_found_startbit_flag == 1 :
                  # データビットの内容を出力
                  sequence = ""
                  for i in range(databit_index):
                        sequence += str(data_and_stop_bit[i])
                  mode = translation_table.table(sequence, mode)

                  finish_1bit_flag = 0
                  databit_index = 0
                  num_smp = 0
                  found_stopbit_flag = 0
                  maybe_found_startbit_flag = 1


      # データビットの処理
      elif processing_databit_flag == 1 :
            num_smp += 1
            # データビットが1か0か判明した時
            if num_smp == int(smp_per_bit * judgement_smp) :
                  finish_1bit_flag = 0
                  data_and_stop_bit[databit_index] = current_bit
                  databit_index += 1
            # 1ビット分の長さが終了
            elif num_smp == int(smp_per_bit) :
                  num_smp = 0
                  finish_1bit_flag = 1


      # スタートビットの処理
      elif maybe_found_startbit_flag == 1 :
            num_smp += 1
            # スタートビットではなかった時
            if num_smp == int(smp_per_bit * judgement_smp) and current_bit != START_BIT :
                  num_smp = 0
                  maybe_found_startbit_flag = 0
            # 1ビット分の長さが終了
            if num_smp == int(smp_per_bit) :
                  num_smp = 0
                  found_startbit_flag = 0
                  processing_databit_flag = 1


      ex_bit = current_bit


waveFile.close()