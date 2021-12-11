!!!set(PROJECT_NAME {{project_name}})
!!!include_directories({{include_dirs}})
!!!add_compile_definitions({{compile_definitions}})
!!?subdirectories!add_subdirectory({{it}})

cmake_minimum_required(VERSION 3.16)
project(${PROJECT_NAME})
set(PROJECT_VERSION 0.0.1)
set(CMAKE_BUILD_PARALLEL_LEVEL 8)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_GENERATOR_PLATFORM x64)

message(STATUS "${PROJECT_NAME} ${PROJECT_VERSION}")

set(Boost_USE_STATIC_LIBS ON)
set(Boost_USE_STATIC_RUNTIME OFF)
set(Boost_NO_WARN_NEW_VERSIONS ON)

find_package(Boost 1.66.0 COMPONENTS unit_test_framework filesystem)
if (Boost_FOUND)
    message(STATUS "Boost_INCLUDE_DIRS: ${Boost_INCLUDE_DIRS}")
    message(STATUS "Boost_LIBRARIES: ${Boost_LIBRARIES} ${Boost_LIBRARY_DIRS}")
    message(STATUS "Boost_VERSION: ${Boost_VERSION}!")
    include_directories(${Boost_INCLUDE_DIRS})
else ()
    message(FATAL_ERROR "Boost not found...")
endif ()

set(SOURCE_FILES src/gdlibrary.cpp src/HUD.cpp)
set(TEST_FILES test/main.cpp test/TestGame.cpp)
include_directories(godot-cpp godot-cpp/godot-headers godot-cpp/include godot-cpp/include/core godot-cpp/include/gen)
link_directories(godot-cpp/bin)
set(GODOT_LIB_PLATFORM linux) # or "osx"
if (WIN32)
    set(GODOT_LIB_PLATFORM windows)
endif ()
set(GODOT_LIB_TARGET debug)
set(GODOT_LIB_BITS 64)

add_library(gdn SHARED ${SOURCE_FILES})
add_executable(test ${SOURCE_FILES} ${TEST_FILES})
set(ARMONIUM_DEPS holib)
!!!add_dependencies(gdn {{dependencies}})
!!!add_dependencies(test {{dependencies}})

set_target_properties(gdn test PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/godot/bin"
        ARCHIVE_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/godot/bin"
        RUNTIME_OUTPUT_DIRECTORY "${PROJECT_SOURCE_DIR}/godot/bin"
        )

set(GODOT_LIB "${PROJECT_SOURCE_DIR}/godot-cpp/bin/libgodot-cpp.${GODOT_LIB_PLATFORM}.${GODOT_LIB_TARGET}.${GODOT_LIB_BITS}.lib")

!!?libraries!set(LINK_LIBS ${LINK_LIBS} "${PROJECT_SOURCE_DIR}/{{it}}")
target_link_libraries(gdn ${LINK_LIBS})
target_link_libraries(test ${LINK_LIBS})

if (UNIX)
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -Wall -Werror -Wno-missing-braces")
endif ()