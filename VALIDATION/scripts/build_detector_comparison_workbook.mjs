import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const [
  rawCsv,
  summaryCsv,
  gatesCsv,
  outputXlsx,
  previewDirectory,
] = process.argv.slice(2);

if (!rawCsv || !summaryCsv || !gatesCsv || !outputXlsx || !previewDirectory) {
  throw new Error(
    "Usage: builder <raw.csv> <summary.csv> <gates.csv> <report.xlsx> <preview-dir>",
  );
}

const workbook = await Workbook.fromCSV(
  await fs.readFile(rawCsv, "utf8"),
  { sheetName: "Raw Trials" },
);
await workbook.fromCSV(
  await fs.readFile(summaryCsv, "utf8"),
  { sheetName: "Scenario Summary" },
);
await workbook.fromCSV(
  await fs.readFile(gatesCsv, "utf8"),
  { sheetName: "Decision Gates" },
);

const raw = workbook.worksheets.getItem("Raw Trials");
const summary = workbook.worksheets.getItem("Scenario Summary");
const gates = workbook.worksheets.getItem("Decision Gates");
const report = workbook.worksheets.add("Report");

const dark = "#18232C";
const header = "#25313B";
const cyan = "#00A7C7";
const purple = "#7C5CFC";
const paleBlue = "#E8F5F9";
const text = "#17212B";
const muted = "#64748B";

raw.showGridLines = false;
raw.freezePanes.freezeRows(1);
raw.getRange("A1:S1601").format.font = { name: "Aptos", size: 8 };
raw.getRange("A1:S1").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true,
  rowHeight: 42,
};
raw.getRange("A1:S1601").format.autofitColumns();
raw.getRange("H:J").format.numberFormat = "0.000";
raw.getRange("R:R").format.numberFormat = "0.000";
raw.getRange("S:S").format.numberFormat = "0.00";

summary.showGridLines = false;
summary.freezePanes.freezeRows(1);
summary.getRange("A1:AC17").format.font = { name: "Aptos", size: 9 };
summary.getRange("A1:AC1").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF", size: 8 },
  wrapText: true,
  rowHeight: 46,
};
summary.getRange("A1:AC17").format.autofitColumns();
summary.getRange("K:R").format.numberFormat = "0.0%";
summary.getRange("S:AC").format.numberFormat = "0.000";

gates.showGridLines = false;
gates.freezePanes.freezeRows(1);
gates.getRange("A1:G7").format.font = { name: "Aptos", size: 10 };
gates.getRange("A1:G1").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF" },
  wrapText: true,
  rowHeight: 34,
};
gates.getRange("A1:G7").format.autofitColumns();
gates.getRange("B:B").format.columnWidth = 38;
gates.getRange("C:C").format.columnWidth = 52;
gates.getRange("G:G").format.columnWidth = 48;
gates.getRange("B2:C7").format.wrapText = true;
gates.getRange("G2:G7").format.wrapText = true;
gates.getRange("D2:E7").format.numberFormat = "0.0000";
gates.getRange("F2:F7").conditionalFormats.add("containsText", {
  text: "true",
  format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});
gates.getRange("F2:F7").conditionalFormats.add("containsText", {
  text: "false",
  format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

report.showGridLines = false;
report.freezePanes.freezeRows(2);
report.getRange("A1:L1").merge();
report.getRange("A1").values = [[
  "SPECTRA Phase 4 — Adaptive Detector vs OS-CFAR",
]];
report.getRange("A1:L1").format = {
  fill: dark,
  font: {
    name: "Aptos Display",
    size: 18,
    bold: true,
    color: "#FFFFFF",
  },
  rowHeight: 34,
};
report.getRange("A2:L2").merge();
report.getRange("A2").values = [[
  "DE-CMP-01 / CFG-C01 | 800 identical deterministic spectra | Synthetic eligibility review only",
]];
report.getRange("A2:L2").format = {
  fill: dark,
  font: { color: "#A8B3BD", size: 10 },
  rowHeight: 22,
};

report.getRange("A4:C7").values = [
  ["SYNTHETIC GATES PASSED", null, null],
  [null, null, null],
  ["Purpose", null, null],
  ["Eligibility for hardware validation; not production selection", null, null],
];
report.getRange("A4:C4").merge();
report.getRange("A5:C5").merge();
report.getRange("A6:C6").merge();
report.getRange("A7:C7").merge();
report.getRange("A5").formulas = [[
  '=COUNTIF(\'Decision Gates\'!F2:F7,"true")&" / "&COUNTA(\'Decision Gates\'!A2:A7)',
]];
report.getRange("A4:C7").format = {
  fill: paleBlue,
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};
report.getRange("A4").format.font = {
  bold: true,
  color: muted,
  size: 10,
};
report.getRange("A5").format.font = {
  bold: true,
  color: dark,
  size: 24,
};
report.getRange("A6").format.font = {
  bold: true,
  color: muted,
  size: 9,
};
report.getRange("A7").format.font = {
  color: text,
  size: 10,
};

report.getRange("E4:G7").values = [
  ["SHARED SPECTRA", null, null],
  [800, null, null],
  ["Detector evaluations", null, null],
  [1600, null, null],
];
report.getRange("E4:G4").merge();
report.getRange("E5:G5").merge();
report.getRange("E6:G6").merge();
report.getRange("E7:G7").merge();
report.getRange("E4:G7").format = {
  fill: "#EEF2F6",
  borders: { preset: "outside", style: "thin", color: "#CBD5E1" },
};
report.getRange("E4").format.font = {
  bold: true,
  color: muted,
  size: 10,
};
report.getRange("E5").format.font = {
  bold: true,
  color: dark,
  size: 24,
};
report.getRange("E6").format.font = {
  bold: true,
  color: muted,
  size: 9,
};
report.getRange("E7").format.font = {
  color: text,
  size: 12,
  bold: true,
};

report.getRange("I4:L7").values = [
  ["FROZEN CONFIGURATION", null, null, null],
  ["FFT", "8,192 bins", "Spacing", "250 Hz"],
  ["Trials/scenario", 100, "Seed", 3104204],
  ["Runtime limit", "100 ms", "Match", "1 FFT bin"],
];
report.getRange("I4:L4").merge();
report.getRange("I4:L7").format = {
  fill: "#EEF2F6",
  borders: { preset: "outside", style: "thin", color: "#CBD5E1" },
};
report.getRange("I4").format.font = {
  bold: true,
  color: muted,
  size: 10,
};
report.getRange("I5:L7").format.font = {
  color: text,
  size: 10,
};

report.getRange("A10:G10").values = [[
  "Gate",
  "Engineering requirement",
  "Criterion",
  "Adaptive",
  "OS-CFAR",
  "Result",
  "Interpretation",
]];
for (let index = 0; index < 6; index++) {
  const reportRow = 11 + index;
  const sourceRow = 2 + index;
  report.getRange(`A${reportRow}:G${reportRow}`).formulas = [[
    `='Decision Gates'!A${sourceRow}`,
    `='Decision Gates'!B${sourceRow}`,
    `='Decision Gates'!C${sourceRow}`,
    `='Decision Gates'!D${sourceRow}`,
    `='Decision Gates'!E${sourceRow}`,
    `=IF('Decision Gates'!F${sourceRow}="true","PASS","FAIL")`,
    `='Decision Gates'!G${sourceRow}`,
  ]];
}
report.getRange("A10:G10").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF", size: 9 },
  wrapText: true,
  rowHeight: 34,
};
report.getRange("A11:G16").format = {
  wrapText: true,
  verticalAlignment: "center",
};
report.getRange("D11:E16").format.numberFormat = "0.0000";
report.getRange("F11:F16").conditionalFormats.add("containsText", {
  text: "PASS",
  format: { fill: "#DDF6E8", font: { bold: true, color: "#087443" } },
});
report.getRange("F11:F16").conditionalFormats.add("containsText", {
  text: "FAIL",
  format: { fill: "#FDE7E9", font: { bold: true, color: "#B42335" } },
});

const scenarioLabels = [
  ["fft_edge", "FFT edge"],
  ["single_carrier", "Single carrier"],
  ["weak_beside_strong", "Weak beside strong"],
  ["multiple_carriers", "Multiple carriers"],
  ["closely_spaced_carriers", "Closely spaced"],
  ["variable_noise_floor", "Variable noise floor"],
  ["monte_carlo", "Monte Carlo"],
];

report.getRange("A19:C19").values = [[
  "Scenario",
  "Adaptive recall",
  "OS-CFAR recall",
]];
for (let index = 0; index < scenarioLabels.length; index++) {
  const row = 20 + index;
  const [scenario, label] = scenarioLabels[index];
  report.getRange(`A${row}`).values = [[label]];
  report.getRange(`B${row}:C${row}`).formulas = [[
    `=SUMIFS('Scenario Summary'!$R$2:$R$17,'Scenario Summary'!$C$2:$C$17,"adaptive",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
    `=SUMIFS('Scenario Summary'!$R$2:$R$17,'Scenario Summary'!$C$2:$C$17,"os_cfar",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
  ]];
}
report.getRange("A19:C19").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("B20:C26").format.numberFormat = "0.0%";

const recallChart = report.charts.add(
  "bar",
  report.getRange("A19:C26"),
);
recallChart.title = "Detection Recall by Scenario";
recallChart.hasLegend = true;
recallChart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 };
recallChart.setPosition("E19", "L32");

const allScenarios = [
  ["noise_only", "Noise only"],
  ...scenarioLabels,
];
report.getRange("A35:C35").values = [[
  "Scenario",
  "Adaptive Pfa",
  "OS-CFAR Pfa",
]];
for (let index = 0; index < allScenarios.length; index++) {
  const row = 36 + index;
  const [scenario, label] = allScenarios[index];
  report.getRange(`A${row}`).values = [[label]];
  report.getRange(`B${row}:C${row}`).formulas = [[
    `=SUMIFS('Scenario Summary'!$N$2:$N$17,'Scenario Summary'!$C$2:$C$17,"adaptive",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
    `=SUMIFS('Scenario Summary'!$N$2:$N$17,'Scenario Summary'!$C$2:$C$17,"os_cfar",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
  ]];
}
report.getRange("A35:C35").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("B36:C43").format.numberFormat = "0.0%";

const falseAlarmChart = report.charts.add(
  "bar",
  report.getRange("A35:C43"),
);
falseAlarmChart.title = "Frame False-Alarm Rate by Scenario";
falseAlarmChart.hasLegend = true;
falseAlarmChart.yAxis = { numberFormatCode: "0%", min: 0, max: 1 };
falseAlarmChart.setPosition("E35", "L49");

report.getRange("A52:C52").values = [[
  "Scenario",
  "Adaptive p95 (ms)",
  "OS-CFAR p95 (ms)",
]];
for (let index = 0; index < allScenarios.length; index++) {
  const row = 53 + index;
  const [scenario, label] = allScenarios[index];
  report.getRange(`A${row}`).values = [[label]];
  report.getRange(`B${row}:C${row}`).formulas = [[
    `=SUMIFS('Scenario Summary'!$U$2:$U$17,'Scenario Summary'!$C$2:$C$17,"adaptive",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
    `=SUMIFS('Scenario Summary'!$U$2:$U$17,'Scenario Summary'!$C$2:$C$17,"os_cfar",'Scenario Summary'!$D$2:$D$17,"${scenario}")`,
  ]];
}
report.getRange("A52:C52").format = {
  fill: header,
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("B53:C60").format.numberFormat = "0.000";

const runtimeChart = report.charts.add(
  "bar",
  report.getRange("A52:C60"),
);
runtimeChart.title = "95th-Percentile Detector Runtime";
runtimeChart.hasLegend = true;
runtimeChart.yAxis = { numberFormatCode: "0.000" };
runtimeChart.setPosition("E52", "L66");

report.getRange("A69:L69").merge();
report.getRange("A69").values = [["Interpretation boundary"]];
report.getRange("A69:L69").format = {
  fill: cyan,
  font: { bold: true, color: "#FFFFFF" },
};
report.getRange("A70:L73").merge();
report.getRange("A70").values = [[
  "Phase 4 compares raw peak detectors on deterministic synthetic spectra. Passing every gate would make OS-CFAR eligible for Phase 5 hardware comparison; it would not authorize production integration. Inputs are unmodulated synthetic tones and noise, FFT levels are relative rather than calibrated dBm, temporal confirmation is excluded, and runtime applies only to the recorded development environment.",
]];
report.getRange("A70:L73").format = {
  fill: paleBlue,
  font: { color: text },
  wrapText: true,
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#77B9CD" },
};

report.getRange("A1:L73").format.font = {
  name: "Aptos",
  size: 10,
};
report.getRange("A1").format.font = {
  name: "Aptos Display",
  size: 18,
  bold: true,
  color: "#FFFFFF",
};
report.getRange("A:A").format.columnWidth = 20;
report.getRange("B:B").format.columnWidth = 31;
report.getRange("C:C").format.columnWidth = 48;
report.getRange("D:F").format.columnWidth = 15;
report.getRange("G:G").format.columnWidth = 44;
report.getRange("H:L").format.columnWidth = 16;

const reportCheck = await workbook.inspect({
  kind: "table",
  range: "Report!A1:L60",
  include: "values,formulas",
  tableMaxRows: 60,
  tableMaxCols: 12,
  maxChars: 12000,
});
console.log(reportCheck.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 200 },
  summary: "final formula error scan",
  maxChars: 3000,
});
console.log(errors.ndjson);

await fs.mkdir(path.dirname(outputXlsx), { recursive: true });
await fs.mkdir(previewDirectory, { recursive: true });

const previews = [
  ["Report", "A1:L73", "report_preview.png"],
  ["Decision Gates", "A1:G7", "decision_gates_preview.png"],
  ["Scenario Summary", "A1:AC17", "scenario_summary_preview.png"],
  ["Raw Trials", "A1:S35", "raw_trials_preview.png"],
];

for (const [sheetName, range, filename] of previews) {
  const preview = await workbook.render({
    sheetName,
    range,
    scale: 1.2,
    format: "png",
  });
  await fs.writeFile(
    path.join(previewDirectory, filename),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

await (await SpreadsheetFile.exportXlsx(workbook)).save(outputXlsx);
