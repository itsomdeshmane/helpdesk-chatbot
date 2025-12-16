using iText.Kernel.Pdf;
using iText.Layout;
using iText.Layout.Element;
using iText.Layout.Properties;
using AnalyticsChatbot.API.Models;

namespace AnalyticsChatbot.API.Utils;

public static class PdfHelper
{
    public static byte[] GeneratePdf(ReportResult reportData)
    {
        using var memoryStream = new MemoryStream();
        using var writer = new PdfWriter(memoryStream);
        using var pdf = new PdfDocument(writer);
        using var document = new Document(pdf);

        if (reportData.Columns == null || reportData.Rows == null)
        {
            throw new ArgumentException("Report data must have columns and rows");
        }

        // Add title
        document.Add(new Paragraph("Analytics Report")
            .SetTextAlignment(TextAlignment.CENTER)
            .SetFontSize(20)
            .SetBold());

        document.Add(new Paragraph($"Generated: {DateTime.Now:yyyy-MM-dd HH:mm:ss}")
            .SetTextAlignment(TextAlignment.CENTER)
            .SetFontSize(10));

        document.Add(new Paragraph("\n"));

        // Create table
        var table = new Table(reportData.Columns.Count);
        table.SetWidth(UnitValue.CreatePercentValue(100));

        // Add headers
        foreach (var column in reportData.Columns)
        {
            table.AddHeaderCell(new Cell()
                .Add(new Paragraph(column))
                .SetBold()
                .SetTextAlignment(TextAlignment.CENTER));
        }

        // Add data rows
        foreach (var row in reportData.Rows)
        {
            foreach (var column in reportData.Columns)
            {
                var value = row.ContainsKey(column) && row[column] != DBNull.Value
                    ? row[column]?.ToString() ?? ""
                    : "";
                
                table.AddCell(new Cell()
                    .Add(new Paragraph(value))
                    .SetTextAlignment(TextAlignment.LEFT));
            }
        }

        document.Add(table);
        document.Close();

        return memoryStream.ToArray();
    }
}
