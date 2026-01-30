package services

import (
	"errors"
	"time"

	"user_management/internal/models"
	"user_management/internal/repositories"

	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type UserService struct {
	userRepo   *repositories.UserRepository
	tenantRepo *repositories.TenantRepository
}

func NewUserService(userRepo *repositories.UserRepository, tenantRepo *repositories.TenantRepository) *UserService {
	return &UserService{
		userRepo:   userRepo,
		tenantRepo: tenantRepo,
	}
}

func (s *UserService) RegisterUser(email, password string, tenantDomain string) (*models.User, error) {
	// Find or create tenant
	tenant, err := s.tenantRepo.FindTenantByDomain(tenantDomain)
	if err != nil {
		tenant = &models.Tenant{
			ID:     uuid.New(),
			Domain: tenantDomain,
			Status: models.TenantProvisioning,
		}
		if err := s.tenantRepo.CreateTenant(tenant); err != nil {
			return nil, err
		}
	}

	// Check if user already exists
	existingUser, err := s.userRepo.FindUserByEmail(email)
	if err != nil {
		return nil, err
	}
	if existingUser != nil {
		return nil, errors.New("user already exists")
	}

	// Hash password
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return nil, err
	}

	// Create user
	user := &models.User{
		ID:             uuid.New(),
		Email:          email,
		PasswordHash:   string(hashedPassword),
		TenantID:       tenant.ID,
		Status:         models.UserActive,
		ProviderType:   "local",
		LastLogin:      time.Now(),
	}

	if err := s.userRepo.CreateUser(user); err != nil {
		return nil, err
	}

	return user, nil
}

func (s *UserService) AssignUserRole(userID uuid.UUID, roleName string) error {
	// Simplified role assignment logic
	return nil
}