import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [rawCsv, summaryCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!rawCsv || !summaryCsv || !outputXlsx || !previewPng) {
  throw new Error("Usage: builder <raw.csv> <summary.csv> <report.xlsx> <preview.png>");
}

const workbook = await Workbook.fromCSV(
  await fs.readFile(rawCsv, "utf8"),
  { sheetName: "Raw Trials" },
);
await workbook.fromCSV(
  await fs.readFile(summaryCsv, "utf8"),
  { sheetName: "Condition Summary" },
);
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("Condition Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:W1001").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:W1").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true,
  rowHeight: 42,
};
raw.getRange("A1:W1001").format.autofitColumns();

summary.showGridLines = false;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:L3").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:L1").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  rowHeight: 38,
};
summary.getRange("D2:D3").format.numberFormat = "0.0%";
summary.getRange("E2:E3").format.numberFormat = "0.00";
summary.getRange("F2:F3").format.numberFormat = "0.0%";
summary.getRange("G2:H3").format.numberFormat = "0.00";
summary.getRange("I2:I3").format.numberFormat = "0.0%";
summary.getRange("J2:J3").format.numberFormat = "0.00";
summary.getRange("K2:K3").format.numberFormat = "0.0%";
summary.getRange("A1:L3").format.autofitColumns();

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-PD-02 — Noise-Only False-Alarm Characterization"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [["CFG-S01 | Hann FFT | Existing adaptive detector | 1,000 deterministic signal-free frames"]];
report.getRange("A2:J2").format = {
  fill: "#18232C",
  font: { color: "#A8B3BD" },
  rowHeight: 22,
};

report.getRange("A4:B13").values = [
  ["Acceptance metric", "Result"],
  ["Total noise-only frames", null],
  ["Conditions", 2],
  ["Worst frame false-alarm probability", null],
  ["Maximum allowed", 0.05],
  ["Worst mean false candidates/frame", null],
  ["Maximum allowed", 0.10],
  ["Worst fraction reaching 3-peak cap", null],
  ["Maximum allowed", 0.01],
  ["Overall result", null],
];
report.getRange("B5").formulas = [["=COUNTA('Raw Trials'!C2:C1001)"]];
report.getRange("B7").formulas = [["=MAX(VALUE('Condition Summary'!D2),VALUE('Condition Summary'!D3))"]];
report.getRange("B9").formulas = [["=MAX(VALUE('Condition Summary'!E2),VALUE('Condition Summary'!E3))"]];
report.getRange("B11").formulas = [["=MAX(VALUE('Condition Summary'!F2),VALUE('Condition Summary'!F3))"]];
report.getRange("B13").formulas = [["=IF(AND(B7<=B8,B9<=B10,B11<=B12),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A13").format.font = { bold: true, color: "#334155" };
report.getRange("B7:B8").format.numberFormat = "0.0%";
report.getRange("B9:B10").format.numberFormat = "0.00";
report.getRange("B11:B12").format.numberFormat = "0.0%";
report.getRange("B13").conditionalFormats.add("containsText", {
  text: "FAIL",
  format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});
report.getRange("B13").conditionalFormats.add("containsText", {
  text: "PASS",
  format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});

report.getRange("A15:H15").values = [[
  "Condition", "Trials", "Frames with false alarm", "Frame false-alarm probability",
  "Mean false peaks/frame", "Frames at 3-peak cap", "Median max excess (dB)", "Result",
]];
for (let row = 16; row <= 17; row++) {
  const source = row - 14;
  report.getRange(`A${row}:H${row}`).formulas = [[
    `='Condition Summary'!A${source}`,
    `=VALUE('Condition Summary'!B${source})`,
    `=VALUE('Condition Summary'!C${source})`,
    `=VALUE('Condition Summary'!D${source})`,
    `=VALUE('Condition Summary'!E${source})`,
    `=VALUE('Condition Summary'!F${source})`,
    `=IF('Condition Summary'!G${source}=\"NA\",\"NA\",VALUE('Condition Summary'!G${source}))`,
    `='Condition Summary'!L${source}`,
  ]];
}
report.getRange("A15:H15").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  rowHeight: 36,
};
report.getRange("D16:D17").format.numberFormat = "0.0%";
report.getRange("E16:E17").format.numberFormat = "0.00";
report.getRange("F16:F17").format.numberFormat = "0.0%";
report.getRange("G16:G17").format.numberFormat = "0.00";
report.getRange("H16:H17").conditionalFormats.add("containsText", {
  text: "FAIL",
  format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.getRange("J4:L6").values = [
  ["Condition", "False-alarm probability", "Limit"],
  ["Flat noise", null, 0.05],
  ["Uneven baseline", null, 0.05],
];
report.getRange("K5").formulas = [["=D16"]];
report.getRange("K6").formulas = [["=D17"]];
const chart = report.charts.add("bar", report.getRange("J4:L6"));
chart.title = "False-Alarm Probability by Noise Condition";
chart.hasLegend = true;
chart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 };
chart.xAxis = { axisType: "textAxis" };
chart.setPosition("D4", "J13");

report.getRange("A20:J20").merge();
report.getRange("A20").values = [["Engineering interpretation"]];
report.getRange("A20:J20").format = {
  fill: "#0B6E8E",
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A21:J24").merge();
report.getRange("A21").values = [[
  "AV-PD-02 evaluates raw detector specificity, not the temporally confirmed signals shown by the full application. A failing result means the configured local threshold reliably selects statistical maxima in signal-free spectra and therefore cannot, by itself, distinguish noise from a signal. This is a bounded engineering limitation, not a software crash. No detector parameters were changed during validation.",
]];
report.getRange("A21:J24").format = {
  fill: "#E8F5F9",
  font: { color: "#163845" },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};
report.getRange("A26:J26").merge();
report.getRange("A26").values = [[
  "Scope: deterministic synthetic algorithm validation. It excludes signal-history confirmation, classification, hardware interference, and any claim of calibrated receiver sensitivity.",
]];
report.getRange("A26:J26").format = {
  font: { italic: true, color: "#64748B", size: 9 },
  wrapText: true,
  rowHeight: 30,
};
report.getRange("A1:J26").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = {
  name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 28;
report.getRange("B:B").format.columnWidth = 18;
report.getRange("C:H").format.columnWidth = 19;
report.getRange("I:J").format.columnWidth = 14;

const check = await workbook.inspect({
  kind: "table",
  range: "Report!A4:H17",
  include: "values,formulas",
  tableMaxRows: 14,
  tableMaxCols: 8,
  maxChars: 3500,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
  maxChars: 2000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Report", range: "A1:J26", scale: 1.3, format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
