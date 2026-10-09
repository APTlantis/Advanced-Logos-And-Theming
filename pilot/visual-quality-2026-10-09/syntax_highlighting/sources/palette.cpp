#include <algorithm>
#include <iostream>
#include <iterator>
#include <string>
#include <vector>

// Illustrative records; no palette extraction is performed.
struct Color {
    std::string id;
    std::string hex;
    double weight = 0.0;
};

template <typename Predicate>
std::vector<Color> select(const std::vector<Color>& colors, Predicate predicate) {
    std::vector<Color> result;
    std::copy_if(colors.begin(), colors.end(), std::back_inserter(result), predicate);
    return result;
}

int main() {
    constexpr unsigned canonical_count = 32;
    const std::vector<Color> palette = {
        {"color_01", "#302820", 0.6},
        {"color_02", "#C8A868", 0.4},
    };
    const auto selected = select(palette, [](const Color& color) {
        return color.weight > 0.0;
    });

    std::cout << "Illustrative entries; expected " << canonical_count << '\n';
    for (const auto& color : selected) {
        std::cout << color.id << ": " << color.hex << '\n';
    }
    return 0;
}
