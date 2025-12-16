using OfficeOpenXml;
using AnalyticsChatbot.API.Models;

namespace AnalyticsChatbot.API.Utils;

public static class ExcelHelper
{
    static ExcelHelper()
    {
        // Set EPPlus license context
        ExcelPackage.LicenseContext = LicenseContext.NonCommercial;
    }

    public static byte[] GenerateExcel(ReportResult reportData)
    {
        using var package = new ExcelPackage();
        var worksheet = package.Workbook.Worksheets.Add("Report");

        if (reportData.Columns == null || reportData.Rows == null)
        {
            throw new ArgumentException("Report data must have columns and rows");
        }

        // Add headers
        for (int i = 0; i < reportData.Columns.Count; i++)
        {
            worksheet.Cells[1, i + 1].Value = reportData.Columns[i];
            worksheet.Cells[1, i + 1].Style.Font.Bold = true;
        }

        // Add data rows
        for (int rowIndex = 0; rowIndex < reportData.Rows.Count; rowIndex++)
        {
            var row = reportData.Rows[rowIndex];
            for (int colIndex = 0; colIndex < reportData.Columns.Count; colIndex++)
            {
                var columnName = reportData.Columns[colIndex];
                if (row.ContainsKey(columnName))
                {
                    var value = row[columnName];
                    worksheet.Cells[rowIndex + 2, colIndex + 1].Value = 
                        value == DBNull.Value ? null : value;
                }
            }
        }

        // Auto-fit columns
        worksheet.Cells[worksheet.Dimension.Address].AutoFitColumns();

        return package.GetAsByteArray();
    }
}
