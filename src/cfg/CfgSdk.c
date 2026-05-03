/**
 *
 * @file CfgSdk.c
 *
 * @brief Library handling SDK configuration
 *
 */

#include "CfgSdk.h"
#include "Config.h"

/**
 * @brief Parsed SDK configuration exposed by this module.
 */
static S_Sdk_Config_t Sdk_Config;
/**
 * @brief Entry point for parsing the SDK configuration block.
 *
 * @param pInst Pointer to the lwjson parser instance.
 *
 * @return true if the section was parsed successfully, false otherwise.
 */
bool ParseJson(lwjson_t* pInst);

/**
 * @brief SDK JSON parser hook used by the Config module.
 *
 * @details
 * This global function pointer is used as an extension mechanism to plug in
 * a custom SDK-specific JSON parsing routine.
 *
 * The core Config module calls this function (if defined) to allow the
 * application or feature-specific module to parse its own configuration
 * section.
 *
 * By assigning this symbol to a concrete implementation (e.g. ParseJson),
 * the module registers its parser without requiring direct dependencies
 * or explicit function calls.
 *
 * This is the expected mechanism for integrating custom configuration
 * parsing logic into the generic Config framework.
 */
ParseSdkJson parseSdkJson = ParseJson;

/**
 * @brief JSON keyword for SDK configuration.
 *
 * @details
 * The keyword shall be used by the Config module together with
 * @ref parseSdkJson to process the corresponding configuration data.
 */
const char* configSdkKeyword = "SdkConfig";

/**
 * @brief Parses the top-level SDK JSON.
 *
 * @param pInst Pointer to the lwjson parser instance.
 * @param config Pointer to the output structure where parsed SDK configurations are stored.
 *
 * @return true if the SDK section was parsed successfully, false otherwise.
 */
bool ParseConfigJson(lwjson_t* pInst, S_Sdk_Config_t* config);

bool ParseJson(lwjson_t* pInst)
{
    return ParseConfigJson(pInst, &Sdk_Config);
}

bool ParseConfigJson(lwjson_t* pInst, S_Sdk_Config_t* config)
{
    const lwjson_token_t* pManagersToken = lwjson_find(pInst, configSdkKeyword);
    if (pManagersToken == NULL)
    {
        // Returning true here means the SdkConfig is optional and can be skipped. If you want force the SdkConfig being
        // present, return false here.
        return true;
    }

    const lwjson_token_t* pToken = lwjson_find_ex(pInst, pManagersToken, "Name");
    if ((pToken != NULL) && (LWJSON_TYPE_STRING == pToken->type))
    {
        const uint32_t nameLen = (pToken->u.str.token_value_len < sizeof(config->Name) - 1U)
                                     ? (pToken->u.str.token_value_len)
                                     : (sizeof(config->Name) - 1U);
        memcpy(config->Name, pToken->u.str.token_value, nameLen);
        config->Name[nameLen] = '\0';
    }
    else
    {
        Config_AddConfigLog("SDK error Name: Invalid or missing");
        return false;
    }

    pToken = lwjson_find_ex(pInst, pManagersToken, "Address");
    if ((pToken == NULL) || (LWJSON_TYPE_NUM_INT != pToken->type))
    {
        Config_AddConfigLog("SDK error Address: Invalid or missing");
        return false;
    }
    config->Address = (uint8_t)pToken->u.num_int;

    // implement what you need

    return true;
}

const S_Sdk_Config_t* CfgSdk_GetSdkConfig(void)
{
    return &Sdk_Config;
}