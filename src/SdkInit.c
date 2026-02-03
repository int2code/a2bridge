/**
 * @file SdkInit.c
 * @brief SDK specific system initialization
 *
 *
 */

#include <Log.h>
#include "Sdk.h"

void Sdk_Init(E_Sdk_Status_t sdkStatus)
{
    if (sdkStatus != SDK_STATUS_OK)
    {
        // the SDK tasks configuration was not ok.
        LOG_ERROR("Wrong SDK tasks configuration, error: %d", sdkStatus);
        LOG_ERROR("NO SDK task will be started. Revise your tasks configuration");
        return;
    }
    // put here your project specific initialization code
}
