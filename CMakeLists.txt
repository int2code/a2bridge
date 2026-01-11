cmake_minimum_required(VERSION 3.15.3)

if (NOT DEFINED A2BRIDGE_CORE_SOURCE_DIR)
# this will be performed only if the SDK is used outside int2code 

# Include cmake tools from SDK 
list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/sdk/cmake")
include(gcc-arm-none-eabi)
include(version_from_tag)

# get the version from the git TAG
get_version_from_tag()

endif()

project(a2bridge)

enable_language(C ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# overwrite this locally if you want to test newer core version 
set(A2BRIDGE_CORE_VERSION ${PRJ_VERSION})

set(TARGET_CM7 ${PROJECT_NAME}_${CMAKE_BUILD_TYPE}_cm7)
# do not remove parent scope, we needed for internal core development @int2code 
set(TARGET_CM7 ${TARGET_CM7} PARENT_SCOPE)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_SOURCE_DIR}/artifacts)




set(USB_VID 0x0483)
set(USB_PID 0xA519)





if (DEFINED A2BRIDGE_CORE_SOURCE_DIR)
  # internal: core from source
  add_subdirectory(${A2BRIDGE_CORE_SOURCE_DIR} a2bridge_core_build)
else()
  # public: core from binary package
  include(cmake/deps/A2BridgeCoreFetch.cmake)
  find_package(a2bridge_core ${A2BRIDGE_CORE_VERSION} REQUIRED)
endif()



add_executable(${TARGET_CM7})

target_link_options(${TARGET_CM7} PRIVATE
  "-Wl,--whole-archive"
)
target_link_libraries(${TARGET_CM7} PRIVATE a2bridge_core)

target_link_options(${TARGET_CM7} PRIVATE
  "-Wl,--no-whole-archive"
)

target_sources(${TARGET_CM7} PUBLIC
        src/main.c    
        src/startup/system_stm32h7xx_dualcore_boot_cm4_cm7.c
        src/startup/startup_stm32h745xihx.s
        src/startup/stm32h7xx_it.c
)


target_compile_options(${TARGET_CM7} PRIVATE
        -mfloat-abi=hard
        -mcpu=cortex-m7
        -mfpu=fpv5-d16
        -Wall
        -Wextra
        #-Wpedantic
        -fdata-sections
        -ffunction-sections
        -Wno-unused-function
        $<$<CONFIG:debug>:-O0>
        $<$<CONFIG:release>:-Os>
        $<$<CONFIG:RelWithDebInfo>:-Os -g>
        )


target_compile_definitions(${TARGET_CM7} PRIVATE
        -DUSE_HAL_DRIVER
        -DSTM32H745xx
        -DCORE_CM7
        -DCFG_TUSB_MCU=OPT_MCU_STM32H7
        -DLWJSON_IGNORE_USER_OPTS
        -DLOG_ENABLED
        $<$<CONFIG:release>:NDEBUG>
        $<$<CONFIG:RelWithDebInfo>:NDEBUG>
        $<$<CONFIG:debug>:DEBUG>
        )


target_link_options(${TARGET_CM7} PRIVATE
        -T${CMAKE_CURRENT_SOURCE_DIR}/STM32H747XIHX_FLASH.ld
        -specs=nano.specs
        -Wl,-Map=${TARGET_CM7}.map
        -Wl,--gc-sections
        -Wl,--print-memory-usage
        -Wl,--start-group -lc -lm -Wl,--end-group
        -mfloat-abi=hard
        -mcpu=cortex-m7
        -mfpu=fpv5-d16
        )


if (NOT DEFINED GIT_TAG_HASH)
find_package(Git)
execute_process(
    COMMAND git describe --always --dirty --tags
    WORKING_DIRECTORY ${CMAKE_CURRENT_SOURCE_DIR}
    OUTPUT_VARIABLE GIT_TAG_HASH
    OUTPUT_STRIP_TRAILING_WHITESPACE)

add_definitions("-DVERSION_GIT_DESCRIPTION=\"${GIT_TAG_HASH}\"")
endif()

set(TOOLS_DIR ${CMAKE_CURRENT_SOURCE_DIR}/tools)

add_custom_command(TARGET ${TARGET_CM7}
        POST_BUILD
        WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMAND arm-none-eabi-objcopy -O ihex ${TARGET_CM7}.elf ${TARGET_CM7}.hex
        COMMAND arm-none-eabi-objcopy -O binary ${TARGET_CM7}.elf ${TARGET_CM7}.bin)

# Create DFU image(int2code prefix + standard DFU suffix)
add_custom_command(TARGET ${TARGET_CM7}
        POST_BUILD
        WORKING_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
        COMMAND python3 ${TOOLS_DIR}/dfu/dfu_prefix.py --i ${TARGET_CM7}.bin
        COMMAND dfu-suffix --pid ${USB_PID} --vid ${USB_VID} --a ${TARGET_CM7}.bin.dfu)

