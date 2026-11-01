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

// Keep existing local config.h files compatible with the cloud-capable firmware.
#ifndef KAREN_DEVICE_TOKEN
#define KAREN_DEVICE_TOKEN ""
#endif

// Existing private config.h files do not need to be replaced for this update.
#ifndef SPEAKER_GAIN
#define SPEAKER_GAIN 0.70f
#endif
static_assert(SPEAKER_GAIN>=0.0f&&SPEAKER_GAIN<=1.0f,
  "SPEAKER_GAIN must be between 0.0f and 1.0f.");

static const uint32_t RATE=16000;
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
bool connectWiFi(){
  if(WiFi.status()==WL_CONNECTED)return true;
  Serial.printf("[%lu ms][WIFI] Connecting; timeout=20 seconds. Credentials are hidden.\n",millis());
  WiFi.mode(WIFI_STA);WiFi.begin(WIFI_SSID,WIFI_PASSWORD);unsigned long start=millis();
  while(WiFi.status()!=WL_CONNECTED&&millis()-start<20000){delay(250);}
  if(WiFi.status()!=WL_CONNECTED){Serial.printf("[WIFI][ERROR] status=%d (%s), elapsed=%lu ms.\n",(int)WiFi.status(),wifiStatusName(WiFi.status()),millis()-start);return false;}
  Serial.printf("[WIFI] Connected; elapsed=%lu ms signal=%d dBm.\n",millis()-start,WiFi.RSSI());return true;
}
bool drainPendingReply(HTTPClient &http){
  // Consume the complete small JSON body before reusing its TLS connection.
  // Flask supplies Content-Length; reject unknown/chunked or oversized bodies.
  int remaining=http.getSize();
  if(remaining<=0||remaining>1024||!http.header("Content-Type").startsWith("application/json")||
      http.header("Transfer-Encoding").length()>0)return false;
  auto *stream=http.getStreamPtr();if(!stream)return false;
  uint8_t buffer[128];unsigned long started=millis();
  while(remaining>0&&millis()-started<15000){
    int available=stream->available();
    if(available>0){
      size_t wanted=(size_t)remaining;if(wanted>sizeof(buffer))wanted=sizeof(buffer);
      if(wanted>(size_t)available)wanted=(size_t)available;
      size_t received=stream->readBytes(buffer,wanted);
      if(!received)return false;
      remaining-=received;
    }else if(!http.connected())return false;
    else delay(1);
  }
  return remaining==0;
}
void logServerTiming(const String &header){
  // Only print known metric names and bounded integer durations. Never echo
  // arbitrary response headers, descriptions or body text into serial logs.
  if(header.length()>256)return;
  unsigned int start=0;
  while(start<header.length()){
    int comma=header.indexOf(',',start);
    String metric=header.substring(start,comma<0?header.length():(unsigned int)comma);metric.trim();
    int separator=metric.indexOf(";dur=");
    if(separator>0){
      String name=metric.substring(0,separator),duration=metric.substring(separator+5);
      bool known=name=="stt"||name=="gemini"||name=="tts"||name=="total";
      bool numeric=duration.length()>0&&duration.length()<=6;
      for(unsigned int i=0;i<duration.length();i++)if(duration[i]<'0'||duration[i]>'9')numeric=false;
      if(known&&numeric)Serial.printf("[HTTP] Backend timing %s_ms=%s\n",name.c_str(),duration.c_str());
    }
    if(comma<0)break;start=comma+1;
  }
}
bool requestReply(){
  Serial.printf("[%lu ms][HTTP] Streaming recorded WAV directly; no flash copy.\n",millis());
  WiFiClient plain;WiFiClientSecure secure;
  String origin=SERVER_ORIGIN;
  if(strlen(KAREN_DEVICE_TOKEN)>0&&!origin.startsWith("https://")){
    Serial.println("[HTTP][ERROR] Device authentication requires verified HTTPS.");return false;
  }
  if(origin.startsWith("https://")){
    if(strlen(ROOT_CA)<100){Serial.println("[TLS][ERROR] Set ROOT_CA in config.h before using HTTPS.");return false;}
    unsigned long clockStarted=millis();
    if(time(nullptr)<1700000000){
      Serial.println("[TLS] Synchronizing clock for certificate verification.");
      static bool clockConfigured=false;
      if(!clockConfigured){configTime(0,0,"pool.ntp.org","time.google.com");clockConfigured=true;}
      while(time(nullptr)<1700000000&&millis()-clockStarted<15000)delay(250);
    }
    Serial.printf("[TLS] clock_ms=%lu\n",millis()-clockStarted);
    if(time(nullptr)<1700000000){Serial.println("[TLS][ERROR] Clock sync failed; TLS needs correct time.");return false;}
    secure.setCACert(ROOT_CA);secure.setHandshakeTimeout(20);
  }else if(!origin.startsWith("http://")){Serial.println("[HTTP][ERROR] SERVER_ORIGIN must start with http:// or https://.");return false;}
  // HTTPClient has a 16-bit per-read timeout. Poll a bounded server job instead
  // of stretching a single socket past 65 seconds. Reuse the ID after a lost POST.
  char requestId[33];snprintf(requestId,sizeof(requestId),"%08lx%08lx%08lx%08lx",
    (unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random(),(unsigned long)esp_random());
  Serial.printf("[HTTP] Request %s; overall timeout=160 seconds.\n",requestId);
  const unsigned long started=millis();bool submitted=false;int posts=0,networkErrors=0;
  int polls=0,lastStatus=0;unsigned long lastProgress=0;
  HTTPClient http;
  // HTTP/1.1 plus a fully drained 202 body keeps the TCP/TLS session available
  // for the next poll. HTTP/1.0 previously repeated the handshake each time.
  http.useHTTP10(false);http.setReuse(true);
  const char *keys[]={"Content-Type","X-Karen-Result","X-Karen-Error","Server-Timing","Transfer-Encoding"};
  while(millis()-started<160000){
    String path=submitted?String("/requests/")+requestId:String("/chat");
    bool opened=origin.startsWith("https://")?http.begin(secure,origin+path):http.begin(plain,origin+path);
    if(!opened){Serial.println("[HTTP][ERROR] Cannot initialize request; check SERVER_ORIGIN syntax.");return false;}
    http.setConnectTimeout(10000);http.setTimeout(15000);
    http.collectHeaders(keys,5);
    if(strlen(KAREN_DEVICE_TOKEN)>0)http.addHeader("Authorization",String("Bearer ")+KAREN_DEVICE_TOKEN);
    int code;unsigned long roundStarted=millis();
    if(!submitted){
      http.addHeader("Content-Type","audio/wav");
      http.addHeader("Prefer","respond-async");http.addHeader("X-Request-ID",requestId);
      File input=LittleFS.open("/question.wav","r");if(!input){Serial.println("[FS][ERROR] Cannot open question.wav.");http.end();return false;}
      Serial.printf("[HTTP] POST attempt=%d bytes=%lu; waiting for backend.\n",posts+1,(unsigned long)input.size());
      posts++;code=http.sendRequest("POST",&input,input.size());input.close();submitted=true;
      Serial.printf("[HTTP] POST headers status=%d upload_ms=%lu (includes connection and response headers).\n",code,millis()-roundStarted);
    }else{
      polls++;code=http.GET();
      Serial.printf("[HTTP] Poll=%d status=%d headers_ms=%lu\n",polls,code,millis()-roundStarted);
    }
    if(code!=lastStatus||millis()-lastProgress>=15000){
      Serial.printf("[HTTP] status=%d elapsed=%lu ms%s\n",code,millis()-started,code==202?"; backend processing, keep waiting":"");
      lastStatus=code;lastProgress=millis();
    }
    if(code==202){
      if(!drainPendingReply(http)){
        Serial.printf("[HTTP][ERROR] Incomplete or unexpected processing body; failures=%d/4.\n",networkErrors+1);
        plain.stop();secure.stop();http.end();
        if(++networkErrors>3)return false;
      }else http.end();
      delay(1000);continue;
    }
    if(code<0){
      Serial.printf("[HTTP][ERROR] Transport: %s; failures=%d/4. Check backend, network and Windows Firewall.\n",HTTPClient::errorToString(code).c_str(),networkErrors+1);
      plain.stop();secure.stop();http.end();if(++networkErrors>3)return false;delay(1000);continue;
    }
    if(code==404&&posts<2){plain.stop();secure.stop();http.end();submitted=false;continue;}
    if(code!=200||!http.header("Content-Type").startsWith("audio/mpeg")){
      Serial.printf("[HTTP][ERROR] Server returned %d or unexpected audio type; request %s. Check Python console.\n",code,requestId);
      plain.stop();secure.stop();http.end();return false;
    }
    int expected=http.getSize();
    if(expected<=0||expected>512000){Serial.printf("[HTTP][ERROR] Unexpected audio size=%d; check Content-Length.\n",expected);plain.stop();secure.stop();http.end();return false;}
    File output=LittleFS.open("/reply.mp3","w");if(!output){Serial.println("[FS][ERROR] Cannot create reply.mp3.");plain.stop();secure.stop();http.end();return false;}
    logServerTiming(http.header("Server-Timing"));
    unsigned long downloadStarted=millis();
    int received=http.writeToStream(&output);output.close();
    Serial.printf("[HTTP] download_ms=%lu polls=%d\n",millis()-downloadStarted,polls);
    // Do not echo arbitrary server header/body text into shareable serial logs.
    String result=http.header("X-Karen-Result");
    Serial.printf("[HTTP] Result: %s; received=%d/%d bytes elapsed=%lu ms.\n",
      result=="ok"?"ok":result=="spoken-error"?"spoken-error":"unknown",received,expected,millis()-started);
    if(result=="spoken-error")Serial.printf("[HTTP][WARN] Backend generated a spoken error. Match request %s in Python logs.\n",requestId);
    plain.stop();secure.stop();http.end();return received==expected;
  }
  Serial.printf("[HTTP][ERROR] Timed out. Inspect /requests/%s before starting another turn.\n",requestId);return false;
}
bool playReply(unsigned long turnStarted){
  Serial.printf("[%lu ms][PLAY] Starting MP3 decoder; gain=%.2f.\n",millis(),(double)SPEAKER_GAIN);
  AudioFileSourceLittleFS source("/reply.mp3");AudioOutputI2S out;
  out.SetPinout(AMP_BCLK,AMP_WS,AMP_DATA);out.SetGain(SPEAKER_GAIN);
  AudioGeneratorMP3 decoder;
  if(!decoder.begin(&source,&out)){Serial.println("[PLAY][ERROR] MP3 decoder did not start.");return false;}
  unsigned long start=millis();
  Serial.printf("[TURN] button_to_playback_ms=%lu; decoder ready, excludes reply duration.\n",start-turnStarted);
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
  // This USB-powered voice device favors response latency over modem power saving.
  if(!WiFi.setSleep(false))Serial.println("[WIFI][WARN] Could not disable modem sleep.");
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
    else if(!playReply(turnStarted))fail("Playback failed. Check amplifier and decoder.");
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
