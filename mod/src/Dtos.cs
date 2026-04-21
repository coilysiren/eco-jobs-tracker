namespace EcoJobsTracker;

public record SpecialtyDto(string Name, int Level, int MaxLevel);

public record PlayerSkillsDto(
    string Player,
    bool Active,
    SpecialtyDto[] Specialties);
