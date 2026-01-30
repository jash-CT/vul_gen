package models

import (
	"time"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

type User struct {
	gorm.Model
	ID             uuid.UUID `gorm:"type:uuid;primary_key"`
	Email          string    `gorm:"uniqueIndex;not null"`
	PasswordHash   string    `gorm:"not null"`
	TenantID       uuid.UUID `gorm:"index"`
	Tenant         Tenant    `gorm:"foreignKey:TenantID"`
	Roles          []Role    `gorm:"many2many:user_roles"`
	LastLogin      time.Time
	ProviderType   string
	ProviderUserID string
	Status         UserStatus
}

type Tenant struct {
	gorm.Model
	ID             uuid.UUID `gorm:"type:uuid;primary_key"`
	Name           string    `gorm:"not null"`
	Domain         string    `gorm:"uniqueIndex"`
	Status         TenantStatus
	SubscriptionTier string
}

type Role struct {
	gorm.Model
	ID          uuid.UUID `gorm:"type:uuid;primary_key"`
	Name        string    `gorm:"uniqueIndex"`
	Description string
	Permissions []Permission `gorm:"many2many:role_permissions"`
}

type Permission struct {
	gorm.Model
	ID   uuid.UUID `gorm:"type:uuid;primary_key"`
	Code string    `gorm:"uniqueIndex"`
	Name string
}

type UserStatus string
const (
	UserActive    UserStatus = "ACTIVE"
	UserSuspended UserStatus = "SUSPENDED"
	UserInactive  UserStatus = "INACTIVE"
)

type TenantStatus string
const (
	TenantActive    TenantStatus = "ACTIVE"
	TenantSuspended TenantStatus = "SUSPENDED"
	TenantProvisioning TenantStatus = "PROVISIONING"
)