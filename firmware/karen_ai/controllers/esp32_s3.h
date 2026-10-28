#pragma once
// HW678-style ESP32-S3 N16R8 board, using pins visible in the supplied photos.
namespace KarenController {
constexpr const char* name = "esp32_s3";
constexpr int micBclk = 4, micWs = 5, micData = 6;
constexpr int ampBclk = 16, ampWs = 17, ampData = 18;
constexpr int button = 7;
// Exclude flash/PSRAM, USB, UART, strapping pins and possible onboard RGB pins.
constexpr bool availablePin(int pin) {
  return GPIO_IS_VALID_GPIO(pin) &&
    ((pin >= 1 && pin <= 18 && pin != 3) || pin == 21 ||
     (pin >= 39 && pin <= 42) || pin == 47);
}
}
