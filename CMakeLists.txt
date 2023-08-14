cmake_minimum_required(VERSION 3.12)

include(pico_sdk_import.cmake)

project(readtemp)

pico_sdk_init()

add_executable(readtemp
        readtemp.c
        )

# Pull in our pico_stdlib which pulls in commonly used features
target_link_libraries(readtemp pico_stdlib hardware_i2c)

pico_enable_stdio_usb(readtemp 1)
pico_enable_stdio_uart(readtemp 0)

# create map/bin/hex file etc.
pico_add_extra_outputs(readtemp)

# add url via pico_set_program_url
# example_auto_set_url(fancyblink)
