// >>> PAPSAS v1.3 BEGIN
export function toCsvRow<T extends Record<string, unknown>>(row: T, order: (keyof T)[]): string {
  return order
    .map((k) => {
      const value = row[k];
      const text = String(value ?? "");
      return /[",\n]/.test(text) ? `"${text.replace(/"/g, '""')}"` : text;
    })
    .join(",");
}

export function toCsv(rows: Record<string, unknown>[]): string {
  if (!rows || rows.length === 0) return "";
  const headers = Array.from(new Set(rows.flatMap((r) => Object.keys(r)))) as (keyof Record<string, unknown>)[];
  const lines: string[] = [];
  lines.push(headers.join(","));
  for (const row of rows) {
    lines.push(toCsvRow(row, headers));
  }
  // normalize to LF for cross-platform stability
  return lines.join("\n");
}

export function downloadCsv(filename: string, csv: string): void {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}
// <<< PAPSAS v1.3 END
