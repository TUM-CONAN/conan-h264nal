cmake_minimum_required(VERSION 3.8)

project(test_package CXX)

find_package(h264nal REQUIRED CONFIG)

add_executable(${PROJECT_NAME} test_package.cpp)
target_link_libraries(${PROJECT_NAME} PRIVATE h264nal::h264nal)
