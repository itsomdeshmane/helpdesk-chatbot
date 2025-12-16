using AnalyticsChatbot.API.Models;
using AnalyticsChatbot.API.Utils;

namespace AnalyticsChatbot.API.Services;

public interface IReportService
{
    Task<byte[]> GenerateExcelReportAsync(ReportResult reportData);
    Task<byte[]> GeneratePdfReportAsync(ReportResult reportData);
}

public class ReportService : IReportService
{
    private readonly ILogger<ReportService> _logger;

    public ReportService(ILogger<ReportService> logger)
    {
        _logger = logger;
    }

    public async Task<byte[]> GenerateExcelReportAsync(ReportResult reportData)
    {
        try
        {
            _logger.LogInformation("Generating Excel report");
            return await Task.Run(() => ExcelHelper.GenerateExcel(reportData));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating Excel report");
            throw;
        }
    }

    public async Task<byte[]> GeneratePdfReportAsync(ReportResult reportData)
    {
        try
        {
            _logger.LogInformation("Generating PDF report");
            return await Task.Run(() => PdfHelper.GeneratePdf(reportData));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating PDF report");
            throw;
        }
    }
}
