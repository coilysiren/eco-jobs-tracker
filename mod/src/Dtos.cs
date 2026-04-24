using System.Text.Json.Serialization;

namespace EcoJobsTracker;

public record SpecialtyDto(
    [property: JsonPropertyName("name")] string Name,
    [property: JsonPropertyName("level")] int Level,
    [property: JsonPropertyName("maxLevel")] int MaxLevel);

public record PlayerSkillsDto(
    [property: JsonPropertyName("player")] string Player,
    [property: JsonPropertyName("active")] bool Active,
    [property: JsonPropertyName("specialties")] SpecialtyDto[] Specialties);
