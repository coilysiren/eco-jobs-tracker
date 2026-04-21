# eco-jobs-tracker — C# side

Two projects share one solution (`eco-jobs-tracker.sln`):

| Project | Purpose | Runs where |
|---|---|---|
| `src/EcoJobsTracker.csproj` | The real mod. Exposes `GET /api/v1/skills` from inside the Eco server process by declaring an `[ApiController]` that Eco's ASP.NET Core host picks up via `AddApplicationPart`. | Eco dedicated server, after `dotnet build -c Release` and dropping the resulting DLL into `Server/Mods/<Name>/`. |
| `shell/EcoJobsTracker.Shell.csproj` | Standalone ASP.NET Core harness. Same route, same DTOs, mock data. Lets the Python tracker iterate against a real C# HTTP server without booting Eco. | `localhost:5100`, launched by `make run-shell` from the repo root. |

DTOs (`src/Dtos.cs`) are shared — the shell project `<Compile Include>`s the file, so any change to the shape propagates to both.

## Local harness

```sh
make run-shell       # -> http://localhost:5100/api/v1/skills
```

## Building the real mod

```sh
cd mod
dotnet build src/EcoJobsTracker.csproj -c Release
# -> mod/src/bin/Release/net10.0/EcoJobsTracker.dll
```

Copy the DLL into the Eco server's `Server/Mods/EcoJobsTracker/` directory and restart the server. Eco's `ModKitPlugin` discovers mod DLLs on boot and registers their MVC application parts automatically.

## Why not UserCode?

Eco does auto-compile `.cs` files dropped into `Server/Mods/UserCode/`, but pre-compiling via `dotnet build` gives us:

- Real IDE support (IntelliSense, nullable annotations, refactors).
- A standalone build that Eco doesn't have to recompile on every server restart.
- Shared type definitions with the shell harness.

Both approaches are supported by Eco; we're choosing the compiled path.
