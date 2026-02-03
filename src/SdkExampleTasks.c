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

static void Sdk_ToggleLed()
{
    static bool ledOn = false;
    if (!ledOn)
    {
        Sdk_SetLed((S_Sdk_LedRgbColor_t){ 0, 0, 120 });
    }
    else
    {
        Sdk_SetLed((S_Sdk_LedRgbColor_t){ 0, 0, 0 });
    }
    ledOn = !ledOn;
}

static void Sdk_Task1(void* pvParameters)
{
    (void)(pvParameters);
    Sdk_TaskReady();
    LOG_DEBUG("SDK TASK1 ready to run ");
    while (true)
    {
        Sdk_TaskSleep(950);
        Sdk_ToggleLed();
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
