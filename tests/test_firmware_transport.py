"""Run the real firmware HTTP flow against scripted host-side transports.

These tests exercise control flow, not radio/TLS performance. Both actual board
cross-compiles remain necessary to check Espressif/Arduino API compatibility.
"""
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[1]


HARNESS = r'''
#include <algorithm>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <ctime>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

void check(bool value, const char *message) {
  if (!value) throw std::runtime_error(message);
}
class String : public std::string {
public:
  using std::string::string;
  String(const std::string &s) : std::string(s) {}
  String(int n) : std::string(std::to_string(n)) {}
  bool startsWith(const char *s) const { return rfind(s, 0) == 0; }
  String substring(size_t begin, size_t end = std::string::npos) const {
    return substr(begin, end == std::string::npos ? end : end - begin);
  }
  int indexOf(char c, size_t begin = 0) const {
    auto n = find(c, begin); return n == npos ? -1 : int(n);
  }
  int indexOf(const char *s, size_t begin = 0) const {
    auto n = find(s, begin); return n == npos ? -1 : int(n);
  }
  void trim() {
    auto first = find_first_not_of(" \r\n\t"), last = find_last_not_of(" \r\n\t");
    *this = first == npos ? String("") : String(substr(first, last - first + 1));
  }
};
struct SerialClass {
  std::string output;
  void println(const char *s) { output += s; output += '\n'; }
  void println(const String &s) { println(s.c_str()); }
  template <typename... Args> void printf(const char *format, Args... args) {
    char buffer[2048]; std::snprintf(buffer, sizeof(buffer), format, args...); output += buffer;
  }
} Serial;
unsigned long clockMs = 0;
unsigned long millis() { return clockMs++; }
void delay(unsigned long ms) { clockMs += ms; }
void yield() { clockMs++; }
void configTime(int, int, const char*, const char*) {}
uint32_t esp_random() { static uint32_t n = 100; return ++n; }
const char *SERVER_ORIGIN = "https://example.test";
const char *KAREN_DEVICE_TOKEN = "private-test-token";
const char ROOT_CA[] = "test certificate placeholder repeated test certificate placeholder repeated test certificate placeholder repeated test certificate placeholder";

class Stream {
public:
  virtual ~Stream() = default;
  virtual int available() { return 0; }
  virtual int read() { return -1; }
  virtual int peek() { return -1; }
  virtual void flush() {}
  virtual size_t write(uint8_t) { return 1; }
  virtual size_t write(const uint8_t *p, size_t n) {
    for (size_t i = 0; i < n; ++i) write(p[i]); return n;
  }
  size_t readBytes(char *p, size_t n) {
    size_t i = 0; while (i < n && available()) p[i++] = char(read()); return i;
  }
  size_t readBytes(uint8_t *p, size_t n) { return readBytes((char*)p, n); }
};
std::string audioWritten;
std::vector<std::string> openedFiles;
class File : public Stream {
public:
  std::string path;
  File(std::string p = "") : path(p) {}
  explicit operator bool() const { return !path.empty(); }
  size_t size() { return 160044; }
  void close() {}
  size_t write(uint8_t b) override { audioWritten += char(b); return 1; }
  size_t write(const uint8_t *p, size_t n) override {
    audioWritten.append((const char*)p, n); return n;
  }
};
struct FS {
  File open(const char *path, const char *) {
    openedFiles.emplace_back(path); return File(path);
  }
} LittleFS;
int socketStops = 0, consumedPending = 0;
class WiFiClient : public Stream {
public:
  bool open = false;
  std::string body;
  size_t position = 0;
  int available() override { return int(body.size() - position); }
  int read() override {
    if (position >= body.size()) return -1;
    int value = uint8_t(body[position++]);
    if (position == body.size() && body.find("processing") != std::string::npos) ++consumedPending;
    return value;
  }
  int peek() override { return position < body.size() ? uint8_t(body[position]) : -1; }
  bool connected() { return open; }
  void stop() { ++socketStops; open = false; body.clear(); position = 0; }
  void setTimeout(unsigned long) {}
};
using NetworkClient = WiFiClient;
class WiFiClientSecure : public WiFiClient {
public:
  void setCACert(const char *) {}
  void setHandshakeTimeout(int) {}
};
struct Reply {
  int code;
  int length;
  std::string body;
  std::string type = "application/json";
  bool closed = false;
  std::string encoding;
};
std::vector<Reply> script;
std::vector<std::string> methods, requestIds, requestedUrls;
std::vector<int> connectionNumbers;
int nextReply = 0, connections = 0;
std::string timingHeader = "stt;dur=10, gemini;dur=20, tts;dur=30";
class HTTPClient {
  WiFiClient *client = nullptr;
  std::map<std::string, std::string> headers;
  Reply reply{0, 0, ""};
  bool reuse = true;
  bool http10 = false;
public:
  bool begin(WiFiClient &c, const String &url) {
    client = &c; headers.clear(); requestedUrls.push_back(url); return true;
  }
  void setConnectTimeout(int) {}
  void setTimeout(int) {}
  void useHTTP10(bool enabled) { http10 = enabled; reuse = !enabled; }
  void setReuse(bool enabled) { reuse = enabled; }
  void collectHeaders(const char **, size_t) {}
  void addHeader(const char *name, const String &value) { headers[name] = value; }
  int perform(const char *method) {
    check(!http10 && reuse, "Polling must use reusable HTTP/1.1");
    if (client->open) check(client->available() == 0, "Unread response body reused as next HTTP response");
    else { ++connections; client->open = true; }
    connectionNumbers.push_back(connections); methods.emplace_back(method);
    check(headers["Authorization"] == "Bearer private-test-token", "Device token missing");
    if (std::string(method) == "POST") {
      check(headers["Content-Type"] == "audio/wav", "POST must stream the raw WAV");
      check(headers["Prefer"] == "respond-async", "Async request preference missing");
      check(!headers["X-Request-ID"].empty(), "Request ID missing");
      requestIds.push_back(headers["X-Request-ID"]);
    } else {
      check(!requestIds.empty() && requestedUrls.back() == std::string(SERVER_ORIGIN) + "/requests/" + requestIds.front(),
            "Polling changed the logical request ID");
    }
    check(nextReply < int(script.size()), "Unexpected extra HTTP attempt");
    reply = script[nextReply++]; client->body = reply.body; client->position = 0;
    if (reply.closed) client->open = false;
    return reply.code;
  }
  int sendRequest(const char *method, File *input, size_t bytes) {
    check(input->path == "/question.wav", "Unexpected upload file");
    check(bytes == 160044, "Upload length changed"); return perform(method);
  }
  int GET() { return perform("GET"); }
  int getSize() { return reply.length; }
  bool connected() { return client->connected(); }
  WiFiClient *getStreamPtr() { return client; }
  int writeToStream(Stream *output) {
    auto body = client->body.substr(client->position);
    size_t written = output->write((const uint8_t*)body.data(), body.size());
    client->position += written;
    if (reply.code == 202) ++consumedPending;
    return int(written);
  }
  String header(const char *name) {
    if (std::string(name) == "Content-Type") return reply.type;
    if (std::string(name) == "X-Karen-Result") return "ok";
    if (std::string(name) == "Transfer-Encoding") return reply.encoding;
    if (std::string(name) == "Server-Timing") return timingHeader;
    return "";
  }
  static String errorToString(int) { return "simulated transport failure"; }
  void end() { if (client && !reuse) client->stop(); }
};
'''


RUNNER = r'''
int main(int argc, char **argv) {
  try {
    check(argc == 2, "Expected scenario");
    std::string scenario = argv[1];
    Reply pending{202, 23, "{\"status\":\"processing\"}"};
    pending.length = pending.body.size();
    Reply audio{200, 8, "ID3reply", "audio/mpeg"};
    bool expected = true;
    if (scenario == "pending") script = {pending, pending, audio};
    else if (scenario == "private-timing") {
      timingHeader = "private-question;dur=123, stt;dur=10;desc=private-token, gemini;dur=-5";
      script = {audio};
    } else if (scenario == "lost-post") script = {{-1, 0, ""}, pending, audio};
    else if (scenario == "unknown-after-lost-post") script = {{-1, 0, ""}, {404, 8, "notfound"}, pending, audio};
    else if (scenario == "server-closes") {
      pending.closed = true; script = {pending, audio};
    } else if (scenario == "oversized-pending") {
      pending.length = 1000000; script = {pending, audio};
    } else if (scenario == "unknown-pending-length") {
      pending.length = -1; script = {pending, audio};
    } else if (scenario == "truncated-pending") {
      pending.length += 30; script = {pending, audio};
    } else if (scenario == "wrong-pending-type") {
      pending.type = "text/html"; script = {pending, audio};
    } else if (scenario == "chunked-pending") {
      pending.encoding = "chunked"; script = {pending, audio};
    } else if (scenario == "truncated-audio") {
      audio.length += 10; script = {audio}; expected = false;
    } else if (scenario == "four-transport-errors") {
      script = {{-1, 0, ""}, {-1, 0, ""}, {-1, 0, ""}, {-1, 0, ""}}; expected = false;
    } else throw std::runtime_error("Unknown scenario");
    bool result = requestReply();
    check(result == expected, "Unexpected requestReply result");
    check(nextReply == int(script.size()), "Did not consume scripted replies");
    check(std::find(openedFiles.begin(), openedFiles.end(), "/upload.bin") == openedFiles.end(), "Extra flash copy opened");
    if (expected) check(audioWritten == "ID3reply", "Downloaded MP3 changed");
    if (scenario == "pending") {
      check(connections == 1, "202 polling did not reuse one connection");
      check(consumedPending == 2, "202 responses were not fully consumed");
      for (const char *metric : {"stt_ms=10", "gemini_ms=20", "tts_ms=30"})
        check(Serial.output.find(metric) != std::string::npos, "Known backend duration missing from serial log");
    }
    if (scenario == "unknown-after-lost-post") {
      check(requestIds.size() == 2 && requestIds[0] == requestIds[1], "Retry changed logical request ID");
    }
    if (scenario == "lost-post") {
      check(requestIds.size() == 1 && methods[1] == "GET", "Lost POST must poll before resubmitting");
      check(socketStops >= 1 && connections >= 2, "Transport error did not discard its socket");
    }
    if (scenario == "oversized-pending" || scenario == "unknown-pending-length" || scenario == "truncated-pending" || scenario == "wrong-pending-type" || scenario == "chunked-pending") {
      check(socketStops >= 1 && connections >= 2, "Unusable pending body did not discard its socket");
    }
    if (scenario == "private-timing") check(Serial.output.find("private-") == std::string::npos, "Untrusted timing header leaked into serial log");
    if (scenario == "server-closes") check(connections == 2, "Server-closed connection did not reconnect");
    if (scenario == "four-transport-errors") check(socketStops >= 4, "Failed transports did not close sockets");
    return 0;
  } catch (const std::exception &e) { std::fprintf(stderr, "%s\n", e.what()); return 1; }
}
'''


@pytest.fixture(scope='module')
def transport(tmp_path_factory):
    compiler = shutil.which('c++')
    if not compiler:
        pytest.skip('Host C++ compiler unavailable; real ESP32 builds are separate')
    source = (ROOT / 'firmware/karen_ai/karen_ai.ino').read_text()
    # All HTTP-specific helpers are kept together immediately before the flow.
    begin = source.index('bool drainPendingReply(')
    end = source.index('bool playReply(', begin)
    network = source[begin:end]
    folder = tmp_path_factory.mktemp('firmware-transport')
    cpp, executable = folder / 'transport.cpp', folder / 'transport'
    cpp.write_text(HARNESS + '\n' + network + '\n' + RUNNER)
    built = subprocess.run([compiler, '-std=c++17', str(cpp), '-o', str(executable)],
                           capture_output=True, text=True)
    assert built.returncode == 0, built.stderr
    return executable


@pytest.mark.parametrize('scenario', [
    'pending', 'lost-post', 'unknown-after-lost-post', 'server-closes',
    'oversized-pending', 'unknown-pending-length', 'truncated-pending',
    'truncated-audio', 'four-transport-errors', 'private-timing',
    'wrong-pending-type', 'chunked-pending',
])
def test_firmware_transport_flow(transport, scenario):
    result = subprocess.run([str(transport), scenario], capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
