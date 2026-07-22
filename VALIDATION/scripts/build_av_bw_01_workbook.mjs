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
  await fs.readFile(summaryCsv, "utf8"), { sheetName: "Width Summary" },
);
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("Width Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:W701").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:W1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true, rowHeight: 42,
};
raw.getRange("A1:W701").format.autofitColumns();

summary.showGridLines = false;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:K15").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:K1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 42,
};
summary.getRange("E2:E15").format.numberFormat = "0.0%";
summary.getRange("F2:K15").format.numberFormat = "0.000";
summary.getRange("A1:K15").format.autofitColumns();

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-BW-01 — Bandwidth Heuristic Validation"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [[
  "CFG-S01 | Existing −15 dB estimator unchanged | 700 deterministic controlled-spectrum trials",
]];
report.getRange("A2:J2").format = {
  fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22,
};

report.getRange("A4:B12").values = [
  ["Validation metric", "Result"],
  ["Total trials", 700],
  ["Controlled shape families", 2],
  ["Controlled widths", 7],
  ["FFT bin spacing (kHz)", 0.25],
  ["Detection probability, 5–200 kHz", null],
  ["Detection probability, 400 kHz", null],
  ["Maximum p95 width error (kHz)", null],
  ["Overall result", null],
];
report.getRange("B9").formulas = [["=MIN('Width Summary'!E2:E7,'Width Summary'!E9:E14)"]];
report.getRange("B10").formulas = [["=MIN('Width Summary'!E8,'Width Summary'!E15)"]];
report.getRange("B11").formulas = [["=MAX('Width Summary'!J2:J7,'Width Summary'!J9:J14)"]];
report.getRange("B12").formulas = [["=IF(AND(B9=1,B10=1,B11<=1),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A12").format.font = { bold: true, color: "#334155" };
report.getRange("B8").format.numberFormat = "0.00";
report.getRange("B9:B10").format.numberFormat = "0.0%";
report.getRange("B11").format.numberFormat = "0.000";
report.getRange("B12").conditionalFormats.add("containsText", {
  text: "PASS", format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});
report.getRange("B12").conditionalFormats.add("containsText", {
  text: "FAIL", format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.getRange("A15:C22").values = [
  ["Controlled width (kHz)", "Gaussian estimate", "Flat-top estimate"],
  ...Array.from({ length: 7 }, () => [null, null, null]),
];
for (let index = 0; index < 6; index++) {
  const row = 16 + index;
  const gaussianSource = 2 + index;
  const flatSource = 9 + index;
  report.getRange(`A${row}:C${row}`).formulas = [[
    `=VALUE('Width Summary'!B${gaussianSource})`,
    `=IFERROR(VALUE('Width Summary'!F${gaussianSource}),NA())`,
    `=IFERROR(VALUE('Width Summary'!F${flatSource}),NA())`,
  ]];
}
report.getRange("A22:C22").values = [[400, "No detection", "No detection"]];
report.getRange("A15:C15").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 34,
};
report.getRange("A16:C22").format.numberFormat = "0.00";

const chart = report.charts.add("scatter", report.getRange("A15:C21"));
chart.title = "Estimated vs Controlled −15 dB Width";
chart.hasLegend = true;
chart.xAxis = { numberFormatCode: "0", min: 0, max: 420 };
chart.yAxis = { numberFormatCode: "0", min: 0, max: 420 };
chart.setPosition("D4", "J16");

report.getRange("A25:J25").merge();
report.getRange("A25").values = [["Engineering conclusion"]];
report.getRange("A25:J25").format = {
  fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A26:J30").merge();
report.getRange("A26").values = [[
  "For both controlled shape families, widths from 5 to 200 kHz were detected in every trial. The existing estimator reported a repeatable +0.25 kHz bias, equal to one FFT bin, because its boundary search includes the first bin at or below the peak−15 dB crossing. At 400 kHz the upstream 250 kHz local-noise window raised the adaptive threshold within the broad response, so no peak—and therefore no bandwidth—was reported. The full tested-range claim fails, while the estimator itself is precise for admitted responses up to 200 kHz.",
]];
report.getRange("A26:J30").format = {
  fill: "#E8F5F9", font: { color: "#163845" }, wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};
report.getRange("A32:J33").merge();
report.getRange("A32").values = [[
  "Scope limitation: this is a synthetic minus-15 dB heuristic characterization. It is not regulatory occupied bandwidth, modulated-signal bandwidth, receiver filter bandwidth, or calibrated RF measurement.",
]];
report.getRange("A32:J33").format = {
  font: { italic: true, color: "#64748B", size: 9 }, wrapText: true,
};

report.getRange("A1:J33").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = {
  name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 34;
report.getRange("B:C").format.columnWidth = 20;
report.getRange("D:J").format.columnWidth = 18;

const check = await workbook.inspect({
  kind: "table", range: "Report!A4:J33", include: "values,formulas",
  tableMaxRows: 30, tableMaxCols: 10, maxChars: 8000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 }, summary: "formula error scan", maxChars: 2000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Report", range: "A1:J33", scale: 1.3, format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
