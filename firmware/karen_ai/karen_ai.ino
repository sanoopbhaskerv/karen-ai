// Targets: classic ESP32 and ESP32-S3, Arduino-ESP32 3.x, ESP8266Audio 2.x.
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
#include "controller.h"

static const uint32_t RATE=16000;
static const char *BOUNDARY="KarenESP32Boundary7d29";
i2s_chan_handle_t mic=nullptr;
void statusLED(bool on){if(STATUS_LED>=0)digitalWrite(STATUS_LED,on?HIGH:LOW);}
void fail(const char* message){ Serial.printf("[%lu ms][ERROR] %s\n",millis(),message); for(int i=0;i<3;i++){statusLED(true);delay(130);statusLED(false);delay(130);} }
const char* wifiStatusName(wl_status_t status){
  switch(status){
    case WL_NO_SSID_AVAIL:return "network not found (check 2.4 GHz)";
    case WL_CONNECT_FAILED:return "connection failed (check password/security)";
    case WL_CONNECTION_LOST:return "connection lost";
    case WL_DISCONNECTED:return "disconnected";
    case WL_IDLE_STATUS:return "not connected yet";
    case WL_CONNECTED:return "connected";
    default:return "unknown";
  }
}
void u16(File &f,uint16_t v){uint8_t b[2]={(uint8_t)v,(uint8_t)(v>>8)};f.write(b,2);}
void u32(File &f,uint32_t v){uint8_t b[4]={(uint8_t)v,(uint8_t)(v>>8),(uint8_t)(v>>16),(uint8_t)(v>>24)};f.write(b,4);}
void wavHeader(File &f,uint32_t bytes){f.print("RIFF");u32(f,bytes+36);f.print("WAVEfmt ");u32(f,16);u16(f,1);u16(f,1);u32(f,RATE);u32(f,RATE*2);u16(f,2);u16(f,16);f.print("data");u32(f,bytes);}
void stopMic(){if(mic){i2s_channel_disable(mic);i2s_del_channel(mic);mic=nullptr;}}
bool startMic(){
  i2s_chan_config_t channel=I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0,I2S_ROLE_MASTER);
  esp_err_t error=i2s_new_channel(&channel,nullptr,&mic);
  if(error!=ESP_OK){Serial.printf("[MIC][ERROR] Create I2S channel: %s\n",esp_err_to_name(error));return false;}
  i2s_std_config_t cfg={};
  cfg.clk_cfg=I2S_STD_CLK_DEFAULT_CONFIG(RATE);
  cfg.slot_cfg=I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT,I2S_SLOT_MODE_MONO);
  cfg.slot_cfg.slot_mask=I2S_STD_SLOT_LEFT;
  cfg.gpio_cfg.mclk=I2S_GPIO_UNUSED;
  cfg.gpio_cfg.bclk=(gpio_num_t)MIC_BCLK;cfg.gpio_cfg.ws=(gpio_num_t)MIC_WS;
  cfg.gpio_cfg.dout=I2S_GPIO_UNUSED;cfg.gpio_cfg.din=(gpio_num_t)MIC_DATA;
  error=i2s_channel_init_std_mode(mic,&cfg);
  if(error!=ESP_OK){Serial.printf("[MIC][ERROR] Configure I2S: %s\n",esp_err_to_name(error));stopMic();return false;}
  error=i2s_channel_enable(mic);
  if(error!=ESP_OK){Serial.printf("[MIC][ERROR] Enable I2S: %s\n",esp_err_to_name(error));stopMic();return false;}
  return true;
}
bool recordQuestion(){
  unsigned long started=millis();
  Serial.printf("[MIC] Starting %d-second recording at %lu Hz; MIC_SHIFT=%d.\n",RECORD_SECONDS,(unsigned long)RATE,MIC_SHIFT);
  if(!startMic())return false;
  File f=LittleFS.open("/question.wav","w");if(!f){Serial.println("[FS][ERROR] Cannot create question.wav; check free flash.");stopMic();return false;}
  const uint32_t target=RATE*RECORD_SECONDS;wavHeader(f,target*2);
  int32_t raw[256];int16_t pcm[256];size_t got=0;uint32_t written=0;
  // Discard initial DMA samples while the microphone stabilizes.
  for(int i=0;i<8;i++)i2s_channel_read(mic,raw,sizeof(raw),&got,1000);
  Serial.println("[MIC] Recording. Speak now.");statusLED(true);
  bool ok=true;
  int32_t minimum=32767,maximum=-32768;
  uint32_t zeroSamples=0,clippedSamples=0;
  uint64_t absoluteSum=0;
  while(written<target){
    esp_err_t error=i2s_channel_read(mic,raw,sizeof(raw),&got,1000);
    if(error!=ESP_OK||got==0){Serial.printf("[MIC][ERROR] I2S read: %s; received=%u bytes.\n",esp_err_to_name(error),(unsigned)got);ok=false;break;}
    size_t n=got/4;if(n>target-written)n=target-written;
    for(size_t i=0;i<n;i++){
      int32_t s=raw[i]>>MIC_SHIFT;
      if(s<=-32768||s>=32767)clippedSamples++;
      pcm[i]=(int16_t)constrain(s,-32768,32767);
      int32_t sample=pcm[i];
      if(sample<minimum)minimum=sample;if(sample>maximum)maximum=sample;
      if(sample==0)zeroSamples++;
      absoluteSum+=(sample<0?-sample:sample);
    }
    if(f.write((uint8_t*)pcm,n*2)!=n*2){Serial.println("[FS][ERROR] Short recording write; check free flash.");ok=false;break;}written+=n;yield();
  }
  f.close();stopMic();statusLED(false);
  Serial.printf("[MIC] %s elapsed=%lu ms samples=%lu/%lu min=%ld max=%ld mean_abs=%lu zero=%lu clipped=%lu\n",
    ok&&written==target?"Complete":"Incomplete",millis()-started,(unsigned long)written,(unsigned long)target,
    (long)minimum,(long)maximum,(unsigned long)(written?absoluteSum/written:0),
    (unsigned long)zeroSamples,(unsigned long)clippedSamples);
  if(written&&zeroSamples==written)Serial.println("[MIC][WARN] All samples are zero. Power off and check 3V3/GND, SD and L/R-to-GND wiring.");
  else if(written&&maximum-minimum<32)Serial.println("[MIC][WARN] Very little signal. Try speaking close to the microphone, then check its wiring.");
  if(written&&clippedSamples>written/100)Serial.println("[MIC][WARN] More than 1% clipped samples. Move farther away; check MIC_SHIFT before changing gain.");
  return ok&&written==target;
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
  Serial.printf("[%lu ms][WIFI] Connecting; timeout=20 seconds. Credentials are hidden.\n",millis());
  WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);unsigned long start=millis();
  while(WiFi.status()!=WL_CONNECTED&&millis()-start<20000){delay(250);}
  if(WiFi.status()!=WL_CONNECTED){Serial.printf("[WIFI][ERROR] status=%d (%s), elapsed=%lu ms.\n",(int)WiFi.status(),wifiStatusName(WiFi.status()),millis()-start);return false;}
  Serial.printf("[WIFI] Connected; elapsed=%lu ms signal=%d dBm.\n",millis()-start,WiFi.RSSI());return true;
}
bool requestReply(){
  Serial.printf("[%lu ms][HTTP] Preparing audio upload.\n",millis());
  if(!createMultipart()){Serial.println("[FS][ERROR] Cannot prepare multipart upload; check free flash.");return false;}
  WiFiClient plain;WiFiClientSecure secure;
  String origin=SERVER_ORIGIN;
  if(origin.startsWith("https://")){
    if(strlen(ROOT_CA)<100){Serial.println("[TLS][ERROR] Set ROOT_CA in config.h before using HTTPS.");return false;}
    Serial.println("[TLS] Synchronizing clock for certificate verification.");
    configTime(0,0,"pool.ntp.org","time.google.com");unsigned long start=millis();
    while(time(nullptr)<1700000000&&millis()-start<15000)delay(250);
    if(time(nullptr)<1700000000){Serial.println("[TLS][ERROR] Clock sync failed; TLS needs correct time.");return false;}
    secure.setCACert(ROOT_CA);secure.setHandshakeTimeout(20);
  }else if(!origin.startsWith("http://")){Serial.println("[HTTP][ERROR] SERVER_ORIGIN must start with http:// or https://.");return false;}
  // HTTPClient has a 16-bit per-read timeout. Poll a bounded server job instead
  // of stretching a single socket past 65 seconds. Reuse the ID after a lost POST.
  char requestId[33];snprintf(requestId,sizeof(requestId),"%08lx%08lx%08lx%08lx",
    (unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random());
  Serial.printf("[HTTP] Request %s; overall timeout=160 seconds.\n",requestId);
  const unsigned long started=millis();bool submitted=false;int posts=0,networkErrors=0;
  int lastStatus=0;unsigned long lastProgress=0;
  while(millis()-started<160000){
    HTTPClient http;
    String path=submitted?String("/requests/")+requestId:String("/chat");
    bool opened=origin.startsWith("https://")?http.begin(secure,origin+path):http.begin(plain,origin+path);
    if(!opened){Serial.println("[HTTP][ERROR] Cannot initialize request; check SERVER_ORIGIN syntax.");return false;}
    http.setConnectTimeout(10000);http.setTimeout(15000);http.useHTTP10(true);
    const char *keys[]={"Content-Type","X-Karen-Result","X-Karen-Error"};http.collectHeaders(keys,3);
    int code;
    if(!submitted){
      http.addHeader("Content-Type",String("multipart/form-data; boundary=")+BOUNDARY);
      http.addHeader("Prefer","respond-async");http.addHeader("X-Request-ID",requestId);
      File input=LittleFS.open("/upload.bin","r");if(!input){Serial.println("[FS][ERROR] Cannot open upload.bin.");http.end();return false;}
      Serial.printf("[HTTP] POST attempt=%d bytes=%lu; waiting for backend.\n",posts+1,(unsigned long)input.size());
      posts++;code=http.sendRequest("POST",&input,input.size());input.close();submitted=true;
    }else{code=http.GET();}
    if(code!=lastStatus||millis()-lastProgress>=15000){
      Serial.printf("[HTTP] status=%d elapsed=%lu ms%s\n",code,millis()-started,code==202?"; backend processing, keep waiting":"");
      lastStatus=code;lastProgress=millis();
    }
    if(code==202){http.end();delay(1000);continue;}
    if(code<0){
      Serial.printf("[HTTP][ERROR] Transport: %s; failures=%d/4. Check backend, network and Windows Firewall.\n",HTTPClient::errorToString(code).c_str(),networkErrors+1);
      http.end();if(++networkErrors>3)return false;delay(1000);continue;
    }
    if(code==404&&posts<2){http.end();submitted=false;continue;}
    if(code!=200||!http.header("Content-Type").startsWith("audio/mpeg")){
      Serial.printf("[HTTP][ERROR] Server returned %d or unexpected audio type; request %s. Check Python console.\n",code,requestId);
      http.end();return false;
    }
    int expected=http.getSize();
    if(expected<=0||expected>512000){Serial.printf("[HTTP][ERROR] Unexpected audio size=%d; check Content-Length.\n",expected);http.end();return false;}
    File output=LittleFS.open("/reply.mp3","w");if(!output){Serial.println("[FS][ERROR] Cannot create reply.mp3.");http.end();return false;}
    int received=http.writeToStream(&output);output.close();
    // Do not echo arbitrary server header/body text into shareable serial logs.
    String result=http.header("X-Karen-Result");
    Serial.printf("[HTTP] Result: %s; received=%d/%d bytes elapsed=%lu ms.\n",
      result=="ok"?"ok":result=="spoken-error"?"spoken-error":"unknown",received,expected,millis()-started);
    if(result=="spoken-error")Serial.printf("[HTTP][WARN] Backend generated a spoken error. Match request %s in Python logs.\n",requestId);
    http.end();return received==expected;
  }
  Serial.printf("[HTTP][ERROR] Timed out. Inspect /requests/%s before starting another turn.\n",requestId);return false;
}
bool playReply(){
  Serial.printf("[%lu ms][PLAY] Starting MP3 decoder; gain=0.35.\n",millis());
  AudioFileSourceLittleFS source("/reply.mp3");AudioOutputI2S out;
  out.SetPinout(AMP_BCLK,AMP_WS,AMP_DATA);out.SetGain(0.35);
  AudioGeneratorMP3 decoder;
  if(!decoder.begin(&source,&out)){Serial.println("[PLAY][ERROR] MP3 decoder did not start.");return false;}
  unsigned long start=millis();
  while(decoder.isRunning()&&millis()-start<90000){if(!decoder.loop())decoder.stop();yield();}
  bool ok=millis()-start<90000;decoder.stop();out.stop();
  Serial.printf("[PLAY] %s elapsed=%lu ms. I2S output does not confirm audible speaker sound.\n",ok?"Decoder finished":"Timed out",millis()-start);return ok;
}
void cleanup(){LittleFS.remove("/question.wav");LittleFS.remove("/upload.bin");LittleFS.remove("/reply.mp3");}
void setup(){
  Serial.begin(115200);pinMode(BUTTON_PIN,INPUT_PULLUP);if(STATUS_LED>=0)pinMode(STATUS_LED,OUTPUT);
  Serial.printf("\n[BOOT] Karen AI | Controller: %s | flash: %lu bytes | PSRAM: %lu bytes\n",KarenController::name,
    (unsigned long)ESP.getFlashChipSize(),(unsigned long)ESP.getPsramSize());
  Serial.printf("[BOOT] heap_free=%lu bytes | PSRAM_free=%lu bytes | baud=115200\n",(unsigned long)ESP.getFreeHeap(),(unsigned long)ESP.getFreePsram());
  Serial.printf("[BOOT] MIC BCLK/WS/SD: %d/%d/%d | AMP BCLK/WS/DIN: %d/%d/%d | button: %d\n",
    MIC_BCLK,MIC_WS,MIC_DATA,AMP_BCLK,AMP_WS,AMP_DATA,BUTTON_PIN);
#if defined(CONFIG_IDF_TARGET_ESP32S3)
  if(ESP.getFlashChipSize()!=16UL*1024*1024)Serial.println("[BOOT][WARN] S3 profile expects 16 MB flash. Stop and verify the board before continuing.");
  if(ESP.getPsramSize()!=8UL*1024*1024)Serial.println("[BOOT][WARN] N16R8 expects 8 MB PSRAM. Check board identity, OPI PSRAM setting and boot errors.");
#endif
  // Formatting on first boot erases this app's flash filesystem only.
  Serial.println("[FS] Mounting; first boot may format the app filesystem.");
  if(!LittleFS.begin(true)){fail("LittleFS failed. Select a partition with >=1.5 MB filesystem.");while(true)delay(1000);}
  Serial.printf("[FS] total=%lu used=%lu bytes before temporary-audio cleanup.\n",(unsigned long)LittleFS.totalBytes(),(unsigned long)LittleFS.usedBytes());
  cleanup();if(!connectWiFi())fail("WiFi unavailable. Will retry when button is pressed.");
  if(digitalRead(BUTTON_PIN)==LOW)Serial.println("[BUTTON][WARN] Button is already LOW. Check it is released and uses opposite switch contacts.");
  Serial.println("[READY] Press the external button, then speak when [MIC] says Speak now.");
}
void loop(){
  if(digitalRead(BUTTON_PIN)==LOW){
    delay(40);if(digitalRead(BUTTON_PIN)!=LOW)return;
    unsigned long turnStarted=millis();
    Serial.printf("[%lu ms][BUTTON] Press accepted; heap_free=%lu bytes.\n",millis(),(unsigned long)ESP.getFreeHeap());
    if(!connectWiFi())fail("Hotspot connection failed.");
    else if(!recordQuestion())fail("Recording failed. Check microphone and free flash.");
    else if(!requestReply())fail("Request failed. Check server and TLS settings.");
    else if(!playReply())fail("Playback failed. Check amplifier and decoder.");
    cleanup();
    Serial.printf("[TURN] Finished elapsed=%lu ms; heap_free=%lu bytes. Release the button.\n",millis()-turnStarted,(unsigned long)ESP.getFreeHeap());
    unsigned long releaseStarted=millis();bool warned=false;
    while(digitalRead(BUTTON_PIN)==LOW){
      if(!warned&&millis()-releaseStarted>3000){Serial.println("[BUTTON][WARN] Still LOW. Release the button; if released, power off and check switch contacts/GND wiring.");warned=true;}
      delay(20);
    }
    delay(200);Serial.println("[READY] Waiting for the next button press.");
  }
  delay(10);
}
