import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [framesCsv, windowsCsv, summaryCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!framesCsv || !windowsCsv || !summaryCsv || !outputXlsx || !previewPng) {
  throw new Error("Usage: builder <frames.csv> <windows.csv> <summary.csv> <report.xlsx> <preview.png>");
}

const workbook = await Workbook.fromCSV(
  await fs.readFile(framesCsv, "utf8"),
  { sheetName: "Frame Results" },
);
await workbook.fromCSV(
  await fs.readFile(windowsCsv, "utf8"),
  { sheetName: "Window Results" },
);
await workbook.fromCSV(
  await fs.readFile(summaryCsv, "utf8"),
  { sheetName: "Condition Summary" },
);

const frames = workbook.worksheets.getItem("Frame Results");
const windows = workbook.worksheets.getItem("Window Results");
const summary = workbook.worksheets.getItem("Condition Summary");
const report = workbook.worksheets.add("Report");

for (const sheet of [frames, windows, summary]) {
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
}
frames.getRange("A1:U10001").format.font = { name: "Aptos", size: 8 };
frames.getRange("A1:U1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true, rowHeight: 42,
};
frames.getRange("A1:U10001").format.autofitColumns();
windows.getRange("A1:M101").format.font = { name: "Aptos", size: 9 };
windows.getRange("A1:M1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 38,
};
windows.getRange("A1:M101").format.autofitColumns();
summary.getRange("A1:T3").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:T1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 42,
};
summary.getRange("I2:I3").format.numberFormat = "0.0%";
summary.getRange("J2:L3").format.numberFormat = "0.00";
summary.getRange("M2:M3").format.numberFormat = "0.0%";
summary.getRange("A1:T3").format.autofitColumns();

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-PC-01 — Temporal Confirmation False-Alarm Validation"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [[
  "CFG-S01 | Existing FFT, detector, and PeakConfirmer | 50 × 100-frame windows per condition",
]];
report.getRange("A2:J2").format = {
  fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22,
};

report.getRange("A4:B13").values = [
  ["Validation metric", "Result"],
  ["Total noise-only frames", null],
  ["Observation windows", null],
  ["Required confirmation hits", null],
  ["Confirmation window (frames)", null],
  ["Frequency tolerance (kHz)", null],
  ["Worst confirmed-frame probability", null],
  ["Worst suppression ratio", null],
  ["Worst p95 false confirmations/window", null],
  ["Overall result", null],
];
report.getRange("B5").formulas = [["=COUNTA('Frame Results'!F2:F10001)"]];
report.getRange("B6").formulas = [["=COUNTA('Window Results'!D2:D101)"]];
report.getRange("B7").formulas = [["=VALUE('Frame Results'!Q2)"]];
report.getRange("B8").formulas = [["=VALUE('Frame Results'!R2)"]];
report.getRange("B9").formulas = [["=VALUE('Frame Results'!S2)"]];
report.getRange("B10").formulas = [["=MAX(VALUE('Condition Summary'!I2),VALUE('Condition Summary'!I3))"]];
report.getRange("B11").formulas = [["=MIN(VALUE('Condition Summary'!M2),VALUE('Condition Summary'!M3))"]];
report.getRange("B12").formulas = [["=MAX(VALUE('Condition Summary'!L2),VALUE('Condition Summary'!L3))"]];
report.getRange("B13").formulas = [["=IF(COUNTIF('Condition Summary'!T2:T3,\"FAIL\")>0,\"FAIL\",\"PASS\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A13").format.font = { bold: true, color: "#334155" };
report.getRange("B10:B11").format.numberFormat = "0.0%";
report.getRange("B12").format.numberFormat = "0.00";
report.getRange("B13").conditionalFormats.add("containsText", {
  text: "FAIL", format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.getRange("A15:J15").values = [[
  "Condition", "Frames", "Raw candidates", "Confirmed false", "Confirmed-frame probability",
  "Mean confirmed/frame", "Mean confirmed/window", "p95 confirmed/window", "Suppression", "Result",
]];
for (let row = 16; row <= 17; row++) {
  const source = row - 14;
  report.getRange(`A${row}:J${row}`).formulas = [[
    `='Condition Summary'!A${source}`,
    `=VALUE('Condition Summary'!C${source})`,
    `=VALUE('Condition Summary'!E${source})`,
    `=VALUE('Condition Summary'!H${source})`,
    `=VALUE('Condition Summary'!I${source})`,
    `=VALUE('Condition Summary'!J${source})`,
    `=VALUE('Condition Summary'!K${source})`,
    `=VALUE('Condition Summary'!L${source})`,
    `=VALUE('Condition Summary'!M${source})`,
    `='Condition Summary'!T${source}`,
  ]];
}
report.getRange("A15:J15").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 9 },
  wrapText: true, rowHeight: 40,
};
report.getRange("E16:E17").format.numberFormat = "0.0%";
report.getRange("F16:H17").format.numberFormat = "0.00";
report.getRange("I16:I17").format.numberFormat = "0.0%";
report.getRange("J16:J17").conditionalFormats.add("containsText", {
  text: "FAIL", format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.getRange("L4:N6").values = [
  ["Condition", "Raw candidates/frame", "Confirmed false/frame"],
  ["Flat noise", null, null],
  ["Uneven baseline", null, null],
];
report.getRange("M5").formulas = [["=VALUE('Condition Summary'!F2)"]];
report.getRange("N5").formulas = [["=VALUE('Condition Summary'!J2)"]];
report.getRange("M6").formulas = [["=VALUE('Condition Summary'!F3)"]];
report.getRange("N6").formulas = [["=VALUE('Condition Summary'!J3)"]];
const candidateChart = report.charts.add("bar", report.getRange("L4:N6"));
candidateChart.title = "Raw vs Temporally Confirmed Noise Candidates";
candidateChart.hasLegend = true;
candidateChart.xAxis = { axisType: "textAxis" };
candidateChart.yAxis = { numberFormatCode: "0.0", min: 0, max: 3.2 };
candidateChart.setPosition("D4", "J13");

report.getRange("A20:J20").merge();
report.getRange("A20").values = [["Engineering conclusion"]];
report.getRange("A20:J20").format = {
  fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A21:J24").merge();
report.getRange("A21").values = [[
  "The unchanged temporal confirmation stage suppresses a portion of raw noise candidates, but it does not meet the frozen false-confirmation criteria. Flat noise retains a 37.3% confirmed-frame probability and uneven-baseline noise retains 91.2%. Suppression is 85.9% and 44.7%, respectively, below the required 95%. The proposed bounded confirmed false-signal claim is therefore not supported under these deterministic conditions. This is an engineering validation result; no application or detector parameters were changed.",
]];
report.getRange("A21:J24").format = {
  fill: "#FFF4E5", font: { color: "#6B3B00" }, wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#E4A23A" },
};
report.getRange("A26:J26").merge();
report.getRange("A26").values = [[
  "Scope: deterministic synthetic validation through PeakConfirmer. Signal-history aging, classification, hardware interference, and displayed UI false-alarm rate remain outside this claim.",
]];
report.getRange("A26:J26").format = {
  font: { italic: true, color: "#64748B", size: 9 }, wrapText: true, rowHeight: 30,
};

report.getRange("A1:J26").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = {
  name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 29;
report.getRange("B:B").format.columnWidth = 18;
report.getRange("C:J").format.columnWidth = 18;

const check = await workbook.inspect({
  kind: "table", range: "Report!A4:J17", include: "values,formulas",
  tableMaxRows: 14, tableMaxCols: 10, maxChars: 5000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 }, summary: "formula error scan", maxChars: 2000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Report", range: "A1:J26", scale: 1.3, format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
