/**
 * @file SdkTasks.c
 * @brief SDK user tasks functions
 * This file contains examples of user tasks functions which can be used for implementing
 * your specific functionality
 * @copyright Copyright (c) 2026
 *
 */

#include "Sdk.h"

static void Sdk_Task1(void* pvParameters);
static void Sdk_Task2(void* pvParameters);
static void Sdk_ToggleLed();

const S_Sdk_TaskInstanceCfg_t SdkTasksCfg[] = {
    { .pTaskName = "SDK_TASK1", .Runner = Sdk_Task1, .StackDepth = 1024, .Priority = 1, .StartupPrio = 0 },
    { .pTaskName = "SDK_TASK2", .Runner = Sdk_Task2, .StackDepth = 1024, .Priority = 1, .StartupPrio = 0 },
};

S_Sdk_TasksCfg_t Sdk_GetTasksConfiguration(void)
{
    return (S_Sdk_TasksCfg_t){ SdkTasksCfg, sizeof(SdkTasksCfg) / sizeof(SdkTasksCfg[0]) };
}

static void Sdk_PulseLed()
{
    static int16_t illumination = 0;
    static int16_t delta        = 12;

    Sdk_SetLed((S_Sdk_LedRgbColor_t){ illumination, illumination, illumination });

    illumination += delta;
    if (illumination > 0xFF)
    {
        illumination = 0xFF;
        delta        = -delta;
    }
    if (illumination < 0)
    {
        illumination = 0;
        delta        = -delta;
    }
}

static void Sdk_Task1(void* pvParameters)
{
    (void)(pvParameters);
    Sdk_TaskReady();
    LOG_DEBUG("SDK TASK1 ready to run ");
    while (true)
    {
        Sdk_TaskSleep(50);
        Sdk_PulseLed();
        Sdk_TaskAlive();
    }
}

static void Sdk_Task2(void* pvParameters)
{
    (void)(pvParameters);
    Sdk_TaskReady();
    while (true)
    {
        Sdk_TaskSleep(950);
        LOG_DEBUG("%s task running", pcTaskGetName(NULL));
        Sdk_TaskAlive();
    }
}
