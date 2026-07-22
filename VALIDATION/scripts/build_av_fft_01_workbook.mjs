import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [inputCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!inputCsv || !outputXlsx || !previewPng) {
  throw new Error("Usage: node build_av_fft_01_workbook.mjs <raw.csv> <report.xlsx> <preview.png>");
}

const csvText = await fs.readFile(inputCsv, "utf8");
const workbook = await Workbook.fromCSV(csvText, { sheetName: "Raw Trials" });
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.add("Summary");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:R26").format.font = { name: "Aptos", size: 9 };
raw.getRange("A1:R1").format = {
  fill: "#25313B",
  font: { name: "Aptos", size: 9, bold: true, color: "#FFFFFF" },
  wrapText: true,
};
raw.getRange("A2:R26").format.borders = {
  insideHorizontal: { style: "thin", color: "#D8DEE4" },
};
raw.getRange("F2:P26").format.numberFormat = "0.000";
raw.getRange("A1:R26").format.autofitColumns();
raw.getRange("A1:R1").format.rowHeight = 34;

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["AV-FFT-01 — Synthetic FFT Frequency Accuracy"]];
summary.getRange("A1:H1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 32,
  verticalAlignment: "center",
};
summary.getRange("A2:H2").merge();
summary.getRange("A2").values = [["CFG-S01 | Bin-centered deterministic complex tones | Existing application FFT implementation"]];
summary.getRange("A2:H2").format = {
  fill: "#18232C",
  font: { name: "Aptos", size: 10, color: "#A8B3BD" },
  rowHeight: 22,
};

summary.getRange("A4:B10").values = [
  ["Metric", "Value"],
  ["Trial count", null],
  ["Passed trials", null],
  ["Failed trials", null],
  ["Maximum absolute error (Hz)", null],
  ["Mean signed error (Hz)", null],
  ["Acceptance limit (Hz)", null],
];
summary.getRange("B5:B10").formulas = [
  ["=COUNTA('Raw Trials'!C2:C26)"],
  ["=COUNTIF('Raw Trials'!Q2:Q26,\"true\")"],
  ["=COUNTIF('Raw Trials'!Q2:Q26,\"false\")"],
  ["=MAX('Raw Trials'!N2:N26)"],
  ["=AVERAGE('Raw Trials'!M2:M26)"],
  ["='Raw Trials'!P2"],
];
summary.getRange("A4:B4").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A5:A10").format.font = { bold: true, color: "#334155" };
summary.getRange("B5:B10").format.numberFormat = "0.000";
summary.getRange("B5:B7").format.numberFormat = "0";
summary.getRange("A4:B10").format.borders = {
  insideHorizontal: { style: "thin", color: "#D8DEE4" },
  outside: { style: "thin", color: "#AEB8C2" },
};

summary.getRange("A12:C18").values = [
  ["Expected offset (kHz)", "Mean error (Hz)", "Trials"],
  [-768, null, null],
  [-384, null, null],
  [0, null, null],
  [384, null, null],
  [768, null, null],
  ["Overall", null, null],
];
summary.getRange("B13").formulas = [["=AVERAGEIF('Raw Trials'!$J$2:$J$26,A13*1000,'Raw Trials'!$M$2:$M$26)"]];
summary.getRange("B13:B17").fillDown();
summary.getRange("C13").formulas = [["=COUNTIF('Raw Trials'!$J$2:$J$26,A13*1000)"]];
summary.getRange("C13:C17").fillDown();
summary.getRange("B18").formulas = [["=AVERAGE('Raw Trials'!M2:M26)"]];
summary.getRange("C18").formulas = [["=COUNTA('Raw Trials'!C2:C26)"]];
summary.getRange("A12:C12").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A12:C18").format.borders = {
  insideHorizontal: { style: "thin", color: "#D8DEE4" },
  outside: { style: "thin", color: "#AEB8C2" },
};
summary.getRange("B13:B18").format.numberFormat = "0.000";
summary.getRange("C13:C18").format.numberFormat = "0";

summary.getRange("A20:H20").merge();
summary.getRange("A20").values = [["Engineering conclusion"]];
summary.getRange("A20:H20").format = {
  fill: "#0B6E8E",
  font: { bold: true, color: "#FFFFFF" },
};
summary.getRange("A21:H22").merge();
summary.getRange("A21").values = [[
  "PASS — Every bin-centered synthetic tone was placed on its expected shifted FFT bin. This validates numerical FFT-axis placement only; it does not validate RTL-SDR oscillator accuracy, off-bin interpolation, or calibrated power.",
]];
summary.getRange("A21:H22").format = {
  fill: "#E8F5F9",
  font: { color: "#163845" },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};

const chart = summary.charts.add("line", summary.getRange("A12:B17"));
chart.title = "Signed Frequency Error Across FFT Span (Hz)";
chart.hasLegend = false;
chart.xAxis = { axisType: "textAxis" };
chart.yAxis = { numberFormatCode: "0.0", min: -125, max: 125 };
chart.setPosition("D4", "H18");

summary.getRange("A1:H22").format.font = { name: "Aptos", size: 10 };
summary.getRange("A1:H2").format.font = { name: "Aptos Display", size: 12, color: "#FFFFFF" };
summary.getRange("A1").format.font = { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" };
summary.getRange("A:A").format.columnWidth = 30;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("C:C").format.columnWidth = 12;
summary.getRange("D:H").format.columnWidth = 14;
summary.freezePanes.freezeRows(2);

const inspection = await workbook.inspect({
  kind: "table",
  range: "Summary!A1:H22",
  include: "values,formulas",
  tableMaxRows: 22,
  tableMaxCols: 8,
});
console.log(inspection.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Summary",
  range: "A1:H22",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputXlsx);
