#pragma once
#define WIFI_SSID "YOUR_2_4_GHZ_HOTSPOT"
#define WIFI_PASSWORD "YOUR_HOTSPOT_PASSWORD"
// Exact origin, no trailing slash. HTTP only for a trusted local network.
#define SERVER_ORIGIN "http://192.168.1.100:8080"
// For HTTPS, replace with the PEM root CA that validates your deployment host.
// Obtain from your host/certificate issuer; do not paste the leaf certificate.
static const char ROOT_CA[] = R"PEM(
)PEM";
// GPIO defaults come from the controller adapter selected by the build target.
// Do not copy the classic ESP32 pin numbers to ESP32-S3; see docs/HARDWARE.md.
// Optional external/plain LED only; the S3 onboard RGB LED needs a different driver.
// On the classic ESP32 only, use 2 after confirming a suitable GPIO2 LED exists.
#define STATUS_LED -1
#define RECORD_SECONDS 5
// INMP441 24-bit signed samples arrive left-aligned in 32-bit words.
// 16 is unity conversion to 16-bit; reduce toward 14 if too quiet (may clip).
#define MIC_SHIFT 16
