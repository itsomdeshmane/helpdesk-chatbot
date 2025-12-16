using Microsoft.AspNetCore.Mvc;
using AnalyticsChatbot.API.Models;
using AnalyticsChatbot.API.Services;

namespace AnalyticsChatbot.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class ReportController : ControllerBase
{
    private readonly IReportService _reportService;
    private readonly ILogger<ReportController> _logger;

    public ReportController(
        IReportService reportService,
        ILogger<ReportController> logger)
    {
        _reportService = reportService;
        _logger = logger;
    }

    [HttpPost("export/excel")]
    public async Task<IActionResult> ExportToExcel([FromBody] ReportResult reportData)
    {
        try
        {
            if (reportData?.Rows == null || !reportData.Rows.Any())
            {
                return BadRequest("No data to export");
            }

            var excelBytes = await _reportService.GenerateExcelReportAsync(reportData);
            
            return File(
                excelBytes,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                $"report_{DateTime.Now:yyyyMMddHHmmss}.xlsx");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating Excel report");
            return StatusCode(500, $"Error generating report: {ex.Message}");
        }
    }

    [HttpPost("export/pdf")]
    public async Task<IActionResult> ExportToPdf([FromBody] ReportResult reportData)
    {
        try
        {
            if (reportData?.Rows == null || !reportData.Rows.Any())
            {
                return BadRequest("No data to export");
            }

            var pdfBytes = await _reportService.GeneratePdfReportAsync(reportData);
            
            return File(
                pdfBytes,
                "application/pdf",
                $"report_{DateTime.Now:yyyyMMddHHmmss}.pdf");
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error generating PDF report");
            return StatusCode(500, $"Error generating report: {ex.Message}");
        }
    }
}
