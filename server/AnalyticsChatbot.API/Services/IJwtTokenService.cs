using Microsoft.AspNetCore.Identity;

namespace AnalyticsChatbot.API.Services
{
    public interface IJwtTokenService
    {
        string GenerateToken(IdentityUser user, string userName);
    }
}

