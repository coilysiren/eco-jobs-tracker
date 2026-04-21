using EcoJobsTracker;
using Microsoft.AspNetCore.Mvc;

namespace EcoJobsTracker.Shell;

// Serves the same route as the real mod with canned data, so the Python
// tracker can iterate against a live C# HTTP server without booting Eco.
[ApiController]
[Route("api/v1/skills")]
public class MockSkillsController : ControllerBase
{
    private static readonly PlayerSkillsDto[] Mock =
    {
        new("coilysiren", true, new[]
        {
            new SpecialtyDto("Basic Carpentry", 5, 7),
            new SpecialtyDto("Advanced Carpentry", 3, 7),
            new SpecialtyDto("Furniture Making", 2, 7),
        }),
        new("ekans", true, new[]
        {
            new SpecialtyDto("Basic Carpentry", 4, 7),
            new SpecialtyDto("Lumber", 1, 7),
            new SpecialtyDto("Mining", 6, 7),
        }),
        new("redwood", false, new[]
        {
            new SpecialtyDto("Glassworking", 5, 7),
            new SpecialtyDto("Basic Masonry", 2, 7),
            new SpecialtyDto("Pottery", 3, 7),
        }),
        new("salt", true, new[]
        {
            new SpecialtyDto("Campfire Cooking", 4, 7),
            new SpecialtyDto("Baking", 2, 7),
            new SpecialtyDto("Farming", 5, 7),
            new SpecialtyDto("Gardening", 3, 7),
        }),
        new("hammerhand", true, new[]
        {
            new SpecialtyDto("Basic Masonry", 5, 7),
            new SpecialtyDto("Brick Making", 4, 7),
            new SpecialtyDto("Advanced Masonry", 3, 7),
        }),
    };

    [HttpGet]
    public IEnumerable<PlayerSkillsDto> Get() => Mock;
}
