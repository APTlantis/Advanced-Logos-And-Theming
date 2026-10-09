// Types describe illustrative review data, not engine configuration.
type ColorId = `color_${string}`;
type ReviewState = "pending" | "reviewed";

interface ColorEntry {
  readonly id: ColorId;
  hex: string;
  weight?: number;
}

interface Review<T> {
  value: T;
  state: ReviewState;
}

function review<T>(value: T): Review<T> {
  return { value, state: "pending" };
}

function summarize(entries: readonly ColorEntry[]): string[] {
  return entries
    .filter(entry => (entry.weight ?? 0) > 0)
    .map(({ id, hex }) => `${id}: ${hex.toUpperCase()}`);
}

const entries: ColorEntry[] = [
  { id: "color_01", hex: "#302820", weight: 0.6 },
  { id: "color_02", hex: "#C8A868", weight: 0.4 },
];

const result = review(summarize(entries));
if (result.state === "pending") {
  console.log(result.value.join("\n"));
}
