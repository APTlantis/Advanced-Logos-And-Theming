// Illustrative data: these examples are displayed, never executed.
const HEX_COLOR = /^#[0-9a-f]{6}$/i;
const DEFAULT_LIMIT = 32;

class Palette {
  #colors;

  constructor(name, colors = []) {
    this.name = name;
    this.#colors = colors.filter(color => HEX_COLOR.test(color.hex));
  }

  get count() {
    return this.#colors.length;
  }

  describe(limit = DEFAULT_LIMIT) {
    const entries = this.#colors.slice(0, limit);
    return entries.map(({ id, hex }, index) => ({
      label: `${index + 1}: ${id}`,
      value: hex.toUpperCase(),
      selected: index === 0,
    }));
  }
}

const palette = new Palette("Illustrative palette", [
  { id: "color_01", hex: "#302820" },
  { id: "color_02", hex: "#C8A868" },
]);

console.log(`${palette.name}: ${palette.count} colors`);
console.table(palette.describe());
