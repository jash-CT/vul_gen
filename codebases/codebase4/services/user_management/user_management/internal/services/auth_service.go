package services

import (
	"errors"
	"time"

	"user_management/internal/models"
	"user_management/internal/repositories"

	"github.com/golang-jwt/jwt/v5"
	"github.com/google/uuid"
	"golang.org/x/crypto/bcrypt"
)

type AuthenticationService struct {
	userRepo *repositories.UserRepository
	jwtSecret []byte
}

func NewAuthenticationService(userRepo *repositories.UserRepository, jwtSecret []byte) *AuthenticationService {
	return &AuthenticationService{
		userRepo:  userRepo,
		jwtSecret: jwtSecret,
	}
}

func (s *AuthenticationService) Authenticate(email, password string) (*models.User, string, error) {
	user, err := s.userRepo.FindUserByEmail(email)
	if err != nil || user == nil {
		return nil, "", errors.New("invalid credentials")
	}

	// Check password
	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(password)); err != nil {
		return nil, "", errors.New("invalid credentials")
	}

	// Generate JWT
	token, err := s.generateJWT(user)
	if err != nil {
		return nil, "", err
	}

	// Update last login
	user.LastLogin = time.Now()
	s.userRepo.UpdateUser(user)

	return user, token, nil
}

func (s *AuthenticationService) generateJWT(user *models.User) (string, error) {
	claims := jwt.MapClaims{
		"sub":       user.ID.String(),
		"email":     user.Email,
		"tenant_id": user.TenantID.String(),
		"exp":       time.Now().Add(time.Hour * 24).Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString(s.jwtSecret)
}

func (s *AuthenticationService) ValidateJWT(tokenString string) (*models.User, error) {
	token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
		return s.jwtSecret, nil
	})

	if err != nil {
		return nil, err
	}

	if claims, ok := token.Claims.(jwt.MapClaims); ok && token.Valid {
		userID, err := uuid.Parse(claims["sub"].(string))
		if err != nil {
			return nil, err
		}

		return s.userRepo.FindUserByID(userID)
	}

	return nil, errors.New("invalid token")
}