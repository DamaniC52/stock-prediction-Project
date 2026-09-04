import { useEffect, useState } from "react";

const light = {
  actual: "#2a78d6",
  predicted: "#eb6834",
  grid: "#e1e0d9",
  axis: "#c3c2b7",
  muted: "#898781",
  surface: "#fcfcfb",
  primary: "#0b0b0b",
  secondary: "#52514e",
};

const dark = {
  actual: "#3987e5",
  predicted: "#d95926",
  grid: "#2c2c2a",
  axis: "#383835",
  muted: "#898781",
  surface: "#1a1a19",
  primary: "#ffffff",
  secondary: "#c3c2b7",
};

// Chart.js paints to canvas and cannot read CSS variables, so the token values
// are mirrored here and swapped when the OS theme changes.
export function useChartTheme() {
  const [isDark, setIsDark] = useState(
    () => window.matchMedia?.("(prefers-color-scheme: dark)").matches ?? false
  );

  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const onChange = (event) => setIsDark(event.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);

  return isDark ? dark : light;
}
