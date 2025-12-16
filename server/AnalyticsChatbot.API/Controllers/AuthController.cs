using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Identity;
using Microsoft.AspNetCore.Authorization;
using AnalyticsChatbot.API.Models;
using AnalyticsChatbot.API.Services;
using System.Security.Claims;

namespace AnalyticsChatbot.API.Controllers
{
    [ApiController]
    [Route("api/[controller]")]
    public class AuthController : ControllerBase
    {
        private readonly UserManager<IdentityUser> _userManager;
        private readonly SignInManager<IdentityUser> _signInManager;
        private readonly IJwtTokenService _jwtTokenService;
        private readonly ILogger<AuthController> _logger;

        public AuthController(
            UserManager<IdentityUser> userManager, 
            SignInManager<IdentityUser> signInManager,
            IJwtTokenService jwtTokenService,
            ILogger<AuthController> logger)
        {
            _userManager = userManager;
            _signInManager = signInManager;
            _jwtTokenService = jwtTokenService;
            _logger = logger;
        }

        [HttpPost("register")]
        public async Task<IActionResult> Register([FromBody] RegisterRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { message = "Invalid registration data", errors = ModelState.Values.SelectMany(v => v.Errors.Select(e => e.ErrorMessage)) });
            }

            try
            {
                // Check if user already exists
                var existingUser = await _userManager.FindByEmailAsync(request.Email);
                if (existingUser != null)
                {
                    return BadRequest(new { message = "User with this email already exists" });
                }

                // Create new user
                var user = new IdentityUser 
                { 
                    UserName = request.Email,
                    Email = request.Email
                };

                var result = await _userManager.CreateAsync(user, request.Password);
                
                if (result.Succeeded)
                {
                    _logger.LogInformation("User {Email} registered successfully", request.Email);
                    
                    // Add user name as a claim
                    await _userManager.AddClaimAsync(user, new Claim("Name", request.Name));
                    
                    // Generate JWT token
                    var token = _jwtTokenService.GenerateToken(user, request.Name);
                    
                    var response = new AuthResponse
                    {
                        Token = token,
                        User = new UserDto
                        {
                            Id = user.Id,
                            Email = user.Email!,
                            Name = request.Name,
                            Role = "User"
                        }
                    };

                    return Ok(response);
                }

                var errors = string.Join(", ", result.Errors.Select(e => e.Description));
                return BadRequest(new { message = "Registration failed", errors = errors });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during user registration");
                return StatusCode(500, new { message = "An error occurred during registration. Please try again." });
            }
        }

        [HttpPost("login")]
        public async Task<IActionResult> Login([FromBody] LoginRequest request)
        {
            if (!ModelState.IsValid)
            {
                return BadRequest(new { message = "Invalid login data", errors = ModelState.Values.SelectMany(v => v.Errors.Select(e => e.ErrorMessage)) });
            }

            try
            {
                // Find user by email
                var user = await _userManager.FindByEmailAsync(request.Email);
                if (user == null)
                {
                    return Unauthorized(new { message = "Invalid email or password" });
                }

                // Check password
                var result = await _signInManager.CheckPasswordSignInAsync(user, request.Password, lockoutOnFailure: false);
                
                if (result.Succeeded)
                {
                    _logger.LogInformation("User {Email} logged in successfully", request.Email);
                    
                    // Get user name from claims
                    var claims = await _userManager.GetClaimsAsync(user);
                    var nameClaim = claims.FirstOrDefault(c => c.Type == "Name");
                    var userName = nameClaim?.Value ?? user.Email ?? "User";
                    
                    // Generate JWT token
                    var token = _jwtTokenService.GenerateToken(user, userName);
                    
                    var response = new AuthResponse
                    {
                        Token = token,
                        User = new UserDto
                        {
                            Id = user.Id,
                            Email = user.Email!,
                            Name = userName,
                            Role = "User"
                        }
                    };

                    return Ok(response);
                }

                if (result.IsLockedOut)
                {
                    return BadRequest(new { message = "Account is locked out. Please try again later." });
                }

                return Unauthorized(new { message = "Invalid email or password" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during user login");
                return StatusCode(500, new { message = "An error occurred during login. Please try again." });
            }
        }

        [HttpPost("logout")]
        [Authorize]
        public async Task<IActionResult> Logout()
        {
            try
            {
                await _signInManager.SignOutAsync();
                _logger.LogInformation("User logged out successfully");
                return Ok(new { message = "Logout successful" });
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error during user logout");
                return StatusCode(500, new { message = "An error occurred during logout" });
            }
        }

        [HttpPost("refresh")]
        [Authorize]
        public async Task<IActionResult> RefreshToken()
        {
            try
            {
                var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
                if (string.IsNullOrEmpty(userId))
                {
                    return Unauthorized(new { message = "Invalid token" });
                }

                var user = await _userManager.FindByIdAsync(userId);
                if (user == null)
                {
                    return Unauthorized(new { message = "User not found" });
                }

                // Get user name from claims
                var claims = await _userManager.GetClaimsAsync(user);
                var nameClaim = claims.FirstOrDefault(c => c.Type == "Name");
                var userName = nameClaim?.Value ?? user.Email ?? "User";

                // Generate new token
                var token = _jwtTokenService.GenerateToken(user, userName);

                var response = new AuthResponse
                {
                    Token = token,
                    User = new UserDto
                    {
                        Id = user.Id,
                        Email = user.Email!,
                        Name = userName,
                        Role = "User"
                    }
                };

                return Ok(response);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error refreshing token");
                return StatusCode(500, new { message = "An error occurred while refreshing token" });
            }
        }

        [HttpGet("me")]
        [Authorize]
        public async Task<IActionResult> GetCurrentUser()
        {
            try
            {
                var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
                if (string.IsNullOrEmpty(userId))
                {
                    return Unauthorized(new { message = "Invalid token" });
                }

                var user = await _userManager.FindByIdAsync(userId);
                if (user == null)
                {
                    return NotFound(new { message = "User not found" });
                }

                // Get user name from claims
                var claims = await _userManager.GetClaimsAsync(user);
                var nameClaim = claims.FirstOrDefault(c => c.Type == "Name");
                var userName = nameClaim?.Value ?? user.Email ?? "User";

                var userDto = new UserDto
                {
                    Id = user.Id,
                    Email = user.Email!,
                    Name = userName,
                    Role = "User"
                };

                return Ok(userDto);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error getting current user");
                return StatusCode(500, new { message = "An error occurred while retrieving user information" });
            }
        }
    }
}
