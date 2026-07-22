import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [trialsCsv, summaryCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!trialsCsv || !summaryCsv || !outputXlsx || !previewPng) {
  throw new Error("Usage: builder <trials.csv> <summary.csv> <report.xlsx> <preview.png>");
}

const workbook = await Workbook.fromCSV(
  await fs.readFile(trialsCsv, "utf8"), { sheetName: "Raw Trials" },
);
await workbook.fromCSV(
  await fs.readFile(summaryCsv, "utf8"), { sheetName: "Condition Summary" },
);
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("Condition Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:T901").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:T1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true, rowHeight: 42,
};
raw.getRange("A1:T901").format.autofitColumns();

summary.showGridLines = false;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:J19").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:J1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 42,
};
summary.getRange("B2:B19").format.numberFormat = "0.0";
summary.getRange("D2:J19").format.numberFormat = "0.000000";
summary.getRange("A1:J19").format.autofitColumns();

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-OCC-01 — Synthetic Occupancy Validation"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [[
  "CFG-S01 | Existing calculate_occupancy unchanged | 900 deterministic trials",
]];
report.getRange("A2:J2").format = {
  fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22,
};

report.getRange("A4:B12").values = [
  ["Validation metric", "Result"],
  ["Total trials", 900],
  ["Spectral bins per trial", 8192],
  ["Occupancy levels", 9],
  ["Layout conditions", 2],
  ["Maximum absolute error (percentage points)", null],
  ["Maximum standard deviation (%)", null],
  ["Maximum layout difference (percentage points)", null],
  ["Overall result", null],
];
report.getRange("B9").formulas = [["=MAX('Condition Summary'!I2:I19)"]];
report.getRange("B10").formulas = [["=MAX('Condition Summary'!G2:G19)"]];
report.getRange("B11").formulas = [[
  "=MAX(ABS('Condition Summary'!F2-'Condition Summary'!F11),ABS('Condition Summary'!F3-'Condition Summary'!F12),ABS('Condition Summary'!F4-'Condition Summary'!F13),ABS('Condition Summary'!F5-'Condition Summary'!F14),ABS('Condition Summary'!F6-'Condition Summary'!F15),ABS('Condition Summary'!F7-'Condition Summary'!F16),ABS('Condition Summary'!F8-'Condition Summary'!F17),ABS('Condition Summary'!F9-'Condition Summary'!F18),ABS('Condition Summary'!F10-'Condition Summary'!F19))",
]];
report.getRange("B12").formulas = [["=IF(AND(B9<=1E-9,B10<=1E-9,B11<=1E-9),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A12").format.font = { bold: true, color: "#334155" };
report.getRange("B9:B11").format.numberFormat = "0.000000";
report.getRange("B12").conditionalFormats.add("containsText", {
  text: "PASS", format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});

report.getRange("A15:C24").values = [
  ["Expected occupancy (%)", "Clustered", "Distributed"],
  ...Array.from({ length: 9 }, () => [null, null, null]),
];
for (let index = 0; index < 9; index++) {
  const row = 16 + index;
  const clusteredSource = 2 + index;
  const distributedSource = 11 + index;
  report.getRange(`A${row}:C${row}`).formulas = [[
    `=VALUE('Condition Summary'!D${clusteredSource})`,
    `=VALUE('Condition Summary'!F${clusteredSource})`,
    `=VALUE('Condition Summary'!F${distributedSource})`,
  ]];
}
report.getRange("A15:C15").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 34,
};
report.getRange("A16:C24").format.numberFormat = "0.000";

const chart = report.charts.add("scatter", report.getRange("A15:C24"));
chart.title = "Measured vs Expected Spectral-Bin Occupancy";
chart.hasLegend = true;
chart.xAxis = { numberFormatCode: "0", min: 0, max: 100 };
chart.yAxis = { numberFormatCode: "0", min: 0, max: 100 };
chart.setPosition("D4", "J16");

report.getRange("A27:J27").merge();
report.getRange("A27").values = [["Engineering conclusion"]];
report.getRange("A27:J27").format = {
  fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A28:J31").merge();
report.getRange("A28").values = [[
  "The existing occupancy function exactly reproduced the realized fraction of 8,192 spectral bins above their corresponding thresholds in all 900 trials. Results were identical for clustered and distributed occupied bins, and repeated randomized threshold/amplitude conditions produced zero variation. This validates the implemented arithmetic definition of measurement-window spectral-bin occupancy.",
]];
report.getRange("A28:J31").format = {
  fill: "#E8F5F9", font: { color: "#163845" }, wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};
report.getRange("A33:J34").merge();
report.getRange("A33").values = [[
  "Scope limitation: occupancy here means the spectral-bin fraction above threshold in one measurement window. It is not regulatory occupancy, long-term channel utilization, or calibrated RF power.",
]];
report.getRange("A33:J34").format = {
  font: { italic: true, color: "#64748B", size: 9 }, wrapText: true,
};

report.getRange("A1:J34").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = {
  name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 39;
report.getRange("B:C").format.columnWidth = 20;
report.getRange("D:J").format.columnWidth = 18;

const check = await workbook.inspect({
  kind: "table", range: "Report!A4:J34", include: "values,formulas",
  tableMaxRows: 31, tableMaxCols: 10, maxChars: 8000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 }, summary: "formula error scan", maxChars: 2000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Report", range: "A1:J34", scale: 1.3, format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
