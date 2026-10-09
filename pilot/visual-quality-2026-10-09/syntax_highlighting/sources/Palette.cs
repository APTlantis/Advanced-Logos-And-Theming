using System;
using System.Collections.Generic;
using System.Linq;

// Illustrative records for a local review.
public sealed record ColorEntry(string Id, string Hex, double Weight);

public static class PaletteReview
{
    private const int CanonicalCount = 32;

    public static string Describe(ColorEntry? entry) => entry switch
    {
        null => "No entry selected",
        { Weight: <= 0 } => "Entry has no observed weight",
        _ => $"{entry.Id}: {entry.Hex.ToUpperInvariant()}"
    };

    public static void Main()
    {
        IReadOnlyList<ColorEntry> colors = new[]
        {
            new ColorEntry("color_01", "#302820", 0.6),
            new ColorEntry("color_02", "#C8A868", 0.4)
        };

        var labels = colors.Where(color => color.Weight > 0)
                           .Select(color => Describe(color));
        Console.WriteLine($"Illustrative entries; expected {CanonicalCount}");
        foreach (var label in labels)
        {
            Console.WriteLine(label);
        }
    }
}
