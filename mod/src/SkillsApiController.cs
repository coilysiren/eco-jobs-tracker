using Eco.Gameplay.Players;
using Microsoft.AspNetCore.Mvc;

namespace EcoJobsTracker;

// Lives inside the Eco server process. Eco's ASP.NET Core host picks up
// [ApiController] classes from mod assemblies via AddApplicationPart.
[ApiController]
[Route("api/v1/skills")]
public class SkillsApiController : ControllerBase
{
    [HttpGet]
    public IEnumerable<PlayerSkillsDto> Get()
    {
        return UserManager.Users.Select(user =>
        {
            var specialties = user.Skillset.Skills
                .Where(skill => skill.Level > 0 && skill.IsSpecialty)
                .Select(skill => new SpecialtyDto(
                    skill.DisplayName,
                    skill.Level,
                    skill.MaxLevel))
                .ToArray();

            return new PlayerSkillsDto(user.Name, user.LoggedIn, specialties);
        });
    }
}
