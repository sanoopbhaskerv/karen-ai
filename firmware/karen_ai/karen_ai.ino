// Target: classic ESP32 Dev Module, Arduino-ESP32 3.x (ESP-IDF 5.x), ESP8266Audio 2.x.
// Recording and playback use I2S sequentially. Files are streamed to flash, not held in RAM.
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <LittleFS.h>
#include <driver/i2s_std.h>
#include <AudioFileSourceLittleFS.h>
#include <AudioGeneratorMP3.h>
#include <AudioOutputI2S.h>
#include <time.h>
#include "config.h"

static const uint32_t RATE=16000;
static const char *BOUNDARY="KarenESP32Boundary7d29";
i2s_chan_handle_t mic=nullptr;
void fail(const char* message){ Serial.println(message); for(int i=0;i<3;i++){digitalWrite(STATUS_LED,HIGH);delay(130);digitalWrite(STATUS_LED,LOW);delay(130);} }
void u16(File &f,uint16_t v){uint8_t b[2]={(uint8_t)v,(uint8_t)(v>>8)};f.write(b,2);}
void u32(File &f,uint32_t v){uint8_t b[4]={(uint8_t)v,(uint8_t)(v>>8),(uint8_t)(v>>16),(uint8_t)(v>>24)};f.write(b,4);}
void wavHeader(File &f,uint32_t bytes){f.print("RIFF");u32(f,bytes+36);f.print("WAVEfmt ");u32(f,16);u16(f,1);u16(f,1);u32(f,RATE);u32(f,RATE*2);u16(f,2);u16(f,16);f.print("data");u32(f,bytes);}
void stopMic(){if(mic){i2s_channel_disable(mic);i2s_del_channel(mic);mic=nullptr;}}
bool startMic(){
  i2s_chan_config_t channel=I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0,I2S_ROLE_MASTER);
  if(i2s_new_channel(&channel,nullptr,&mic)!=ESP_OK)return false;
  i2s_std_config_t cfg={};
  cfg.clk_cfg=I2S_STD_CLK_DEFAULT_CONFIG(RATE);
  cfg.slot_cfg=I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT,I2S_SLOT_MODE_MONO);
  cfg.slot_cfg.slot_mask=I2S_STD_SLOT_LEFT;
  cfg.gpio_cfg.mclk=I2S_GPIO_UNUSED;
  cfg.gpio_cfg.bclk=(gpio_num_t)MIC_BCLK;cfg.gpio_cfg.ws=(gpio_num_t)MIC_WS;
  cfg.gpio_cfg.dout=I2S_GPIO_UNUSED;cfg.gpio_cfg.din=(gpio_num_t)MIC_DATA;
  if(i2s_channel_init_std_mode(mic,&cfg)!=ESP_OK){stopMic();return false;}
  if(i2s_channel_enable(mic)!=ESP_OK){stopMic();return false;}
  return true;
}
bool recordQuestion(){
  if(!startMic())return false;
  File f=LittleFS.open("/question.wav","w");if(!f){stopMic();return false;}
  const uint32_t target=RATE*RECORD_SECONDS;wavHeader(f,target*2);
  int32_t raw[256];int16_t pcm[256];size_t got=0;uint32_t written=0;
  // Discard initial DMA samples while the microphone stabilizes.
  for(int i=0;i<8;i++)i2s_channel_read(mic,raw,sizeof(raw),&got,1000);
  Serial.println("Recording. Speak now.");digitalWrite(STATUS_LED,HIGH);
  bool ok=true;
  while(written<target){
    if(i2s_channel_read(mic,raw,sizeof(raw),&got,1000)!=ESP_OK||got==0){ok=false;break;}
    size_t n=got/4;if(n>target-written)n=target-written;
    for(size_t i=0;i<n;i++){int32_t s=raw[i]>>MIC_SHIFT;pcm[i]=(int16_t)constrain(s,-32768,32767);}
    if(f.write((uint8_t*)pcm,n*2)!=n*2){ok=false;break;}written+=n;yield();
  }
  f.close();stopMic();digitalWrite(STATUS_LED,LOW);return ok&&written==target;
}
bool createMultipart(){
  File src=LittleFS.open("/question.wav","r"),dst=LittleFS.open("/upload.bin","w");
  if(!src||!dst)return false;
  String head=String("--")+BOUNDARY+"\r\nContent-Disposition: form-data; name=\"audio\"; filename=\"question.wav\"\r\nContent-Type: audio/wav\r\n\r\n";
  if(dst.print(head)!=head.length())return false;
  uint8_t buffer[1024];while(src.available()){size_t n=src.read(buffer,sizeof(buffer));if(!n||dst.write(buffer,n)!=n)return false;yield();}
  String tail=String("\r\n--")+BOUNDARY+"--\r\n";bool ok=dst.print(tail)==tail.length();src.close();dst.close();return ok;
}
bool connectWiFi(){
  if(WiFi.status()==WL_CONNECTED)return true;
  WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);unsigned long start=millis();
  while(WiFi.status()!=WL_CONNECTED&&millis()-start<20000){delay(250);}
  if(WiFi.status()!=WL_CONNECTED)return false;
  Serial.print("Connected: ");Serial.println(WiFi.localIP());return true;
}
bool requestReply(){
  if(!createMultipart())return false;
  WiFiClient plain;WiFiClientSecure secure;HTTPClient http;
  String origin=SERVER_ORIGIN;
  if(origin.startsWith("https://")){
    if(strlen(ROOT_CA)<100){Serial.println("Set ROOT_CA in config.h before using HTTPS.");return false;}
    configTime(0,0,"pool.ntp.org","time.google.com");unsigned long start=millis();
    while(time(nullptr)<1700000000&&millis()-start<15000)delay(250);
    if(time(nullptr)<1700000000){Serial.println("Clock sync failed; TLS needs correct time.");return false;}
    secure.setCACert(ROOT_CA);secure.setHandshakeTimeout(20);
    if(!http.begin(secure,origin+"/chat"))return false;
  }else if(origin.startsWith("http://")){
    if(!http.begin(plain,origin+"/chat"))return false;
  }else{return false;}
  http.setConnectTimeout(15000);http.setTimeout(60000);
  // Known-length HTTP/1.0 response avoids chunked decoding on the flash writer.
  http.useHTTP10(true);
  const char *keys[]={"Content-Type","X-Karen-Result"};http.collectHeaders(keys,2);
  http.addHeader("Content-Type",String("multipart/form-data; boundary=")+BOUNDARY);
  File input=LittleFS.open("/upload.bin","r");if(!input){http.end();return false;}
  Serial.println("Sending question; waiting for Karen…");int code=http.sendRequest("POST",&input,input.size());input.close();
  if(code!=200||!http.header("Content-Type").startsWith("audio/mpeg")){Serial.printf("Server returned %d. Check dashboard/key/network.\n",code);http.end();return false;}
  int expected=http.getSize();
  if(expected<=0||expected>512000){Serial.println("Unexpected audio size; check proxy Content-Length.");http.end();return false;}
  File output=LittleFS.open("/reply.mp3","w");if(!output){http.end();return false;}
  int received=http.writeToStream(&output);output.close();
  Serial.println(http.header("X-Karen-Result"));http.end();
  return received==expected;
}
bool playReply(){
  AudioFileSourceLittleFS source("/reply.mp3");AudioOutputI2S out;
  out.SetPinout(AMP_BCLK,AMP_WS,AMP_DATA);out.SetGain(0.35);
  AudioGeneratorMP3 decoder;
  if(!decoder.begin(&source,&out))return false;
  unsigned long start=millis();
  while(decoder.isRunning()&&millis()-start<90000){if(!decoder.loop())decoder.stop();yield();}
  bool ok=millis()-start<90000;decoder.stop();out.stop();return ok;
}
void cleanup(){LittleFS.remove("/question.wav");LittleFS.remove("/upload.bin");LittleFS.remove("/reply.mp3");}
void setup(){
  Serial.begin(115200);pinMode(BUTTON_PIN,INPUT_PULLUP);pinMode(STATUS_LED,OUTPUT);
  // Formatting on first boot erases this app's flash filesystem only.
  if(!LittleFS.begin(true)){fail("LittleFS failed. Select a partition with >=1.5 MB filesystem.");while(true)delay(1000);}
  cleanup();if(!connectWiFi())fail("WiFi unavailable. Will retry when button is pressed.");
  Serial.println("Ready. Press button, then speak for five seconds.");
}
void loop(){
  if(digitalRead(BUTTON_PIN)==LOW){
    delay(40);if(digitalRead(BUTTON_PIN)!=LOW)return;
    if(!connectWiFi())fail("Hotspot connection failed.");
    else if(!recordQuestion())fail("Recording failed. Check microphone and free flash.");
    else if(!requestReply())fail("Request failed. Check server and TLS settings.");
    else if(!playReply())fail("Playback failed. Check amplifier and decoder.");
    cleanup();while(digitalRead(BUTTON_PIN)==LOW)delay(20);delay(200);Serial.println("Ready.");
  }
  delay(10);
}
