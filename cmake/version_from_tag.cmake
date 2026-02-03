include_guard(GLOBAL)

# cmake/version_from_tag.cmake
#
# Exports (API kept):
#   PRJ_VERSION             (numeric: 2.4.6)
#   PRJ_VERSION_FULL        (string:  v2.4.6-0-g<hash>-dirty OR v2.4.6-dirty OR <hash>-dirty)
#   PRJ_VERSION_IS_DIRTY    (0/1)   <-- dirty if distance>0 OR local changes
#   PRJ_VERSION_MAJOR/MINOR/PATCH
#   PRJ_VERSION_GIT_COMMIT  (short hash)
#
# Compatibility exports:
#   PROJECT_VERSION
#   PROJECT_VERSION_FULL

function(get_version_from_tag)
  find_package(Git QUIET)

  set(_fallback_version "0.0.0")
  set(_fallback_full    "0.0.0-unknown")
  set(_dirty_flag 0)
  set(_git_commit "unknown")
  set(_best_tag "")

  if(NOT Git_FOUND)
    message(WARNING "Git not found; using fallback version ${_fallback_version}")
    set(PRJ_VERSION "${_fallback_version}" PARENT_SCOPE)
    set(PRJ_VERSION_FULL "${_fallback_full}" PARENT_SCOPE)
    set(PRJ_VERSION_IS_DIRTY 0 PARENT_SCOPE)
    set(PRJ_VERSION_MAJOR 0 PARENT_SCOPE)
    set(PRJ_VERSION_MINOR 0 PARENT_SCOPE)
    set(PRJ_VERSION_PATCH 0 PARENT_SCOPE)
    set(PRJ_VERSION_GIT_COMMIT "${_git_commit}" PARENT_SCOPE)
    set(PROJECT_VERSION "${_fallback_version}" PARENT_SCOPE)
    set(PROJECT_VERSION_FULL "${_fallback_full}" PARENT_SCOPE)
    return()
  endif()

  # 1) Get tags reachable from HEAD
  execute_process(
    COMMAND "${GIT_EXECUTABLE}" tag --merged HEAD
    WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
    OUTPUT_VARIABLE _tags
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
  )

  if(NOT _tags STREQUAL "")
    string(REPLACE "\n" ";" _tag_list "${_tags}")
    list(SORT _tag_list COMPARE NATURAL ORDER DESCENDING)
    list(GET _tag_list 0 _best_tag)
  endif()

  # 2) git describe (keep hash + distance; local changes add -dirty)
  if(NOT _best_tag STREQUAL "")
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" describe --tags --dirty --long --always --match "${_best_tag}"
      WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
      OUTPUT_VARIABLE _git_describe
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_VARIABLE _git_err
      RESULT_VARIABLE _rc
    )
  else()
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" describe --tags --dirty --long --always
      WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
      OUTPUT_VARIABLE _git_describe
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_VARIABLE _git_err
      RESULT_VARIABLE _rc
    )
  endif()

  if(NOT _rc EQUAL 0 OR _git_describe STREQUAL "")
    message(WARNING "Git describe failed: ${_git_err}. Using fallback.")
    set(_git_describe "${_fallback_full}")
  endif()

  # 2a) Dirty semantics:
  #     - local changes => git describe ends with -dirty
  #     - not exactly on tag commit => distance in "<tag>-<N>-g<hash>" is N>0
  set(_worktree_dirty 0)
  set(_ahead_of_tag 0)
  set(_distance 0)

  if(_git_describe MATCHES "-dirty$")
    set(_worktree_dirty 1)
  endif()

  if(_git_describe MATCHES "-([0-9]+)-g[0-9a-fA-F]+")
    set(_distance "${CMAKE_MATCH_1}")
    if(NOT _distance STREQUAL "0")
      set(_ahead_of_tag 1)
    endif()
  endif()

  if(_worktree_dirty OR _ahead_of_tag)
    set(_dirty_flag 1)
  else()
    set(_dirty_flag 0)
  endif()

  # Ensure PRJ_VERSION_FULL carries -dirty if OUR dirty flag is set
  if(_dirty_flag AND NOT _git_describe MATCHES "-dirty$")
    set(_git_describe "${_git_describe}-dirty")
  endif()

  # 2b) Commit hash
  if(_git_describe MATCHES "-g([0-9a-fA-F]+)")
    set(_git_commit "${CMAKE_MATCH_1}")
  else()
    execute_process(
      COMMAND "${GIT_EXECUTABLE}" rev-parse --short HEAD
      WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
      OUTPUT_VARIABLE _git_commit
      OUTPUT_STRIP_TRAILING_WHITESPACE
      ERROR_QUIET
    )
    if(_git_commit STREQUAL "")
      set(_git_commit "unknown")
    endif()
  endif()

  # 3) Numeric version from tag (vX.Y.Z) or fallback
  set(_maj 0)
  set(_min 0)
  set(_pat 0)
  set(_numeric "${_fallback_version}")

  if(NOT _best_tag STREQUAL "")
    string(REGEX REPLACE "^[vV]" "" _tag_stripped "${_best_tag}")
    if(_tag_stripped MATCHES "^([0-9]+)\\.([0-9]+)\\.([0-9]+)$")
      set(_maj "${CMAKE_MATCH_1}")
      set(_min "${CMAKE_MATCH_2}")
      set(_pat "${CMAKE_MATCH_3}")
      set(_numeric "${_maj}.${_min}.${_pat}")
    else()
      message(WARNING "Tag '${_best_tag}' is not vX.Y.Z. Using fallback ${_fallback_version}")
    endif()
  endif()

  # 4) Export (keep your API)
  set(PRJ_VERSION             "${_numeric}"      PARENT_SCOPE)
  set(PRJ_VERSION_FULL        "${_git_describe}" PARENT_SCOPE)
  set(PRJ_VERSION_IS_DIRTY    "${_dirty_flag}"   PARENT_SCOPE)
  set(PRJ_VERSION_MAJOR       "${_maj}"          PARENT_SCOPE)
  set(PRJ_VERSION_MINOR       "${_min}"          PARENT_SCOPE)
  set(PRJ_VERSION_PATCH       "${_pat}"          PARENT_SCOPE)
  set(PRJ_VERSION_GIT_COMMIT  "${_git_commit}"   PARENT_SCOPE)

  set(PROJECT_VERSION         "${_numeric}"      PARENT_SCOPE)
  set(PROJECT_VERSION_FULL    "${_git_describe}" PARENT_SCOPE)

  # 5) Messages (useful, not spammy)
  message(STATUS "Version:  ${_numeric} (tag: ${_best_tag})")
  message(STATUS "Describe: ${_git_describe}")
  message(STATUS "Commit:   ${_git_commit}  Dirty: ${_dirty_flag} (distance: ${_distance})")
endfunction()
