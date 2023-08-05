/**
 * @file /roscreate/src/roscreate2/templates/cpp/src/lib/package_name.cpp
 *
 * @brief File comment
 *
 * File comment
 *
 * @date Aug 10, 2012
 **/

/*****************************************************************************
** Includes
*****************************************************************************/

#include "../../include/%(name)s/%(name)s.hpp"
#include <iostream>

namespace %(name)s
{
  void Foo::helloDude() {
    std::cout << "Hello Dude" << std::endl;
  }
}


