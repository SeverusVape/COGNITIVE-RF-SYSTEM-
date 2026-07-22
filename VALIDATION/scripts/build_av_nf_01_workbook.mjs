import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [rawCsv, conditionCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!rawCsv || !conditionCsv || !outputXlsx || !previewPng) throw new Error("Usage: builder <raw.csv> <conditions.csv> <report.xlsx> <preview.png>");
const workbook = await Workbook.fromCSV(await fs.readFile(rawCsv, "utf8"), { sheetName: "Raw Trials" });
await workbook.fromCSV(await fs.readFile(conditionCsv, "utf8"), { sheetName: "Condition Summary" });
const raw = workbook.worksheets.getItem("Raw Trials");
const conditions = workbook.worksheets.getItem("Condition Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false; raw.freezePanes.freezeRows(1);
raw.getRange("A1:AA301").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:AA1").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 }, wrapText: true, rowHeight: 40 };
raw.getRange("F2:Y301").format.numberFormat = "0.000";
raw.getRange("A1:AA301").format.autofitColumns();
conditions.showGridLines = false; conditions.freezePanes.freezeRows(1);
conditions.getRange("A1:I4").format.font = { name: "Aptos", size: 9 };
conditions.getRange("A1:I1").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" }, wrapText: true, rowHeight: 34 };
conditions.getRange("C2:H4").format.numberFormat = "0.000";
conditions.getRange("A1:I4").format.autofitColumns();

report.showGridLines = false;
report.getRange("A1:J1").merge(); report.getRange("A1").values = [["AV-NF-01 — Adaptive Noise-Floor Validation"]];
report.getRange("A1:J1").format = { fill: "#18232C", font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" }, rowHeight: 34 };
report.getRange("A2:J2").merge(); report.getRange("A2").values = [["CFG-S01 | Flat, curved, and stepped synthetic spectral baselines | Existing percentile estimator"]];
report.getRange("A2:J2").format = { fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22 };

report.getRange("A4:B12").values = [
  ["Acceptance metric", "Result"], ["Trials", null], ["Trials per condition", null],
  ["Mean MAE limit (dB)", 1.25], ["Maximum condition mean MAE (dB)", null],
  ["95th-percentile trial MAE limit (dB)", 1.50], ["Maximum observed p95 trial MAE (dB)", null],
  ["Peak-effect p95 limit (dB)", 0.25], ["Overall result", null],
];
report.getRange("B5:B6").formulas = [["=COUNTA('Raw Trials'!C2:C301)"], ["=B5/3"]];
report.getRange("B8").formulas = [["=MAX('Condition Summary'!D2:D4)"]];
report.getRange("B10").formulas = [["=MAX('Condition Summary'!E2:E4)"]];
report.getRange("B12").formulas = [["=IF(AND(B8<=B7,B10<=B9,MAX('Condition Summary'!G2:G4)<=B11),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" } };
report.getRange("A5:A12").format.font = { bold: true, color: "#334155" };
report.getRange("B7:B11").format.numberFormat = "0.000";
report.getRange("A4:B12").format.borders = { insideHorizontal: { style: "thin", color: "#D8DEE4" }, outside: { style: "thin", color: "#AEB8C2" } };
report.getRange("B12").conditionalFormats.add("containsText", { text: "PASS", format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } } });

report.getRange("A14:H18").values = [
  ["Condition", "Trials", "Mean bias (dB)", "Mean MAE (dB)", "p95 trial MAE (dB)", "Mean p95 bin error (dB)", "p95 peak effect (dB)", "Pass"],
  ["Flat", 100, null, null, null, null, null, null],
  ["Curved", 100, null, null, null, null, null, null],
  ["Stepped", 100, null, null, null, null, null, null],
  ["Limits", null, null, 1.25, 1.50, null, 0.25, null],
];
for (let row = 15; row <= 17; row++) {
  const source = row - 13;
  report.getRange(`C${row}:H${row}`).formulas = [[
    `='Condition Summary'!C${source}`, `='Condition Summary'!D${source}`,
    `='Condition Summary'!E${source}`, `='Condition Summary'!F${source}`,
    `='Condition Summary'!G${source}`, `='Condition Summary'!I${source}`,
  ]];
}
report.getRange("A14:H14").format = { fill: "#25313B", font: { bold: true, color: "#FFFFFF" }, wrapText: true };
report.getRange("C15:G18").format.numberFormat = "0.000";
report.getRange("A14:H18").format.borders = { insideHorizontal: { style: "thin", color: "#D8DEE4" }, outside: { style: "thin", color: "#AEB8C2" } };

const chart = report.charts.add("bar", {
  chartType: "bar",
  title: "Noise-Floor Error by Baseline Condition (dB)",
  hasLegend: true,
});
const meanSeries = chart.series.add("Mean MAE"); meanSeries.categoryFormula = "'Report'!$A$15:$A$17"; meanSeries.formula = "'Report'!$D$15:$D$17"; meanSeries.fill = "#00AEEA";
const p95Series = chart.series.add("p95 Trial MAE"); p95Series.categoryFormula = "'Report'!$A$15:$A$17"; p95Series.formula = "'Report'!$E$15:$E$17"; p95Series.fill = "#7F8C98";
chart.title = "Noise-Floor Error by Baseline Condition (dB)"; chart.hasLegend = true; chart.yAxis = { numberFormatCode: "0.00", min: 0, max: 1.5 }; chart.setPosition("D4", "J12");

report.getRange("A20:J20").merge(); report.getRange("A20").values = [["Engineering conclusion"]];
report.getRange("A20:J20").format = { fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" } };
report.getRange("A21:J23").merge(); report.getRange("A21").values = [["PASS — The existing 30th-percentile local estimator tracked flat, curved, and stepped synthetic baselines within the declared limits. Seven narrow injected peaks did not materially raise the estimated floor, and the detection threshold preserved its exact 10 dB margin. The expected negative bias is consistent with estimating a lower percentile rather than the mean. Abrupt-step transition bins were excluded because they lie inside the estimator window."]];
report.getRange("A21:J23").format = { fill: "#E8F5F9", font: { color: "#163845" }, wrapText: true, verticalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#77B9CD" } };
report.getRange("A25:J25").merge(); report.getRange("A25").values = [["Scope: algorithm validation using synthetic spectral data. This does not measure RTL-SDR noise figure, antenna noise, calibrated dBm, or analog receiver performance."]];
report.getRange("A25:J25").format = { font: { italic: true, color: "#64748B", size: 9 }, wrapText: true, rowHeight: 28 };
report.getRange("A1:J25").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" };
report.getRange("A:A").format.columnWidth = 28; report.getRange("B:B").format.columnWidth = 18; report.getRange("C:H").format.columnWidth = 17; report.getRange("I:J").format.columnWidth = 14;
report.freezePanes.freezeRows(2);

console.log((await workbook.inspect({ kind: "table", range: "Report!A1:J25", include: "values,formulas", tableMaxRows: 25, tableMaxCols: 10 })).ndjson);
console.log((await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" })).ndjson);
await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({ sheetName: "Report", range: "A1:J25", scale: 1.3, format: "png" });
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
