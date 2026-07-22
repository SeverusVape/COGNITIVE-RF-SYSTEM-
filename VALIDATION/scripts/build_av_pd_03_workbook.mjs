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
  await fs.readFile(summaryCsv, "utf8"), { sheetName: "Spacing Summary" },
);
const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("Spacing Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:AE1801").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:AE1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true, rowHeight: 42,
};
raw.getRange("A1:AE1801").format.autofitColumns();

summary.showGridLines = false;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:P37").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:P1").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 42,
};
summary.getRange("E2:H37").format.numberFormat = "0.0%";
summary.getRange("I2:K37").format.numberFormat = "0.00";
summary.getRange("A1:P37").format.autofitColumns();

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-PD-03 — Two-Tone Resolution Validation"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [[
  "CFG-S01 | Unchanged Hann FFT and adaptive peak detector | 1,800 deterministic trials",
]];
report.getRange("A2:J2").format = {
  fill: "#18232C", font: { color: "#A8B3BD" }, rowHeight: 22,
};

report.getRange("A4:B13").values = [
  ["Validation metric", "Result"],
  ["Total trials", 1800],
  ["Configured minimum spacing", 75.0],
  ["FFT bin spacing (Hz)", 250.0],
  ["Min equal-tone P(resolve), ≥75 kHz", null],
  ["Required minimum", 0.95],
  ["Max equal-tone P(resolve), <75 kHz", null],
  ["Allowed maximum", 0.05],
  ["Maximum p95 frequency error (Hz)", null],
  ["Overall result", null],
];
report.getRange("B8").formulas = [["=MIN('Spacing Summary'!E7:E13)"]];
report.getRange("B10").formulas = [["=MAX('Spacing Summary'!E2:E6)"]];
report.getRange("B12").formulas = [["=MAX('Spacing Summary'!K7:K13)"]];
report.getRange("B13").formulas = [["=IF(AND(B8>=B9,B10<=B11,B12<=B7),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A13").format.font = { bold: true, color: "#334155" };
report.getRange("B6").format.numberFormat = "0.0 \"kHz\"";
report.getRange("B8:B11").format.numberFormat = "0.0%";
report.getRange("B12").format.numberFormat = "0.0";
report.getRange("B13").conditionalFormats.add("containsText", {
  text: "PASS", format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});
report.getRange("B13").conditionalFormats.add("containsText", {
  text: "FAIL", format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.getRange("A15:D27").values = [
  ["Separation (kHz)", "Equal amplitude", "Tone 2 −6 dB", "Tone 2 −12 dB"],
  ...Array.from({ length: 12 }, (_, index) => [
    null, null, null, null,
  ]),
];
for (let index = 0; index < 12; index++) {
  const row = 16 + index;
  const equalSource = 2 + index;
  const minus6Source = 14 + index;
  const minus12Source = 26 + index;
  report.getRange(`A${row}:D${row}`).formulas = [[
    `=VALUE('Spacing Summary'!A${equalSource})`,
    `=VALUE('Spacing Summary'!E${equalSource})`,
    `=VALUE('Spacing Summary'!E${minus6Source})`,
    `=VALUE('Spacing Summary'!E${minus12Source})`,
  ]];
}
report.getRange("A15:D15").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" },
  wrapText: true, rowHeight: 34,
};
report.getRange("B16:D27").format.numberFormat = "0%";

const chart = report.charts.add("line", report.getRange("A15:D27"));
chart.title = "Resolution Probability vs Tone Separation";
chart.hasLegend = true;
chart.xAxis = { axisType: "textAxis" };
chart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 };
chart.setPosition("D4", "J14");

report.getRange("F16:H20").values = [
  ["Relative level", "Validated boundary", "Minimum probability at boundary"],
  ["0 dB", 75.0, null],
  ["−6 dB", 75.0, null],
  ["−12 dB", 75.0, null],
  ["Detector spacing setting", 75.0, null],
];
report.getRange("H17").formulas = [["='Spacing Summary'!E7"]];
report.getRange("H18").formulas = [["='Spacing Summary'!E19"]];
report.getRange("H19").formulas = [["='Spacing Summary'!E31"]];
report.getRange("F16:H16").format = {
  fill: "#25313B", font: { bold: true, color: "#FFFFFF" }, wrapText: true,
};
report.getRange("G17:G20").format.numberFormat = "0.0 \"kHz\"";
report.getRange("H17:H19").format.numberFormat = "0%";

report.getRange("A30:J30").merge();
report.getRange("A30").values = [["Engineering conclusion"]];
report.getRange("A30:J30").format = {
  fill: "#0B6E8E", font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A31:J34").merge();
report.getRange("A31").values = [[
  "The configured detector exhibits a sharp synthetic two-tone boundary at 75 kHz. Equal-amplitude tones were unresolved in every trial at 74 kHz and below and resolved in every trial from 75 kHz upward. With the secondary tone reduced by 6 or 12 dB, resolution was 98% at exactly 75 kHz and 100% from 76 kHz upward. Below the spacing limit the detector generally retained one response; unequal-amplitude cases consistently retained the stronger tone. Resolved frequency errors remained below one 250 Hz FFT bin.",
]];
report.getRange("A31:J34").format = {
  fill: "#E8F5F9", font: { color: "#163845" }, wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};
report.getRange("A36:J36").merge();
report.getRange("A36").values = [[
  "Scope: deterministic unmodulated synthetic tones at fixed SNR. This does not establish hardware selectivity, modulated-signal resolution, temporal-confirmation behavior, or calibrated dynamic range.",
]];
report.getRange("A36:J36").format = {
  font: { italic: true, color: "#64748B", size: 9 }, wrapText: true, rowHeight: 30,
};

report.getRange("A1:J36").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = {
  name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 32;
report.getRange("B:D").format.columnWidth = 19;
report.getRange("E:J").format.columnWidth = 18;

const check = await workbook.inspect({
  kind: "table", range: "Report!A4:H27", include: "values,formulas",
  tableMaxRows: 24, tableMaxCols: 8, maxChars: 7000,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 }, summary: "formula error scan", maxChars: 2000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
const preview = await workbook.render({
  sheetName: "Report", range: "A1:J36", scale: 1.3, format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
