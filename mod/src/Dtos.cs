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

public record PlayerSkillsDto(
    [property: JsonPropertyName("player"), JsonProperty("player")] string Player,
    [property: JsonPropertyName("active"), JsonProperty("active")] bool Active,
    [property: JsonPropertyName("specialties"), JsonProperty("specialties")] SpecialtyDto[] Specialties);
