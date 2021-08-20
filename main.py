import wave
import numpy as np
fname='rtty3s.wav' # should be specify the filename.
smp= 8000          # Sampling Rate
baud = 45.45       # Baud rate
FQm= smp/915.0     # Mark Frequency 914Hz
FQs= smp/1085.0    # Space Frequency 1086Hz
wind= 32           # windows size Integer サンプル数？
waveFile = wave.open(fname, 'r')

current_bit=0
ex_bit=0
sum1=0
hogehoge = [0] * 2000
data_and_finish_bit = [0] * 6
index_databit = 0
smp_per_bit = int(smp / baud)

flag_maybe_found_startbit = 0
flag_found_startbit = 0
flag_processing_databit = 0
flag_found_databit = 0
flag_finish_1bit = 0
flag_found_stopbit = 0

num_smp = 0
surplus = 0
START_BIT = 0
STOP_BIT = 1
mq=[];mi=[];sq=[];si=[]

for j in range(waveFile.getnframes()):
      buf = waveFile.readframes(1)
      mq.append((buf[0]-128)*np.sin(np.pi*2.0/FQm*j))
      mi.append((buf[0]-128)*np.cos(np.pi*2.0/FQm*j))
      sq.append((buf[0]-128)*np.sin(np.pi*2.0/FQs*j))
      si.append((buf[0]-128)*np.cos(np.pi*2.0/FQs*j))
      mk = np.sqrt(sum(mq)**2 + sum(mi)**2)
      sp = np.sqrt(sum(sq)**2 + sum(si)**2)
      #print(mk,sp,int(mk>sp),sep=",")
      if j>wind:
            mq.pop(0);mi.pop(0);sq.pop(0);si.pop(0)
      current_bit = int(mk>sp)

      #ストップビット→スタートビットを探す
      if flag_maybe_found_startbit == 0 and current_bit == START_BIT and ex_bit == STOP_BIT:
            flag_maybe_found_startbit = 1


      # ストップビットの処理
      if index_databit == 5 and flag_finish_1bit == 1:
            flag_processing_databit = 0
            num_smp += 1
            # ストップビットではなかった時
            #if current_bit != ex_bit and flag_found_stopbit == 0 :
            if num_smp == int(smp_per_bit * 0.25) and current_bit != STOP_BIT :
                  index_databit = 0
                  num_smp = 0
                  flag_finish_1bit = 0
                  flag_maybe_found_startbit = 0
            # ストップビットであることが判明した時
            elif num_smp == int(smp_per_bit * 0.25) : # TODO : maybe can delete
                  flag_found_stopbit = 1              # TODO : delete
            # nbitの長さが終了
            elif current_bit != ex_bit and flag_maybe_found_startbit == 1 :
                  # データビットの内容を出力
                  for i in range(index_databit):
                        print(data_and_finish_bit[i], end="")
                  print("\n", end="")
                  flag_finish_1bit = 0
                  index_databit = 0
                  num_smp = 0
                  flag_found_stopbit = 0
                  flag_maybe_found_startbit = 1

      #データビットの処理
      elif flag_processing_databit == 1 :               # TODO flag_processing_databit = 0
            num_smp += 1
            # データビットが1か0か判明した時
            if num_smp == int(smp_per_bit * 0.25) :
                  flag_finish_1bit = 0
                  data_and_finish_bit[index_databit] = current_bit
                  index_databit += 1
            # 1ビットの長さが終了
            elif num_smp == int(smp_per_bit) :
                  num_smp = 0
                  flag_finish_1bit = 1


      #スタートビットぽいものを見つけた時の処理
      elif flag_maybe_found_startbit == 1 :
            num_smp += 1
            # スタートビットではなかった時
            #if current_bit != ex_bit and flag_found_startbit == 0 :
            if num_smp == int(smp_per_bit * 0.25) and current_bit != START_BIT :
                  num_smp = 0
                  flag_maybe_found_startbit = 0
            # スタートビットであることが判明した時
            if num_smp == int(smp_per_bit * 0.25) and current_bit == START_BIT :    # TODO : maybe can delete
                  flag_found_startbit = 1       # TODO : delete
            # 1bitの長さが終了
            if num_smp == int(smp_per_bit) :
                  num_smp = 0
                  flag_found_startbit = 0
                  flag_processing_databit = 1


      ex_bit = current_bit









waveFile.close()