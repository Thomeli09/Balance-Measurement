"""Create both Markdown and LaTeX specimen summaries from a saved dataset."""

from balance_measurement.analysis import summarize
from balance_measurement.domain import Specimen
from balance_measurement.reporting import latex_report, markdown_report, save_report
from balance_measurement.storage import load_measurements

if __name__ == "__main__":
    summary = summarize(load_measurements("measurements.csv"))
    sample = Specimen(specimen_id="S001", project="Carbonation", material="concrete")
    save_report(markdown_report(sample, summary), "report.md")
    save_report(latex_report(sample, summary), "report.tex")
