cmake_minimum_required(VERSION 3.8)
project(my_robot)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(urdf REQUIRED)

install(DIRECTORY
  launch
  urdf
  meshes
  config
  worlds
  DESTINATION share/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/arm_teleop.py
  scripts/base_teleop.py
  scripts/imu_visualizer.py
  scripts/omni_controller.py
  scripts/scan_visualizer.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
