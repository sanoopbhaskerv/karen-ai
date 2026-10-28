#pragma once
#include <driver/gpio.h>

// The build tool selects the chip from KAREN_CONTROLLER. Arduino IDE selects
// the same adapter through its board target. Unsupported chips fail closed.
#if defined(CONFIG_IDF_TARGET_ESP32S3)
#include "controllers/esp32_s3.h"
#elif defined(CONFIG_IDF_TARGET_ESP32)
#include "controllers/esp32.h"
#else
#error "Karen supports classic ESP32 and ESP32-S3 only. Select the correct board."
#endif

// Existing classic config.h pin overrides remain supported. Old classic pins
// used with an S3 target are rejected below instead of silently using PSRAM pins.
#ifndef MIC_BCLK
#define MIC_BCLK KarenController::micBclk
#endif
#ifndef MIC_WS
#define MIC_WS KarenController::micWs
#endif
#ifndef MIC_DATA
#define MIC_DATA KarenController::micData
#endif
#ifndef AMP_BCLK
#define AMP_BCLK KarenController::ampBclk
#endif
#ifndef AMP_WS
#define AMP_WS KarenController::ampWs
#endif
#ifndef AMP_DATA
#define AMP_DATA KarenController::ampData
#endif
#ifndef BUTTON_PIN
#define BUTTON_PIN KarenController::button
#endif
#ifndef STATUS_LED
#define STATUS_LED -1
#endif

namespace KarenController {
constexpr int signals[] = {MIC_BCLK, MIC_WS, MIC_DATA, AMP_BCLK, AMP_WS, AMP_DATA, BUTTON_PIN, STATUS_LED};
constexpr bool validPins() {
  for (int i = 0; i < 8; ++i) {
    if (i == 7 && signals[i] == -1) continue;
    if (!availablePin(signals[i])) return false;
    for (int j = 0; j < i; ++j) if (signals[i] == signals[j]) return false;
  }
  return GPIO_IS_VALID_OUTPUT_GPIO(MIC_BCLK) && GPIO_IS_VALID_OUTPUT_GPIO(MIC_WS) &&
    GPIO_IS_VALID_OUTPUT_GPIO(AMP_BCLK) && GPIO_IS_VALID_OUTPUT_GPIO(AMP_WS) &&
    GPIO_IS_VALID_OUTPUT_GPIO(AMP_DATA) && GPIO_IS_VALID_OUTPUT_GPIO(BUTTON_PIN) &&
    (STATUS_LED == -1 || GPIO_IS_VALID_OUTPUT_GPIO(STATUS_LED));
}
static_assert(validPins(), "Invalid, reserved or overlapping Karen pins. Remove old pin overrides from config.h to use the selected controller defaults.");
}
