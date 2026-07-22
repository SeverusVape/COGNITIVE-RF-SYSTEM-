import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [rawCsv, summaryCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!rawCsv || !summaryCsv || !outputXlsx || !previewPng) throw new Error("Usage: builder <raw.csv> <summary.csv> <report.xlsx> <preview.png>");
const workbook = await Workbook.fromCSV(await fs.readFile(rawCsv, "utf8"), { sheetName: "Raw Trials" });
await workbook.fromCSV(await fs.readFile(summaryCsv, "utf8"), { sheetName: "SNR Summary" });
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("SNR Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false; raw.freezePanes.freezeRows(1);
raw.getRange("A1:AC901").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:AC1").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 }, wrapText: true, rowHeight: 40 };
raw.getRange("A1:AC901").format.autofitColumns();
summary.showGridLines = false; summary.freezePanes.freezeRows(1);
summary.getRange("A1:G10").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:G1").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" }, wrapText: true, rowHeight: 34 };
summary.getRange("D2:D10").format.numberFormat = "0.0%";
summary.getRange("E2:G10").format.numberFormat = "0.0";
summary.getRange("A1:G10").format.autofitColumns();

report.showGridLines = false;
report.getRange("A1:J1").merge(); report.getRange("A1").values = [["AV-PD-01 — Synthetic Peak-Detector Performance"]];
report.getRange("A1:J1").format = { fill: "#18232C", font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" }, rowHeight: 34 };
report.getRange("A2:J2").merge(); report.getRange("A2").values = [["CFG-S01 | Hann FFT | Existing local threshold and peak detector | 900 deterministic trials"]];
report.getRange("A2:J2").format = { fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22 };

report.getRange("A4:B11").values = [
  ["Acceptance metric", "Result"], ["Total trials", null], ["SNR levels", 9],
  ["Detection rise: -40 to -22 dB", null], ["Minimum required rise", 0.80],
  ["Detection probability at -22 dB", null], ["Minimum required at -22 dB", 0.95],
  ["Overall result", null],
];
report.getRange("B5").formulas = [["=COUNTA('Raw Trials'!C2:C901)"]];
report.getRange("B7").formulas = [["=VALUE('SNR Summary'!D9)-VALUE('SNR Summary'!D2)"]];
report.getRange("B9").formulas = [["=VALUE('SNR Summary'!D9)"]];
report.getRange("B11").formulas = [["=IF(AND(B7>=B8,B9>=B10,MAX('SNR Summary'!E2:E10)<=250),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" } };
report.getRange("A5:A11").format.font = { bold: true, color: "#334155" };
report.getRange("B7:B10").format.numberFormat = "0.0%";
report.getRange("B11").conditionalFormats.add("containsText", { text: "PASS", format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } } });

report.getRange("A14:G14").values = [["Input SNR (dB)", "Trials", "Detected", "Detection probability", "Median frequency error (Hz)", "p95 frequency error (Hz)", "Mean peaks returned"]];
for (let row = 15; row <= 23; row++) {
  const source = row - 13;
  report.getRange(`A${row}:G${row}`).formulas = [[`=VALUE('SNR Summary'!A${source})`, `=VALUE('SNR Summary'!B${source})`, `=VALUE('SNR Summary'!C${source})`, `=VALUE('SNR Summary'!D${source})`, `=IF('SNR Summary'!E${source}=\"NA\",\"NA\",VALUE('SNR Summary'!E${source}))`, `=IF('SNR Summary'!F${source}=\"NA\",\"NA\",VALUE('SNR Summary'!F${source}))`, `=VALUE('SNR Summary'!G${source})`]];
}
report.getRange("A14:G14").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" }, wrapText: true };
report.getRange("D15:D23").format.numberFormat = "0.0%";
report.getRange("E15:G23").format.numberFormat = "0.0";

const chart = report.charts.add("line", { chartType: "line", title: "Detection Probability vs Input SNR", hasLegend: false });
const series = chart.series.add("Detection probability");
series.categoryFormula = "'Report'!$A$15:$A$23"; series.formula = "'Report'!$D$15:$D$23"; series.fill = "#00AEEA";
chart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 }; chart.xAxis = { axisType: "textAxis" }; chart.setPosition("D4", "J12");

report.getRange("A25:J25").merge(); report.getRange("A25").values = [["Engineering interpretation"]];
report.getRange("A25:J25").format = { fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" } };
report.getRange("A26:J28").merge(); report.getRange("A26").values = [["The experiment characterizes the existing single-tone detector as a probability-of-detection curve, not a binary sensitivity claim. Processing gain allows detection below 0 dB input SNR. Frequency estimates remain FFT-bin limited. Noise-only false alarms, hardware sensitivity, and modulated signals are intentionally outside AV-PD-01 and are addressed separately."]];
report.getRange("A26:J28").format = { fill: "#E8F5F9", font: { color: "#163845" }, wrapText: true, verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#77B9CD" } };
report.getRange("A30:J30").merge(); report.getRange("A30").values = [["Scope: deterministic algorithm validation using synthetic IQ. Relative levels are not calibrated dBm and do not represent RTL-SDR sensitivity."]];
report.getRange("A30:J30").format = { font: { italic: true, color: "#64748B", size: 9 }, wrapText: true, rowHeight: 28 };
report.getRange("A1:J30").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" };
report.getRange("A:A").format.columnWidth = 27; report.getRange("B:B").format.columnWidth = 18; report.getRange("C:G").format.columnWidth = 19; report.getRange("H:J").format.columnWidth = 14;
report.freezePanes.freezeRows(2);

const check = await workbook.inspect({ kind: "table", range: "Report!A4:B11", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 2, maxChars: 2000 });
console.log(check.ndjson);
const errors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan", maxChars: 2000 });
console.log(errors.ndjson);
await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({ sheetName: "Report", range: "A1:J30", scale: 1.3, format: "png" });
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
