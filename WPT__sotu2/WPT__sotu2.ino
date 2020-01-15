
#include <si5351.h>
#include <Wire.h>
#include<MsTimer2.h>
Si5351 si5351;

unsigned long long freq = 5000000ULL;           /*出力周波数50kHz(これをいじって周波数を変える)freq×0.01=周波数Hz*/
unsigned long long pll_freq = 70500000000ULL;   /*PLL周波数(いじるな)*/

String data;
float data0 = 0;
float f = 0;

void setup() {

  Serial.begin(57600);
  MsTimer2::set(100, flash);

  bool i2c_found;                                         /*I2C通信ができるかどうかブール値を入れる変数*/
  i2c_found = si5351.init(SI5351_CRYSTAL_LOAD_8PF, 0, 0);  /*I2C通信を確認(ライブラリreadme参照)*/
  if (!i2c_found) {
    Serial.println("Error:I2C");
  }

  si5351.init(SI5351_CRYSTAL_LOAD_8PF, 0, 0);             /*振動子負荷容量(使うモジュールが8pFなのでこれ)*/
  si5351.set_freq_manual(freq, pll_freq, SI5351_CLK0);    /*出力周波数,PLL周波数,設定先出力ピン設定*/
  si5351.set_phase(SI5351_CLK0, 0);                       /*位相(今回特に意味はない)*/
  si5351.pll_reset(SI5351_PLLA);                          /*PLLをリセット（使う前に一回リセット）*/
  si5351.update_status();                                 /*si5351のステータスを読む(今回特に使っていない)*/

  while (Serial.available() == 0);
}




void flash(void) {
  int i = analogRead(0);
  f = i * 5.0 / 1023.0;
  Serial.println(f);
}

void loop() {
  char aizu = Serial.read();
  if (aizu == 'a') {
    MsTimer2::stop(); //新しいduty比に変更されるまでflash関数を止める
    aizu = 'c';
    receive_duty_data();
    MsTimer2::start();
  }

  else if (aizu == 'b') {
    MsTimer2::stop();
    si5351.set_freq(400000, SI5351_CLK0);    /*信号を止める*/            /*!!!!!set_freq(0)!!!これでは止まらない!!!!!*/
  }

  else if (aizu == 'c') {
    //pass
  }
}

void receive_duty_data() {
  data = Serial.readString();
  data0 = data.toFloat();
  unsigned long long freq = data0 * 100000; /*1=0.01Hzなので末尾に00をつける.入力単位をキロにしたいので末尾に10^3をつける．*/
  si5351.set_freq(freq, SI5351_CLK0);       /*周波数セット*/
  si5351.pll_reset(SI5351_PLLA);            /*念のためPLLをリセット*/
  si5351.update_status();
}
