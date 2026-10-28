#pragma once
#define WIFI_SSID "YOUR_2_4_GHZ_HOTSPOT"
#define WIFI_PASSWORD "YOUR_HOTSPOT_PASSWORD"
// Exact origin, no trailing slash. HTTP only for a trusted local network.
#define SERVER_ORIGIN "http://192.168.1.100:8080"
// For HTTPS, replace with the PEM root CA that validates your deployment host.
// Obtain from your host/certificate issuer; do not paste the leaf certificate.
static const char ROOT_CA[] = R"PEM(
)PEM";
#define MIC_BCLK 26
#define MIC_WS 25
#define MIC_DATA 33
#define AMP_BCLK 27
#define AMP_WS 14
#define AMP_DATA 22
#define BUTTON_PIN 32
#define STATUS_LED 2
#define RECORD_SECONDS 5
// INMP441 24-bit signed samples arrive left-aligned in 32-bit words.
// 16 is unity conversion to 16-bit; reduce toward 14 if too quiet (may clip).
#define MIC_SHIFT 16
