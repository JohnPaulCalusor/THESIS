// >>> PAPSAS v1.3 BEGIN
export function toCsv(rows: Array<Record<string, any>>): string {
  if (!Array.isArray(rows) || rows.length === 0) return "";
  const keys = Array.from(new Set(rows.flatMap(r => Object.keys(r))));
  const esc = (v: any) => {
    const s = String(v ?? "").replace(/"/g, '""');
    return /[",\n]/.test(s) ? `"${s}"` : s;
  };
  const lines = [keys.join(",")];
  for (const r of rows) lines.push(keys.map(k => esc(r[k])).join(","));
  return lines.join("\r\n");
}

export function downloadCsv(filename: string, csv: string) {
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// Filename format guidance:
// results-election-<id>-<YYYYMMDD-HHMM>.csv
// <<< PAPSAS v1.3 END

