using EcoJobsTracker.Shell;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers();

var app = builder.Build();
app.MapGet("/healthz", () => Results.Ok(new { ok = true }));
app.MapControllers();

var port = Environment.GetEnvironmentVariable("PORT") ?? "5100";
app.Run($"http://0.0.0.0:{port}");
