/**
 *
 * @file CfgSdk.h
 *
 * @brief Library handling SDK configuration
 *
 */

#pragma once

#include "stdbool.h"
#include "stdint.h"

#define NAME_MAX_LEN 16

/**
 * @brief SDK Config example.
 */
typedef struct
{
    char    Name[NAME_MAX_LEN];
    uint8_t Address;

} S_Sdk_Config_t;
/**
 * @brief Returns parsed SDK configuration list.
 *
 * @return pointer to parsed SDK configuration list
 */
const S_Sdk_Config_t* CfgSdk_GetSdkConfig(void);