#include <iostream>
#include <string>

int main() {
    std::string line;
    int i = 0;
    const std::string choices[3] = {"rock", "paper", "scissors"};
    while(std::cin >> line) {
        if(line == "quit") break;
        if(line == "choose") {
            std::cout << choices[i % 3] << std::endl;
            i ++;
        }
    }
}
