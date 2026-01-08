include_guard(GLOBAL)

set(A2BRIDGE_RELEASE_TAG  "v0.0.1-dev" CACHE STRING "GitHub release tag (e.g. v0.0.1-dev)")
set(A2BRIDGE_CORE_FLAVOR  "release"    CACHE STRING "Core flavor: release|debug")

set(_asset "a2bridge_core-${A2BRIDGE_CORE_FLAVOR}-${A2BRIDGE_RELEASE_TAG}.zip")
set(_url   "https://github.com/int2code/a2bridge/releases/download/${A2BRIDGE_RELEASE_TAG}/${_asset}")

set(_deps_root    "${CMAKE_BINARY_DIR}/_deps/a2bridge_core/${A2BRIDGE_RELEASE_TAG}/${A2BRIDGE_CORE_FLAVOR}")
set(_zip_path     "${_deps_root}/${_asset}")
set(_extract_root "${_deps_root}/extract")

# zip extracts into artifacts/a2bridge_core/...
set(_cfg_dir "${_extract_root}/artifacts/a2bridge_core/lib/cmake/a2bridge_core")
set(_cfg_file "${_cfg_dir}/a2bridge_coreConfig.cmake")

file(MAKE_DIRECTORY "${_deps_root}")

# Reuse if already extracted
if (EXISTS "${_cfg_file}")
  set(a2bridge_core_DIR "${_cfg_dir}" CACHE PATH "a2bridge_core package dir" FORCE)
  message(STATUS "Using cached a2bridge_core: ${a2bridge_core_DIR}")
  return()
endif()

message(STATUS "Downloading a2bridge_core from: ${_url}")

file(DOWNLOAD
  "${_url}" "${_zip_path}"
  SHOW_PROGRESS
  TLS_VERIFY ON
  STATUS _st
)

list(GET _st 0 _code)
list(GET _st 1 _msg)
if (NOT _code EQUAL 0)
  message(FATAL_ERROR "Failed to download ${_asset}: ${_msg}")
endif()

# Fresh extract
file(REMOVE_RECURSE "${_extract_root}")
file(MAKE_DIRECTORY "${_extract_root}")

execute_process(
  COMMAND "${CMAKE_COMMAND}" -E tar xf "${_zip_path}"
  WORKING_DIRECTORY "${_extract_root}"
  RESULT_VARIABLE _rc
)
if (NOT _rc EQUAL 0)
  message(FATAL_ERROR "Failed to extract ${_zip_path}")
endif()

if (NOT EXISTS "${_cfg_file}")
  message(FATAL_ERROR
    "a2bridge_core package layout unexpected.\n"
    "Expected: ${_cfg_file}\n"
    "Your zip should contain: artifacts/a2bridge_core/lib/cmake/a2bridge_core/..."
  )
endif()

set(a2bridge_core_DIR "${_cfg_dir}" CACHE PATH "a2bridge_core package dir" FORCE)
message(STATUS "a2bridge_core_DIR=${a2bridge_core_DIR}")
