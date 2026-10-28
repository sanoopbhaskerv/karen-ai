#pragma once
// Classic ESP32 Dev Module / 38-pin WROOM board.
namespace KarenController {
constexpr const char* name = "esp32";
constexpr int micBclk = 26, micWs = 25, micData = 33;
constexpr int ampBclk = 27, ampWs = 14, ampData = 22;
constexpr int button = 32;
constexpr bool availablePin(int pin) { return GPIO_IS_VALID_GPIO(pin) && !(pin >= 6 && pin <= 11); }
}
