using System.Text.Json.Serialization;
using Newtonsoft.Json;

namespace EcoJobsTracker;

// Both attribute sets present so the DTOs serialize as camelCase under either
// System.Text.Json (shell harness default in recent ASP.NET) or Newtonsoft.Json
// (Eco's own web pipeline).
public record SpecialtyDto(
    [property: JsonPropertyName("name"), JsonProperty("name")] string Name,
    [property: JsonPropertyName("level"), JsonProperty("level")] int Level,
    [property: JsonPropertyName("maxLevel"), JsonProperty("maxLevel")] int MaxLevel);

// lastSeen is an ISO-8601 UTC timestamp ("yyyy-MM-ddTHH:mm:ssZ") or null if
// the player has never logged in. The Python tracker derives "active" by
// comparing this against now() - ACTIVE_WINDOW_DAYS, so the mod stays
// agnostic to what window the dashboard cares about.
public record PlayerSkillsDto(
    [property: JsonPropertyName("player"), JsonProperty("player")] string Player,
    [property: JsonPropertyName("lastSeen"), JsonProperty("lastSeen")] string? LastSeen,
    [property: JsonPropertyName("specialties"), JsonProperty("specialties")] SpecialtyDto[] Specialties);
