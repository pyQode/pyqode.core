# CMake script for building debian packages:
#
# To build a python3 package, run the following commands:
#   - cd /path/to/src
#   - mkdir build && build
#   - cmake -DCPACK_GENERATOR=DEB ..
#   - make package
#
# To build a python2 package, run the following commands:
#   - cd /path/to/src
#   - mkdir build && build
#   - cmake -DTARGET_PYTHON_3=OFF -DCPACK_GENERATOR=DEB ..
#   - make package
#
# To upload a PPA package, adapt DPUT_HOST to point to your ppa then run
# make dput
#
cmake_minimum_required( VERSION 2.8 )

# ##############################################################

set(PROJECT_NAME pyqode.core)
project(pyqode.core)
set(VERSION_MAJOR 1)
set(VERSION_MINOR 1)
set(VERSION_PATCH 0)
set(VERSION ${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH})
option(TARGET_PYTHON_3
       "ON to target Python >= 3, OFF to target Python 2.7" ON)

# Make the scripts available in the 'cmake' directory available for the
# 'include()' command, 'find_package()' command.

set( CMAKE_MODULE_PATH ${CMAKE_MODULE_PATH} ${CMAKE_CURRENT_LIST_DIR}/cmake )

# ##############################################################

if(${TARGET_PYTHON_3})
    set(DEPENDS "python3-pygments, python3-pyqt4")
    find_package(PythonInterp 3)
    set(CPACK_TARGET_INTERPRETER_VERSION "python3")
else()
    set(DEPENDS "python-pygments, python-qt4")
    find_package(PythonInterp 2.7)
    set(CPACK_TARGET_INTERPRETER_VERSION "python")
endif()

# ##############################################################
# get python interpreter and determine install path


execute_process ( COMMAND ${PYTHON_EXECUTABLE} -c "import site; print(site.getsitepackages()[1])"
                  OUTPUT_VARIABLE _ABS_PYTHON_MODULE_PATH
                  OUTPUT_STRIP_TRAILING_WHITESPACE )

get_filename_component ( _ABS_PYTHON_MODULE_PATH ${_ABS_PYTHON_MODULE_PATH} ABSOLUTE )
file(RELATIVE_PATH _REL_PYTHON_MODULE_PATH ${CMAKE_INSTALL_PREFIX} ${_ABS_PYTHON_MODULE_PATH} )
set(PYTHON_MODULE_PATH ${_REL_PYTHON_MODULE_PATH})

message(STATUS "Target interpreter: ${CPACK_TARGET_INTERPRETER_VERSION}")
message(STATUS "pyqode.core will be installed to ${CMAKE_INSTALL_PREFIX}/${PYTHON_MODULE_PATH}")

# ##############################################################

install(DIRECTORY pyqode DESTINATION ${PYTHON_MODULE_PATH})


# ##############################################################

if(CMAKE_CPACK_COMMAND AND UNIX)
    set(DPUT_HOST "ppa:pyqode/unstable" CACHE STRING "PPA repository to upload the debian sources")

    # Packing information
    set(CPACK_PACKAGE_NAME ${CPACK_TARGET_INTERPRETER_VERSION}-${PROJECT_NAME})

    # trick to put the copyright to /usr/share/doc/<package>/
    configure_file(
      "${PROJECT_SOURCE_DIR}/LICENSE.txt"
      "${PROJECT_BINARY_DIR}/copyright"
      )
    INSTALL(FILES "${PROJECT_BINARY_DIR}/copyright"
            DESTINATION share/doc/${CPACK_PACKAGE_NAME}/)

    set(CPACK_PACKAGE_CONTACT "Colin Duquesnoy <colin.duquesnoy@gmail.com>" CACHE STRING "Package maintainer and PGP signer.")
    set(CPACK_PACKAGE_VENDOR "https://github.com/ColinDuquesnoy/pyqode.core")
    set(CPACK_PACKAGE_DISPLAY_NAME "pyqode.core ${VERSION}")
    set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Code editor widget for PyQt/PySide")
    set(CPACK_PACKAGE_VERSION "${VERSION}")
    set(CPACK_PACKAGE_VERSION_MAJOR ${VERSION_MAJOR})
    set(CPACK_PACKAGE_VERSION_MINOR ${VERSION_MINOR})
    set(CPACK_PACKAGE_VERSION_PATCH ${VERSION_PATCH})
    set(CPACK_DEBIAN_CHANGELOG
        "  * See the homepage for a full change log:\n    https://github.com/ColinDuquesnoy/pyqode.core\n")
    set(DEB_LONG_DESCRIPTION
        " pyQode is a *flexible source code editor widget* for Python Qt\n"
        " applications. pyQode is a library/widget, not an IDE. You can\n"
        " view it as an alternative to QScintilla.\n"
        " .\n"
        " pyQode is a namespace package made up of the following official packages:\n"
        "   * pyqode.core\n"
        "   * pyqode.python\n"
        "   * pyqode.widgets\n"
        "   * pyqode.designer\n")
    string(REPLACE ";" "" DEB_LONG_DESCRIPTION ${DEB_LONG_DESCRIPTION})
    set(CPACK_DEBIAN_PACKAGE_DESCRIPTION
        "${CPACK_PACKAGE_DESCRIPTION_SUMMARY}\n${DEB_LONG_DESCRIPTION}")
    set(CPACK_RESOURCE_FILE_LICENSE ${CMAKE_CURRENT_SOURCE_DIR}/LICENSE.txt)
    set(CPACK_DEBIAN_CMAKE_OPTIONS "-DTARGET_PYTHON_3=${TARGET_PYTHON_3}")

    # base
    set(CPACK_DEBIAN_BUILD_DEPENDS_UBUNTU debhelper cmake ${CPACK_TARGET_INTERPRETER_VERSION})

    # get architecture
    set(CPACK_DEBIAN_PACKAGE_ARCHITECTURE "all")

    # debian
    set(CPACK_DEBIAN_PACKAGE_PRIORITY optional)
    set(CPACK_DEBIAN_PACKAGE_SECTION python)
    set(CPACK_DEBIAN_PACKAGE_DEPENDS ${DEPENDS})
    set(CPACK_DEBIAN_PACKAGE_SOURCE_COPY "${PYTHON_EXECUTABLE} /tools/copydebfiles.py")
    set(CPACK_DEBIAN_PACKAGE_REMOVE_SOURCE_FILES )
#     set(CPACK_DEBIAN_PACKAGE_SOURCE_COPY "${PYTHON_EXECUTABLE} /tools/copydebfiles.py")
#     FILE(READ "CHANGELOG" CPACK_DEBIAN_CHANGELOG)
    execute_process(COMMAND lsb_release -is
        OUTPUT_VARIABLE _lsb_distribution OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE _lsb_release_failed)
    if(${_lsb_distribution})
        set(CPACK_DEBIAN_DISTRIBUTION_NAME ${_lsb_distribution} CACHE STRING "Name of the distribution")
    else()
        # lsb_release fail when building the package in a ppa, as ubuntu is always the target release
        # on launchpad, we can safely set the distribution name to ubuntu
        set(CPACK_DEBIAN_DISTRIBUTION_NAME "ubuntu")
    endif()
    string(TOLOWER ${CPACK_DEBIAN_DISTRIBUTION_NAME} CPACK_DEBIAN_DISTRIBUTION_NAME)
    if( ${CPACK_DEBIAN_DISTRIBUTION_NAME} STREQUAL "ubuntu" )
        set(CPACK_DEBIAN_DISTRIBUTION_RELEASES precise quantal raring saucy CACHE STRING "Release code-names of the distrubiton release")
    endif()
    # The debian generator does not seem to use a correct name for the debian packages
    set(CPACK_PACKAGE_FILE_NAME "${CPACK_PACKAGE_NAME}_${VERSION_MAJOR}.${VERSION_MINOR}.${VERSION_PATCH}_${CPACK_DEBIAN_PACKAGE_ARCHITECTURE}")

    include(CPack)
    include(DebSourcePPA)
endif()