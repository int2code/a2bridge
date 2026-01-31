include_guard(GLOBAL)


function(fetch_a2bridge_core build_type version is_ver_dirty ) 
  
set(_git_hub_repo "https://github.com/int2code/a2bridge/releases/download/v")
  if(${is_ver_dirty})
    set(_asset "a2bridge_core-${build_type}-${version}-dev.tar.gz")
    set(_url   "${_git_hub_repo}${version}-dev/${_asset}")
  else()
    set(_asset "a2bridge_core-${build_type}-${version}.tar.gz")
    set(_url   "${_git_hub_repo}${version}/${_asset}")
  endif()
  
  

  set(_deps_root    "${CMAKE_BINARY_DIR}/_deps/a2bridge_core/${version}/${build_type}")
  set(_zip_path     "${_deps_root}/${_asset}")
  set(_extract_root "${_deps_root}/extract")

  # tar extracts into /a2bridge_core/...
  set(_cfg_dir "${_extract_root}/a2bridge_core/lib/cmake/a2bridge_core")
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

  file(ARCHIVE_EXTRACT
     INPUT ${_zip_path}
     DESTINATION ${_extract_root}
  )

  if (NOT EXISTS "${_cfg_file}")
    message(FATAL_ERROR
      "a2bridge_core package layout unexpected.\n"
      "Expected: ${_cfg_file}\n"
      "Your zip should contain: a2bridge_core/lib/cmake/a2bridge_core/..."
    )
  endif()

  set(a2bridge_core_DIR "${_cfg_dir}" CACHE PATH "a2bridge_core package dir" FORCE)
  message(STATUS "a2bridge_core_DIR=${a2bridge_core_DIR}")

endfunction()