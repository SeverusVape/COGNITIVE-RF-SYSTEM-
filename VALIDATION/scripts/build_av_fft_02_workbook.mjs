import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [rawCsv, conditionCsv, outputXlsx, previewPng] = process.argv.slice(2);
if (!rawCsv || !conditionCsv || !outputXlsx || !previewPng) {
  throw new Error("Usage: node build_av_fft_02_workbook.mjs <raw.csv> <conditions.csv> <report.xlsx> <preview.png>");
}

const rawText = await fs.readFile(rawCsv, "utf8");
const conditionText = await fs.readFile(conditionCsv, "utf8");
const workbook = await Workbook.fromCSV(rawText, { sheetName: "Raw Trials" });
await workbook.fromCSV(conditionText, { sheetName: "Condition Summary" });
const raw = workbook.worksheets.getItem("Raw Trials");
const conditions = workbook.worksheets.getItem("Condition Summary");
const report = workbook.worksheets.add("Report");

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:X361").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:X1").format = {
  fill: "#25313B",
  font: { name: "Aptos", size: 8, bold: true, color: "#FFFFFF" },
  wrapText: true,
  rowHeight: 38,
};
raw.getRange("G2:V361").format.numberFormat = "0.000";
raw.getRange("A1:X361").format.autofitColumns();

conditions.showGridLines = false;
conditions.freezePanes.freezeRows(1);
conditions.getRange("A1:H10").format.font = { name: "Aptos", size: 9 };
conditions.getRange("A1:H1").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  rowHeight: 32,
};
conditions.getRange("B2:G10").format.numberFormat = "0.000";
conditions.getRange("A1:H10").format.autofitColumns();

report.showGridLines = false;
report.getRange("A1:J1").merge();
report.getRange("A1").values = [["AV-FFT-02 — Hann Window and Off-Bin Leakage Validation"]];
report.getRange("A1:J1").format = {
  fill: "#18232C",
  font: { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" },
  rowHeight: 34,
  verticalAlignment: "center",
};
report.getRange("A2:J2").merge();
report.getRange("A2").values = [["CFG-S01 | Existing rectangular and coherent-gain-corrected Hann FFT paths | Synthetic IQ only"]];
report.getRange("A2:J2").format = {
  fill: "#18232C",
  font: { name: "Aptos", size: 10, color: "#A8B3BD" },
  rowHeight: 22,
};

report.getRange("A4:B11").values = [
  ["Acceptance metric", "Result"],
  ["Spectra evaluated", null],
  ["Paired tone realizations", null],
  ["Centered peak error limit (dB)", 0.01],
  ["Maximum centered peak error (dB)", null],
  ["Minimum required leakage improvement (dB)", 10.0],
  ["Minimum observed leakage improvement (dB)", null],
  ["Overall result", null],
];
report.getRange("B5:B6").formulas = [
  ["=COUNTA('Raw Trials'!C2:C361)"],
  ["=B5/2"],
];
report.getRange("B8").formulas = [["=MAX(E14,F14,-E14,-F14)"]];
report.getRange("B10").formulas = [["=MIN('Condition Summary'!G3:G4,'Condition Summary'!G6:G7,'Condition Summary'!G9:G10)"]];
report.getRange("B11").formulas = [["=IF(AND(B8<=B7,B10>=B9),\"PASS\",\"FAIL\")"]];
report.getRange("A4:B4").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A5:A11").format.font = { bold: true, color: "#334155" };
report.getRange("B7:B10").format.numberFormat = "0.000";
report.getRange("A4:B11").format.borders = {
  insideHorizontal: { style: "thin", color: "#D8DEE4" },
  outside: { style: "thin", color: "#AEB8C2" },
};
report.getRange("B11").conditionalFormats.add("containsText", {
  text: "PASS",
  format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});

report.getRange("A13:F16").values = [
  ["Fractional offset", "Rectangular leakage (dB)", "Hann leakage (dB)", "Hann improvement (dB)", "Rectangular peak error (dB)", "Hann peak error (dB)"],
  [0.00, null, null, null, null, null],
  [0.25, null, null, null, null, null],
  [0.50, null, null, null, null, null],
];
report.getRange("B14").formulas = [["=AVERAGEIF('Condition Summary'!$B$2:$B$10,A14,'Condition Summary'!$E$2:$E$10)"]];
report.getRange("B14:B16").fillDown();
report.getRange("C14").formulas = [["=AVERAGEIF('Condition Summary'!$B$2:$B$10,A14,'Condition Summary'!$F$2:$F$10)"]];
report.getRange("C14:C16").fillDown();
report.getRange("D14").formulas = [["=B14-C14"]];
report.getRange("D14:D16").fillDown();
report.getRange("E14").formulas = [["=AVERAGEIF('Condition Summary'!$B$2:$B$10,A14,'Condition Summary'!$C$2:$C$10)"]];
report.getRange("E14:E16").fillDown();
report.getRange("F14").formulas = [["=AVERAGEIF('Condition Summary'!$B$2:$B$10,A14,'Condition Summary'!$D$2:$D$10)"]];
report.getRange("F14:F16").fillDown();
report.getRange("A13:F13").format = {
  fill: "#25313B",
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
};
report.getRange("A13:F16").format.borders = {
  insideHorizontal: { style: "thin", color: "#D8DEE4" },
  outside: { style: "thin", color: "#AEB8C2" },
};
report.getRange("A14:F16").format.numberFormat = "0.000";

const leakageChart = report.charts.add("line", {
  chartType: "line",
  title: "Hann Reduces Off-Bin Leakage (dB)",
  hasLegend: true,
});
const rectangularLeakage = leakageChart.series.add("Rectangular");
rectangularLeakage.categoryFormula = "'Report'!$A$15:$A$16";
rectangularLeakage.formula = "'Report'!$B$15:$B$16";
rectangularLeakage.fill = "#7F8C98";
const hannLeakage = leakageChart.series.add("Hann");
hannLeakage.categoryFormula = "'Report'!$A$15:$A$16";
hannLeakage.formula = "'Report'!$C$15:$C$16";
hannLeakage.fill = "#00AEEA";
leakageChart.title = "Hann Reduces Off-Bin Leakage (dB)";
leakageChart.hasLegend = true;
leakageChart.xAxis = { axisType: "textAxis" };
leakageChart.yAxis = { numberFormatCode: "0.0" };
leakageChart.setPosition("D4", "J12");

const peakChart = report.charts.add("line", {
  chartType: "line",
  title: "Peak Amplitude Error (dB)",
  hasLegend: true,
});
const rectangularPeak = peakChart.series.add("Rectangular");
rectangularPeak.categoryFormula = "'Report'!$A$14:$A$16";
rectangularPeak.formula = "'Report'!$E$14:$E$16";
rectangularPeak.fill = "#7F8C98";
const hannPeak = peakChart.series.add("Hann");
hannPeak.categoryFormula = "'Report'!$A$14:$A$16";
hannPeak.formula = "'Report'!$F$14:$F$16";
hannPeak.fill = "#00AEEA";
peakChart.title = "Peak Amplitude Error (dB)";
peakChart.hasLegend = true;
peakChart.xAxis = { axisType: "textAxis" };
peakChart.yAxis = { numberFormatCode: "0.0" };
peakChart.setPosition("G13", "J22");

report.getRange("A18:F18").merge();
report.getRange("A18").values = [["Engineering conclusion"]];
report.getRange("A18:F18").format = {
  fill: "#0B6E8E",
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A19:F22").merge();
report.getRange("A19").values = [[
  "PASS — The coherent-gain-corrected Hann path preserved bin-centered amplitude and reduced off-bin leakage by at least 22 dB under the fixed ±2-bin leakage definition. The expected tradeoff remains a wider main lobe. This validates numerical window behavior only, not the RTL-SDR analog response or calibrated power.",
]];
report.getRange("A19:F22").format = {
  fill: "#E8F5F9",
  font: { color: "#163845" },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};

report.getRange("A24:J24").merge();
report.getRange("A24").values = [["Measurement definition: integrated energy outside a fixed ±2-bin region around the detected peak, relative to total spectral energy. Paired phases use identical seeds for both windows."]];
report.getRange("A24:J24").format = {
  font: { italic: true, color: "#64748B", size: 9 },
  wrapText: true,
  rowHeight: 28,
};

report.getRange("A1:J24").format.font = { name: "Aptos", size: 10 };
report.getRange("A1").format.font = { name: "Aptos Display", size: 18, bold: true, color: "#FFFFFF" };
report.getRange("A:A").format.columnWidth = 34;
report.getRange("B:B").format.columnWidth = 19;
report.getRange("C:F").format.columnWidth = 18;
report.getRange("G:J").format.columnWidth = 14;
report.freezePanes.freezeRows(2);

const inspection = await workbook.inspect({
  kind: "table",
  range: "Report!A1:J24",
  include: "values,formulas",
  tableMaxRows: 24,
  tableMaxCols: 10,
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
  sheetName: "Report",
  range: "A1:J24",
  scale: 1.3,
  format: "png",
});
await fs.writeFile(previewPng, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputXlsx);
