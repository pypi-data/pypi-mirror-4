#include <bitset>
#include <iostream>

using namespace std;

// g++ test_bitset.cpp -o test_bitset  -g3 -DDEBUG=1 -D_GLIBCXX_DEBUG_PEDANTIC -D_GLIBCPP_CONCEPT_CHECKS -Wall -W -Wredundant-decls -Wunknown-pragmas -Wunused -Wunused -Wendif-labels -Wno-sign-compare -Wshadow -O -Wuninitialized

#define UNUSED __attribute((__unused__))

int main(UNUSED int argc, UNUSED char* argv[]) {

  std::bitset<1> bs;

  for (int val=0; val < 2; val++) {
    bs[0] = val;
    cout << "bs:" << val << " " << bs << "\n ";
    cout << "  " << bs[0] << " " << bool(bs[0]) << " " <<  static_cast<bool>(bs[0]) << "\n\n";
  }
  return 0;
}
