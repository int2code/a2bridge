# cmake/version_from_tag.cmake
# Exports:
#   PROJECT_VERSION        (numeric: 2.4.4)
#   PROJECT_VERSION_FULL   (string: v2.4.4-8-g<hash>-dirty)
#   PROJECT_VERSION_MAJOR/MINOR/PATCH (numbers)

function(get_version_from_tag)
    find_package(Git QUIET)

    # -------- Fallbacks (used if git is unavailable or no tags) ----------
    set(_fallback_version "0.0.0")
    set(_git_commit "unknown")
    set(_fallback_full    "0.0.0-${_git_commit}")
    set(_dirty_flag 1)
    

    if(NOT Git_FOUND)
        message(WARNING "Git not found; using fallback version ${_fallback_version}")
        set(PROJECT_VERSION      "${_fallback_version}" PARENT_SCOPE)
        set(PROJECT_VERSION_FULL "${_fallback_full}"    PARENT_SCOPE)
        return()
    endif()

    # -------- Get full describe 
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" describe --tags --dirty --always
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_describe
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _desc_rc
    )
    if(NOT _desc_rc EQUAL 0 OR _git_describe STREQUAL "")
        set(_git_describe "${_fallback_full}")
    endif()
    message("Git tag: " ${_git_describe})

    if (NOT _git_describe MATCHES "dirty")
        set(_dirty_flag 0)
    endif()

    if(_git_describe MATCHES "-g([0-9a-fA-F]+)")
        set(_git_commit "${CMAKE_MATCH_1}")
        set(PRJ_VERSION_GIT_COMMIT ${_git_commit} PARENT_SCOPE)
    endif()

    # -------- Get latest tag name 
    # Prefer "git describe --tags --abbrev=0" (requires tags present).
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" describe --tags --abbrev=0
        WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        OUTPUT_VARIABLE _git_tag
        OUTPUT_STRIP_TRAILING_WHITESPACE
        ERROR_QUIET
        RESULT_VARIABLE _tag_rc
    )

    if(NOT _tag_rc EQUAL 0 OR _git_tag STREQUAL "")
        # No tags (or shallow clone without tags) -> numeric fallback
        set(_numeric "${_fallback_version}")
    else()
        # Strip common prefixes like v or V
        string(REGEX REPLACE "^[vV]" "" _tag_stripped "${_git_tag}")
        
        # Validate and extract numeric x.y.z (or x.y or x)
        # Accept tags like: 2.4.4, 2.4, 2
        if(${_tag_stripped} MATCHES "^([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?(\\.[0-9]+)?$")
            set(_numeric "${_tag_stripped}")
        else()
            message(WARNING "Git tag '${_git_tag}' is not a numeric version tag (expected vX.Y.Z). Using fallback ${_fallback_version}")
            set(_numeric "${_fallback_version}")
        endif()
    endif()

    
    # Normalize to MAJOR.MINOR.PATCH (CMake accepts shorter, but this makes it consistent)
    # Fill missing parts with 0.
    set(_maj 0) 
    set(_min 0) 
    set(_pat 0)

    if(${_numeric} MATCHES "^([0-9]+)(\\.[0-9]+)?(\\.[0-9]+)?$")
        set(_maj "${CMAKE_MATCH_1}")
        if(CMAKE_MATCH_2)
            string(SUBSTRING "${CMAKE_MATCH_2}" 1 -1 _min)  # drop leading dot
        endif()
        if(CMAKE_MATCH_3)
            string(SUBSTRING "${CMAKE_MATCH_3}" 1 -1 _pat)  # drop leading dot
        endif()
    endif()
    set(_numeric_norm "${_maj}.${_min}.${_pat}")

    # Export to parent
    set(PRJ_VERSION             "${_numeric_norm}"  PARENT_SCOPE)
    set(PRJ_VERSION_FULL        "${_git_describe}"  PARENT_SCOPE)
    set(PRJ_VERSION_IS_DIRTY    "${_dirty_flag}"    PARENT_SCOPE)
    
    set(PRJ_VERSION_MAJOR       "${_maj}"           PARENT_SCOPE)
    set(PRJ_VERSION_MINOR       "${_min}"           PARENT_SCOPE)
    set(PRJ_VERSION_PATCH       "${_pat}"           PARENT_SCOPE)
    message("Project version: " ${_numeric_norm})
    message("Version dirty:   " ${_dirty_flag})
    message("Git commit:      " ${_git_commit})
endfunction()